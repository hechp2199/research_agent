def combine_search_queries(queries: list[str]) -> str:
    return " OR ".join(
        f"({query})"
        for query in queries
    )