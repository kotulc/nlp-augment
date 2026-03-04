"""Deterministic relevance helpers kept for legacy demo compatibility."""


def _normalize(text: str) -> str:
    """Normalize text for simple token-based scoring."""
    return text.lower().strip(".,!?;:()[]{}\"'")


def _tokenize(text: str) -> list[str]:
    """Split content into normalized non-empty word tokens."""
    return [_normalize(token) for token in text.split() if _normalize(token)]


def _similarity_score(query_tokens: set[str], candidate: str) -> float:
    """Compute simple overlap score in a stable 0-1 range."""
    if not query_tokens:
        return 0.0

    candidate_tokens = set(_tokenize(candidate))
    overlap = len(query_tokens & candidate_tokens)
    return round((overlap + 1) / (len(query_tokens) + 1), 3)


def _acceptability_score(candidate: str) -> float:
    """Estimate readability with a bounded length-based heuristic."""
    token_count = len(_tokenize(candidate))
    if token_count == 0:
        return 0.0

    if token_count <= 3:
        return 0.7
    if token_count <= 8:
        return 0.9
    if token_count <= 14:
        return 0.8
    return 0.65


def composite_scores(content: str, candidates: list[str]) -> tuple[list[str], list[float]]:
    """Rank candidates by overlap similarity multiplied by acceptability."""
    query_tokens = set(_tokenize(content))
    deduped_candidates = list(dict.fromkeys(candidates))
    scored = []
    for candidate in deduped_candidates:
        similarity = _similarity_score(query_tokens, candidate)
        composite = round(similarity * _acceptability_score(candidate), 3)
        scored.append((candidate, composite))

    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return [candidate for candidate, _ in ranked], [score for _, score in ranked]


def maximal_marginal_relevance(
    content: str,
    candidates: list[str],
    sim_lambda: float = 0.5,
    top_n: int = 10,
) -> tuple[list[str], list[float]]:
    """Select diverse candidates balancing relevance and novelty."""
    if top_n <= 0 or not candidates:
        return [], []

    query_tokens = set(_tokenize(content))
    unique_candidates = list(dict.fromkeys(candidates))
    remaining = list(unique_candidates)
    selected: list[str] = []
    selected_scores: list[float] = []

    while remaining and len(selected) < top_n:
        best_candidate = None
        best_score = -1.0
        for candidate in remaining:
            relevance = _similarity_score(query_tokens, candidate)
            if not selected:
                mmr_score = relevance
            else:
                candidate_tokens = set(_tokenize(candidate))
                max_overlap = 0.0
                for chosen in selected:
                    chosen_tokens = set(_tokenize(chosen))
                    union_count = len(candidate_tokens | chosen_tokens) or 1
                    overlap = len(candidate_tokens & chosen_tokens) / union_count
                    max_overlap = max(max_overlap, overlap)

                mmr_score = (sim_lambda * relevance) - ((1 - sim_lambda) * max_overlap)

            if mmr_score > best_score:
                best_candidate = candidate
                best_score = mmr_score

        if best_candidate is None:
            break

        selected.append(best_candidate)
        selected_scores.append(round(best_score, 3))
        remaining.remove(best_candidate)

    return selected, selected_scores


def semantic_similarity(content: str, candidates: list[str]) -> tuple[list[str], list[float]]:
    """Rank candidates by token-overlap similarity with input content."""
    query_tokens = set(_tokenize(content))
    scored = [(candidate, _similarity_score(query_tokens, candidate)) for candidate in candidates]
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return [candidate for candidate, _ in ranked], [score for _, score in ranked]
