from fastapi import APIRouter, HTTPException

from app.schemas.research import ResearchRequest, ResearchResult
from app.services.research import search_literature
from app.services.research_graph import run_research_graph

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


@router.post("/graph_search", response_model=ResearchResult)
async def research_graph(request: ResearchRequest):

    try:
        return await run_research_graph(request.query, request.limit, request.top_k)

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
