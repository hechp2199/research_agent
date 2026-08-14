from fastapi import APIRouter, HTTPException, Query

from app.schemas.paper import Paper
from app.services.europe_pmc import search_europe_pmc

router = APIRouter(
    prefix="/europe-pmc",
    tags=["Europe PMC"],
)


@router.get("/search", response_model=list[Paper])
async def search(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
):
    """Function to fetch the relevant papers for the user query from EuropePMC source

    Args:
        query (str, optional): User's research query. Defaults to Query(..., min_length=1).
        limit (int, optional): Number of papers to retrieve. Defaults to Query(10, ge=1, le=100).

    Raises:
        HTTPException: Error during external API access

    Returns:
        _type_: List of papers relevant for the query
    """
    try:
        papers = await search_europe_pmc(query, limit)

        return papers

    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail="Europe PMC service unavailable",
        ) from e
