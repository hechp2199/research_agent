import re

from app.schemas.paper import Paper


def normalize_text(text: str) -> set[str]:
    """Convert text into a set of normalized words."""
    return set(re.findall(r"\b[a-z0-9]+\b", text.lower()))


def calculate_relevance_score(
    query: str,
    paper: Paper,
) -> float:
    """Calculate a simple keyword-based relevance score."""

    query_terms = normalize_text(query)

    if not query_terms:
        return 0.0

    title_terms = normalize_text(paper.title or "")
    abstract_terms = normalize_text(paper.abstract or "")

    title_matches = query_terms & title_terms
    abstract_matches = query_terms & abstract_terms

    title_score = len(title_matches) / len(query_terms)
    abstract_score = len(abstract_matches) / len(query_terms)

    return (title_score * 0.7) + (abstract_score * 0.3)


def rank_papers(
    query: str,
    papers: list[Paper],
) -> list[Paper]:
    """Rank papers by relevance to the query."""

    scored_papers = [
        (
            calculate_relevance_score(query, paper),
            paper,
        )
        for paper in papers
    ]

    scored_papers.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [paper for _, paper in scored_papers]
