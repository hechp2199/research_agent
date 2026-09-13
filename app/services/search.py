import asyncio

from app.schemas.paper import Paper
from app.services.literature.europe_pmc import search_europe_pmc
from app.services.literature.pubmed import fetch_pubmed_details, search_pubmed
from app.utils.search_query import combine_search_queries


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

    print("Number of papers: "+ str(len(papers)))
    return papers, source_status
