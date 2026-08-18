from fastapi import APIRouter

from app.schemas.research import ResearchRequest, ResearchResult
from app.services.research import search_literature

router = APIRouter(
    prefix="/research",
    tags=["Research"],
)


@router.post("/search", response_model=ResearchResult)
async def research(request: ResearchRequest):
    return await search_literature(request.query, request.limit, request.top_k)
