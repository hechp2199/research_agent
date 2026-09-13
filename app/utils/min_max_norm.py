def min_max_normalize(
    scores: list[float],
) -> list[float]:
    if not scores:
        return []

    minimum = min(scores)
    maximum = max(scores)

    if maximum == minimum:
        return [0.0] * len(scores)

    return [(score - minimum) / (maximum - minimum) for score in scores]
