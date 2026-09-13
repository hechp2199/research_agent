import uuid

from langgraph.graph import StateGraph, START, END

from app.schemas.research import ResearchResult, ResearchState
from app.services.planner import generate_research_plan
from app.services.search import search_sources
from app.utils.deduplication import deduplicate_papers
from app.utils.ranking.hybrid_relevance import rank_papers
from app.services.evidence import assess_evidence
from app.services.refinement import generate_refinement_queries
from app.services.summarizer import generate_research_summary
from app.utils.logger import get_logger

logger = get_logger(__name__)
MAX_SEARCH_ITERATIONS = 2


async def plan_node(state: ResearchState) -> dict:
    logger.info(
        "[%s] Planning research: %s",
        state.research_id,
        state.query,
    )
    plan = await generate_research_plan(state.query)
    logger.info(
        "[%s] Plan generated: %d queries, sources=%s",
        state.research_id,
        len(plan.search_queries),
        plan.sources,
    )

    return {
        "plan": plan,
    }


async def search_node(state: ResearchState) -> dict:

    queries = (
        state.refinement_queries
        if state.refinement_queries
        else state.plan.search_queries
    )

    logger.info(
        "[%s] Starting search iteration %d: queries=%s",
        state.research_id,
        state.iteration + 1,
        queries,
    )

    new_papers, source_status = await search_sources(
        queries,
        state.plan.sources,
        state.limit,
    )

    logger.info(
        "[%s] Search completed: retrieved=%d papers | source_status=%s",
        state.research_id,
        len(new_papers),
        source_status,
    )

    return {
        "papers": state.papers + new_papers,
        "source_status": source_status,
        "refinement_queries": [],
        "iteration": state.iteration + 1,
    }


def prepare_evidence_node(state: ResearchState) -> dict:

    logger.info(
        "[%s] Preparing evidence: input_papers=%d",
        state.research_id,
        len(state.papers),
    )
    papers = deduplicate_papers(state.papers)

    logger.info(
        "[%s] Deduplication completed: remaining=%d papers",
        state.research_id,
        len(papers),
    )

    papers = rank_papers(state.query, papers)

    logger.info(
        "[%s] Ranking completed",
        state.research_id,
    )

    return {
        "papers": papers,
    }


async def assess_evidence_node(state: ResearchState) -> dict:

    logger.info(
        "[%s] Assessing evidence using top_k=%d",
        state.research_id,
        state.top_k,
    )
    assessment = await assess_evidence(
        state.query,
        state.papers[: state.top_k],
    )
    logger.info(
        "[%s] Evidence assessment: sufficient=%s, missing_aspects=%d",
        state.research_id,
        assessment.sufficient,
        len(assessment.missing_aspects),
    )

    return {
        "evidence_assessment": assessment,
    }


def route_after_assessment(state: ResearchState) -> str:
    if state.evidence_assessment.sufficient:
        logger.info(
            "[%s] Evidence sufficient -> synthesize",
            state.research_id,
        )
        return "synthesize"

    if state.iteration >= MAX_SEARCH_ITERATIONS:
        logger.info(
            "[%s] Maximum search iterations reached (%d) -> synthesize",
            state.research_id,
            MAX_SEARCH_ITERATIONS,
        )
        return "synthesize"

    logger.info(
        "[%s] Evidence insufficient -> refine",
        state.research_id,
    )

    return "refine"


async def refine_node(state: ResearchState) -> dict:

    logger.info(
        "[%s] Generating refinement queries",
        state.research_id,
    )
    refinement = await generate_refinement_queries(
        state.query,
        state.evidence_assessment.missing_aspects,
    )
    logger.info(
        "[%s] Refinement generated: queries=%s",
        state.research_id,
        refinement.search_queries,
    )

    return {
        "refinement_queries": refinement.search_queries,
    }


async def synthesize_node(state: ResearchState) -> dict:
    final_papers = state.papers[: state.top_k]

    logger.info(
        "[%s] Synthesizing final answer using %d papers",
        state.research_id,
        len(final_papers),
    )
    summary = await generate_research_summary(
        state.query,
        final_papers,
    )
    logger.info(
        "[%s] Synthesis completed",
        state.research_id,
    )

    return {
        "final_papers": final_papers,
        "summary": summary,
    }


# Building the graph
builder = StateGraph(ResearchState)

builder.add_node("plan", plan_node)
builder.add_node("search", search_node)
builder.add_node("prepare_evidence", prepare_evidence_node)
builder.add_node("assess_evidence", assess_evidence_node)
builder.add_node("refine", refine_node)
builder.add_node("synthesize", synthesize_node)

builder.add_edge(START, "plan")
builder.add_edge("plan", "search")
builder.add_edge("search", "prepare_evidence")
builder.add_edge("prepare_evidence", "assess_evidence")
builder.add_conditional_edges(
    "assess_evidence",
    route_after_assessment,
    {
        "refine": "refine",
        "synthesize": "synthesize",
    },
)
builder.add_edge("refine", "search")
builder.add_edge("synthesize", END)

research_graph = builder.compile()


async def run_research_graph(
    query: str,
    limit: int = 10,
    top_k: int = 5,
) -> ResearchResult:
    research_id = str(uuid.uuid4())

    logger.info(
        "[%s] Research started: query=%s",
        research_id,
        query,
    )

    initial_state = ResearchState(
        query=query,
        limit=limit,
        top_k=top_k,
        research_id=research_id,
    )

    final_state = await research_graph.ainvoke(initial_state)

    logger.info(
        "[%s] Research completed",
        research_id,
    )

    return ResearchResult(
        papers=final_state["final_papers"],
        sources=final_state["source_status"],
        summary=final_state["summary"],
    )


async def main():
    research_id = str(uuid.uuid4())
    initial_state = ResearchState(
        query="lightweight deep learning for meniscus tear detection",
        limit=5,
        top_k=2,
        research_id=research_id,
    )

    logger.info(
        "[%s] Research started: query=%s",
        initial_state.research_id,
        initial_state.query,
    )
    result = await research_graph.ainvoke(initial_state)
    logger.info(
        "[%s] Research completed",
        research_id,
    )

    print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
