from pydantic import BaseModel, Field

from app.schemas.paper import Paper


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=10, ge=1, le=100)
    top_k: int = Field(default=5, ge=1, le=20)


class ResearchResult(BaseModel):
    papers: list[Paper]
    sources: dict[str, str]
    summary: str


class ResearchPlan(BaseModel):
    search_queries: list[str] = Field(
        min_length=1, description="Search queries to use for literature retrieval"
    )
    sources: list[str] = Field(min_length=1, description="Literature sources to search")
    reasoning: str = Field(
        min_length=1, description="Brief explanation of the research strategy"
    )


class EvidenceAssessment(BaseModel):
    sufficient: bool
    reasoning: str
    missing_aspects: list[str]


class SearchRefinement(BaseModel):
    search_queries: list[str]
    reasoning: str
