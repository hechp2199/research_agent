import asyncio
import xml.etree.ElementTree as ET
import httpx

from app.schemas.paper import Paper


async def search_pubmed(query: str, limit: int = 10) -> list[str]:
    """Function which searches and retrives the list of relevant paper PMIDs

    Args:
        query (str): User search query
        limit (int): Max number of paper IDs to retrieve. Defaults to 10.

    Returns:
        list[str]: List of PMIDs for the paper
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                params={
                    "db": "pubmed",
                    "term": query,
                    "retmode": "json",
                    "retmax": limit,
                },
            )

            response.raise_for_status()
        except httpx.HTTPError as e:
            raise RuntimeError("PubMed search failed") from e

        data = response.json()

        return data["esearchresult"]["idlist"]


async def fetch_pubmed_details(pmids: list[str]) -> list[Paper]:
    """Function to fetch the list of papers using the PMIDs and
    parsing the search results to Paper model

    Args:
        pmids (list[str]): List of PMIDs

    Returns:
        list[Paper]: List of papers parsed from the search result
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
                params={"db": "pubmed", "id": ",".join(pmids)},
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise RuntimeError("PubMed fetch failed") from e

        root = ET.fromstring(response.text)

        articles = root.findall(".//PubmedArticle")
        papers = []

        for article in articles:
            pmid = article.findtext(".//PMID")
            title = article.findtext(".//ArticleTitle")

            # Abstract
            abstract_parts = article.findall(".//AbstractText")
            abstract = " ".join(element.text or "" for element in abstract_parts)

            # Authors
            authors = []
            for author in article.findall(".//Author"):
                last_name = author.findtext("LastName")
                fore_name = author.findtext("ForeName")

                if last_name and fore_name:
                    authors.append(f"{fore_name} {last_name}")
                elif last_name:
                    authors.append(last_name)

            # Journal
            journal = article.findtext(".//Journal/Title")

            # Publication date
            publication_date = None

            date = article.find(".//ArticleDate[@DateType='Electronic']")

            if date is not None:
                year = date.findtext("Year")
                month = date.findtext("Month")
                day = date.findtext("Day")

                if year and month and day:
                    publication_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            # DOI and PMCID
            doi = None
            pmcid = None

            for article_id in article.findall(".//ArticleId"):
                id_type = article_id.get("IdType")

                if id_type == "doi":
                    doi = article_id.text
                elif id_type == "pmc":
                    pmcid = article_id.text

            paper = Paper(
                pmid=pmid,
                title=title,
                abstract=abstract,
                authors=authors,
                journal=journal,
                publication_date=publication_date,
                doi=doi,
                pmcid=pmcid,
                source="PubMed",
            )

            papers.append(paper)
        return papers


async def main():
    pmids = await search_pubmed("Deep learning for knee abnormality", limit=3)

    print("Found PMIDs:", pmids)

    papers = await fetch_pubmed_details(pmids)
    for paper in papers:
        print(paper)
        print()


if __name__ == "__main__":
    asyncio.run(main())
