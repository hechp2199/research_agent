import asyncio
import uuid

from app.schemas.paper import Paper
from app.schemas.research import ResearchResult, ResearchState
from app.services.pubmed import search_pubmed, fetch_pubmed_details
from app.services.europe_pmc import search_europe_pmc
from app.services.evidence import assess_evidence
from app.services.planner import generate_research_plan
from app.services.refinement import generate_refinement_queries
from app.services.summarizer import generate_research_summary
from app.utils.deduplication import deduplicate_papers
from app.utils.logger import get_logger
from app.utils.relevance import rank_papers
from app.utils.search_query import combine_search_queries

MAX_SEARCH_ITERATIONS = 2
logger = get_logger(__name__)


async def search_pubmed_papers(query: str, limit: int) -> list[Paper]:
    pmids = await search_pubmed(query, limit)

    if not pmids:
        return []

    return await fetch_pubmed_details(pmids)


async def search_sources(
    queries: list[str],
    sources: list[str],
    limit: int,
) -> tuple[list[Paper], dict[str, str]]:

    combined_query = combine_search_queries(queries)

    tasks = []

    if "pubmed" in sources:
        tasks.append(asyncio.create_task(search_pubmed_papers(combined_query, limit)))

    if "europe_pmc" in sources:
        tasks.append(asyncio.create_task(search_europe_pmc(combined_query, limit)))

    if not tasks:
        raise RuntimeError("No valid literature sources selected")

    results = await asyncio.gather(
        *tasks,
        return_exceptions=True,
    )

    papers = []
    source_status = {}

    result_index = 0

    if "pubmed" in sources:
        result = results[result_index]
        result_index += 1

        if isinstance(result, Exception):
            source_status["PubMed"] = "failed"
        else:
            source_status["PubMed"] = "success"
            papers.extend(result)

    if "europe_pmc" in sources:
        result = results[result_index]

        if isinstance(result, Exception):
            source_status["Europe PMC"] = "failed"
        else:
            source_status["Europe PMC"] = "success"
            papers.extend(result)

    return papers, source_status


async def search_literature(
    query: str,
    limit: int = 10,
    top_k: int = 5,
) -> ResearchResult:

    research_id = str(uuid.uuid4())
    logger.info("[%s] Research started | query=%s", research_id, query)
    state = ResearchState(query=query)

    # 1. Create initial research plan
    logger.info("[%s] Generating research plan", research_id)
    state.plan = await generate_research_plan(state.query)
    logger.info(
        "[%s] Research plan generated | queries=%d | sources=%s",
        research_id,
        len(state.plan.search_queries),
        state.plan.sources,
    )

    # 2. Initial search
    logger.info(
        "[%s] Starting initial literature search | sources=%s | limit=%d",
        research_id,
        state.plan.sources,
        limit,
    )
    state.papers, state.source_status = await search_sources(
        state.plan.search_queries,
        state.plan.sources,
        limit,
    )
    logger.info(
        "[%s] Initial search completed | papers=%d | source_status=%s",
        research_id,
        len(state.papers),
        state.source_status,
    )

    if not state.papers:
        raise RuntimeError("No papers could be retrieved from any source")

    # 3. Iterative evidence gathering
    for iteration in range(MAX_SEARCH_ITERATIONS):

        state.iteration = iteration
        logger.info(
            "[%s] Research iteration %d/%d",
            research_id,
            iteration + 1,
            MAX_SEARCH_ITERATIONS,
        )

        papers_before_dedup = len(state.papers)

        # Deduplicate and rank current evidence
        state.papers = deduplicate_papers(state.papers)

        logger.info(
            "[%s] Deduplication completed | papers=%d -> %d",
            research_id,
            papers_before_dedup,
            len(state.papers),
        )

        state.papers = rank_papers(state.query, state.papers)

        logger.info(
            "[%s] Relevance ranking completed | candidates=%d | top_k=%d",
            research_id,
            len(state.papers),
            top_k,
        )

        # Assess current evidence
        logger.info(
            "[%s] Assessing evidence sufficiency | papers_evaluated=%d",
            research_id,
            min(len(state.papers), top_k),
        )
        state.evidence_assessment = await assess_evidence(
            state.query,
            state.papers[:top_k],
        )
        logger.info(
            "[%s] Evidence assessment completed | sufficient=%s | missing_aspects=%d | reasoning=%s",
            research_id,
            state.evidence_assessment.sufficient,
            len(state.evidence_assessment.missing_aspects),
            state.evidence_assessment.reasoning,
        )

        # Stop if evidence is sufficient
        if state.evidence_assessment.sufficient:
            logger.info(
                "[%s] Evidence sufficient | stopping refinement",
                research_id,
            )
            break

        # No useful missing aspects → cannot refine
        if not state.evidence_assessment.missing_aspects:
            logger.info(
                "[%s] Evidence insufficient but no missing aspects identified | stopping",
                research_id,
            )
            break

        # Don't refine after the final iteration
        if iteration == MAX_SEARCH_ITERATIONS - 1:
            logger.info(
                "[%s] Maximum search iterations reached | stopping refinement",
                research_id,
            )
            break

        # Generate targeted refinement queries
        logger.info(
            "[%s] Generating refinement queries | missing_aspects=%d",
            research_id,
            len(state.evidence_assessment.missing_aspects),
        )
        refinement = await generate_refinement_queries(
            state.query,
            state.evidence_assessment.missing_aspects,
        )
        logger.info(
            "[%s] Refinement queries generated | queries=%d",
            research_id,
            len(refinement.search_queries),
        )

        if not refinement.search_queries:
            break

        # Store refinement queries in state
        state.refinement_queries = refinement.search_queries

        # Search for additional evidence
        logger.info(
            "[%s] Starting refinement search | iteration=%d",
            research_id,
            iteration + 1,
        )
        refinement_papers, refinement_sources = await search_sources(
            state.refinement_queries,
            state.plan.sources,
            limit,
        )
        logger.info(
            "[%s] Refinement search completed | papers=%d | source_status=%s",
            research_id,
            len(refinement_papers),
            refinement_sources,
        )

        if not refinement_papers:
            break

        # Add new evidence to existing collection
        state.papers.extend(refinement_papers)
        logger.info(
            "[%s] Refinement papers added | total_papers=%d",
            research_id,
            len(state.papers),
        )

        # Update source status
        for source, status in refinement_sources.items():

            if source not in state.source_status:
                state.source_status[source] = status

            elif status == "success":
                state.source_status[source] = "success"

    # 4. Final deduplication and ranking
    logger.info(
        "[%s] Finalizing research results",
        research_id,
    )
    state.papers = deduplicate_papers(state.papers)
    state.papers = rank_papers(state.query, state.papers)

    # 5. Final evidence set
    state.final_papers = state.papers[:top_k]
    logger.info(
        "[%s] Final evidence set selected | papers=%d",
        research_id,
        len(state.final_papers),
    )

    # 6. Final synthesis
    logger.info(
        "[%s] Generating final research summary",
        research_id,
    )
    state.summary = await generate_research_summary(
        state.query,
        state.final_papers,
    )
    logger.info(
        "[%s] Research completed successfully | final_papers=%d",
        research_id,
        len(state.final_papers),
    )

    return ResearchResult(
        papers=state.final_papers,
        sources=state.source_status,
        summary=state.summary,
    )
