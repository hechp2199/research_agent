import asyncio

from app.schemas.paper import Paper
from app.schemas.research import ResearchResult
from app.services.pubmed import search_pubmed, fetch_pubmed_details
from app.services.europe_pmc import search_europe_pmc
from app.services.evidence import assess_evidence
from app.services.planner import generate_research_plan
from app.services.refinement import generate_refinement_queries
from app.services.summarizer import generate_research_summary
from app.utils.deduplication import deduplicate_papers
from app.utils.relevance import rank_papers
from app.utils.search_query import combine_search_queries

MAX_SEARCH_ITERATIONS = 2


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

    # 1. Create initial research plan
    plan = await generate_research_plan(query)

    # 2. Initial search
    papers, sources = await search_sources(
        plan.search_queries,
        plan.sources,
        limit,
    )

    if not papers:
        raise RuntimeError("No papers could be retrieved from any source")

    # 3. Iterative evidence gathering
    for iteration in range(MAX_SEARCH_ITERATIONS):

        # Deduplicate and rank current evidence
        papers = deduplicate_papers(papers)
        papers = rank_papers(query, papers)

        # Assess current evidence
        assessment = await assess_evidence(
            query,
            papers[:top_k],
        )

        # Stop if evidence is sufficient
        if assessment.sufficient:
            break

        # No useful missing aspects → cannot refine
        if not assessment.missing_aspects:
            break

        # Don't refine after the final iteration
        if iteration == MAX_SEARCH_ITERATIONS - 1:
            break

        # Generate targeted refinement queries
        refinement = await generate_refinement_queries(
            query,
            assessment.missing_aspects,
        )

        if not refinement.search_queries:
            break

        # Search for additional evidence
        refinement_papers, refinement_sources = await search_sources(
            refinement.search_queries,
            plan.sources,
            limit,
        )

        if not refinement_papers:
            break

        # Add new evidence to existing collection
        papers.extend(refinement_papers)

        # Update source status
        for source, status in refinement_sources.items():

            if source not in sources:
                sources[source] = status

            elif status == "success":
                sources[source] = "success"

    # 4. Final deduplication and ranking
    papers = deduplicate_papers(papers)
    papers = rank_papers(query, papers)

    # 5. Final evidence set
    papers = papers[:top_k]

    # 6. Final synthesis
    summary = await generate_research_summary(
        query,
        papers,
    )

    return ResearchResult(
        papers=papers,
        sources=sources,
        summary=summary,
    )
