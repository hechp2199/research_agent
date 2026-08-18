from pydantic import BaseModel, Field


class Paper(BaseModel):
    pmid: str | None = None
    title: str | None = None
    abstract: str | None = None
    authors: list[str] = Field(default_factory=list)
    journal: str | None = None
    publication_date: str | None = None
    doi: str | None = None
    pmcid: str | None = None
    source: str