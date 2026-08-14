from fastapi import APIRouter, HTTPException, Query

from app.services.pubmed import search_pubmed, fetch_pubmed_details
from app.schemas.paper import Paper

router = APIRouter(
    prefix="/pubmed",
    tags=["PubMed"],
)


@router.get("/search", response_model=list[Paper])
async def search(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
):
    """Function to fetch the relevant papers for the user query from PubMed source

    Args:
        query (str, optional): User's research query. Defaults to Query(..., min_length=1).
        limit (int, optional): Number of papers to retrieve. Defaults to Query(10, ge=1, le=100).

    Raises:
        HTTPException: Error during external API access

    Returns:
        _type_: List of papers relevant for the query
    """
    try:
        pmids = await search_pubmed(query, limit)

        if not pmids:
            return []

        papers = await fetch_pubmed_details(pmids)

        return papers
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )
