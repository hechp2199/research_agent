from fastapi import APIRouter, HTTPException

from app.schemas.research import ResearchRequest, ResearchResult
from app.services.research import search_literature

router = APIRouter(
    prefix="/research",
    tags=["Research"],
)


@router.post("/search", response_model=ResearchResult)
async def research(request: ResearchRequest):

    try:
        return await search_literature(request.query, request.limit, request.top_k)

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
