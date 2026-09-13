from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.schemas.paper import Paper

model = SentenceTransformer("NeuML/pubmedbert-base-embeddings")


def calculate_embedding_scores(
    query: str,
    papers: list[Paper],
) -> list[float]:
    """Calculate semantic similarity between query and papers."""

    if not papers:
        return []

    # Encode query once
    query_embedding = model.encode([query])

    # Collect paper text
    titles = [paper.title or "" for paper in papers]
    abstracts = [paper.abstract or "" for paper in papers]

    # Encode all titles and abstracts in batches
    title_embeddings = model.encode(titles)
    abstract_embeddings = model.encode(abstracts)

    # Calculate cosine similarity
    title_scores = cosine_similarity(
        query_embedding,
        title_embeddings,
    )[0]

    abstract_scores = cosine_similarity(
        query_embedding,
        abstract_embeddings,
    )[0]

    # 70% title + 30% abstract
    weighted_scores = 0.7 * title_scores + 0.3 * abstract_scores

    return weighted_scores.tolist()


def rank_papers(
    query: str,
    papers: list[Paper],
) -> list[Paper]:
    """Rank papers using embedding similarity."""

    if not papers:
        return []

    scores = calculate_embedding_scores(
        query,
        papers,
    )

    scored_papers = list(zip(scores, papers))

    scored_papers.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [paper for _, paper in scored_papers]
