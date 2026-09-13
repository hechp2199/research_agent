from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.schemas.paper import Paper


def calculate_tfidf_scores(
    query: str,
    papers: list[Paper],
) -> list[float]:
    """Calculate weighted TF-IDF cosine similarity using title and abstract."""

    if not papers:
        return []

    titles = [paper.title or "" for paper in papers]

    abstracts = [paper.abstract or "" for paper in papers]

    # -------------------------
    # Title TF-IDF
    # -------------------------

    title_vectorizer = TfidfVectorizer()

    title_vectors = title_vectorizer.fit_transform(titles)

    title_query_vector = title_vectorizer.transform([query])

    title_similarities = cosine_similarity(
        title_query_vector,
        title_vectors,
    )[0]

    # -------------------------
    # Abstract TF-IDF
    # -------------------------

    abstract_vectorizer = TfidfVectorizer()

    abstract_vectors = abstract_vectorizer.fit_transform(abstracts)

    abstract_query_vector = abstract_vectorizer.transform([query])

    abstract_similarities = cosine_similarity(
        abstract_query_vector,
        abstract_vectors,
    )[0]

    # -------------------------
    # Weighted score
    # -------------------------

    weighted_scores = 0.7 * title_similarities + 0.3 * abstract_similarities

    return weighted_scores.tolist()


def rank_papers(
    query: str,
    papers: list[Paper],
) -> list[Paper]:
    """Rank papers using weighted TF-IDF and cosine similarity."""

    if not papers:
        return []

    similarities = calculate_tfidf_scores(
        query,
        papers,
    )

    scored_papers = list(zip(similarities, papers))

    scored_papers.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [paper for _, paper in scored_papers]
