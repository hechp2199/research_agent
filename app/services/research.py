import asyncio

from app.schemas.paper import Paper
from app.schemas.research import ResearchResult
from app.services.pubmed import search_pubmed, fetch_pubmed_details
from app.services.europe_pmc import search_europe_pmc
from app.utils.deduplication import deduplicate_papers
from app.utils.relevance import rank_papers


async def search_pubmed_papers(query: str, limit: int) -> list[Paper]:
    pmids = await search_pubmed(query, limit)

    if not pmids:
        return []

    return await fetch_pubmed_details(pmids)


async def search_literature(
    query: str, limit: int = 10, top_k: int = 5
) -> ResearchResult:

    pubmed_task = asyncio.create_task(search_pubmed_papers(query, limit))

    europe_pmc_task = asyncio.create_task(search_europe_pmc(query, limit))

    results = await asyncio.gather(
        pubmed_task,
        europe_pmc_task,
        return_exceptions=True,
    )

    pubmed_result, europe_pmc_result = results

    papers = []
    sources = {}

    # PubMed
    if isinstance(pubmed_result, Exception):
        sources["PubMed"] = "failed"
    else:
        sources["PubMed"] = "success"
        papers.extend(pubmed_result)

    if not isinstance(europe_pmc_result, Exception):
        papers.extend(europe_pmc_result)

    # Europe PMC
    if isinstance(europe_pmc_result, Exception):
        sources["Europe PMC"] = "failed"
    else:
        sources["Europe PMC"] = "success"
        papers.extend(europe_pmc_result)

    papers = deduplicate_papers(papers)
    papers = rank_papers(query, papers)
    papers = papers[:top_k]

    return ResearchResult(papers=papers, sources=sources)
