import asyncio
import httpx

from app.schemas.paper import Paper


async def search_europe_pmc(
    query: str,
    limit: int = 10,
) -> list[Paper]:
    """Function to fetch the list of papers using the user query
    from Europe PMC andmapping the search results to Paper model

    Args:
        query (str): User search query
        limit (int, optional): Max number of papers to retrieve. Defaults to 10.

    Returns:
        list[Paper]: List of papers mapped from the search result
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                params={
                    "query": query,
                    "format": "json",
                    "pageSize": limit,
                    "resultType": "core",
                },
            )

            response.raise_for_status()
        except httpx.HTTPError as e:
            raise RuntimeError("Europe PMC search failed") from e

        data = response.json()

        papers = []

        for result in data["resultList"]["result"]:
            paper = Paper(
                pmid=result.get("pmid"),
                title=result.get("title"),
                abstract=result.get("abstractText"),
                authors=[
                    author.get("fullName")
                    for author in result.get("authorList", {}).get("author", [])
                    if author.get("fullName")
                ],
                journal=result.get("journalInfo").get("journal").get("title"),
                publication_date=result.get("firstPublicationDate"),
                doi=result.get("doi"),
                pmcid=result.get("id"),
                source="Europe PMC",
            )

            papers.append(paper)

        return papers


async def main():
    papers = await search_europe_pmc(
        "Deep learning for knee abnormality",
        limit=3,
    )

    for paper in papers:
        print(paper)
        print()


if __name__ == "__main__":
    asyncio.run(main())
