from app.schemas.paper import Paper
from app.utils.min_max_norm import min_max_normalize
from app.utils.ranking.relevance import calculate_tfidf_scores
from app.utils.ranking.embedding_relevance import calculate_embedding_scores

EMBEDDING_WEIGHT = 0.7
TFIDF_WEIGHT = 0.3


def calculate_hybrid_scores(
    query: str,
    papers: list[Paper],
) -> list[float]:
    """Calculate hybrid relevance scores using
    embedding and TF-IDF similarity.
    """

    if not papers:
        return []

    tfidf_scores = calculate_tfidf_scores(
        query,
        papers,
    )
    normalized_tfidf = min_max_normalize(tfidf_scores)

    embedding_scores = calculate_embedding_scores(
        query,
        papers,
    )
    normalized_embedding = min_max_normalize(embedding_scores)

    hybrid_scores = [
        (EMBEDDING_WEIGHT * embedding_score + TFIDF_WEIGHT * tfidf_score)
        for embedding_score, tfidf_score in zip(normalized_embedding, normalized_tfidf)
    ]

    return hybrid_scores


def rank_papers(
    query: str,
    papers: list[Paper],
) -> list[Paper]:
    """Rank papers using hybrid semantic and keyword relevance."""

    if not papers:
        return []

    hybrid_scores = calculate_hybrid_scores(
        query,
        papers,
    )

    scored_papers = list(zip(hybrid_scores, papers))
    print_ranking("Ranking", hybrid_scores, papers)

    scored_papers.sort(
        key=lambda item: item[0],
        reverse=True,
    )


    return [paper for _, paper in scored_papers]


def print_ranking(
    title: str,
    scores: list[float],
    papers: list[Paper],
) -> None:
    """Print papers ranked by the supplied scores."""
    ranked = sorted(
        zip(scores, papers),
        key=lambda item: item[0],
        reverse=True,
    )
    print(f"\n========== {title} ==========")
    for rank, (score, paper) in enumerate(
        ranked,
        start=1,
    ):
        print(f"{rank}. " f"Score={score:.4f} | " f"{paper.title}")
