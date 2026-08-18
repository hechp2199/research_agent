from pydantic import BaseModel, Field

from app.schemas.paper import Paper


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=100)
    top_k: int = Field(default=5, ge=1, le=20)


class ResearchResult(BaseModel):
    papers: list[Paper]
    sources: dict[str, str]
