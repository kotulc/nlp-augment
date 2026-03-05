"""Relevance utilities for default providers."""

from math import sqrt

from mdaug.providers.default.models import get_acceptability_model, get_embedding_model


def _cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not vector_a or not vector_b or len(vector_a) != len(vector_b):
        return 0.0

    dot_product = sum(value_a * value_b for value_a, value_b in zip(vector_a, vector_b))
    norm_a = sqrt(sum(value * value for value in vector_a))
    norm_b = sqrt(sum(value * value for value in vector_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def _to_vectors(encoded_items) -> list[list[float]]:
    """Convert embedding outputs to plain python float vectors."""
    return [[float(value) for value in row] for row in encoded_items]


def _pairwise_similarity(vectors: list[list[float]]) -> list[list[float]]:
    """Compute a full pairwise cosine similarity matrix."""
    matrix = []
    for row_vector in vectors:
        row = []
        for col_vector in vectors:
            row.append(_cosine_similarity(row_vector, col_vector))
        matrix.append(row)

    return matrix


def composite_scores(content: str, candidates: list[str]) -> tuple[list[str], list[float]]:
    """Score candidates by similarity times linguistic acceptability."""
    deduped_candidates = list(dict.fromkeys(candidate.strip().lower() for candidate in candidates if candidate))
    if not deduped_candidates:
        return [], []

    candidate_list, semantic_scores = semantic_similarity(content, deduped_candidates)
    acceptability_model = get_acceptability_model()
    combined = []
    for candidate, semantic_score in zip(candidate_list, semantic_scores):
        acceptability = float(acceptability_model(candidate)["score"])
        combined.append((candidate, round(acceptability * semantic_score, 4)))

    ranked = sorted(combined, key=lambda item: item[1], reverse=True)
    return [candidate for candidate, _score in ranked], [score for _candidate, score in ranked]


def maximal_marginal_relevance(
    content: str,
    candidates: list[str],
    sim_lambda: float = 0.5,
    top_n: int = 10,
) -> tuple[list[str], list[float]]:
    """Select candidates balancing query relevance and inter-candidate diversity."""
    deduped_candidates = list(dict.fromkeys(candidate for candidate in candidates if candidate))
    if not deduped_candidates or top_n <= 0:
        return [], []

    encode = get_embedding_model()
    content_vector = _to_vectors(encode([content]))[0]
    candidate_vectors = _to_vectors(encode(deduped_candidates))
    relevance_scores = [_cosine_similarity(content_vector, vector) for vector in candidate_vectors]
    novelty_matrix = _pairwise_similarity(candidate_vectors)

    available_indices = list(range(len(deduped_candidates)))
    selected_indices = []
    selected_scores = []

    while available_indices and len(selected_indices) < top_n:
        best_index = None
        best_score = None
        for index in available_indices:
            relevance = relevance_scores[index]
            if not selected_indices:
                mmr_score = relevance
            else:
                max_novelty_penalty = max(novelty_matrix[index][selected] for selected in selected_indices)
                mmr_score = (sim_lambda * relevance) - ((1 - sim_lambda) * max_novelty_penalty)

            if best_score is None or mmr_score > best_score:
                best_score = mmr_score
                best_index = index

        if best_index is None or best_score is None:
            break

        selected_indices.append(best_index)
        selected_scores.append(round(float(best_score), 4))
        available_indices.remove(best_index)

    return (
        [deduped_candidates[index] for index in selected_indices],
        selected_scores,
    )


def semantic_similarity(content: str, candidates: list[str]) -> tuple[list[str], list[float]]:
    """Rank candidates by semantic similarity to content embeddings."""
    deduped_candidates = list(dict.fromkeys(candidate for candidate in candidates if candidate))
    if not deduped_candidates:
        return [], []

    encode = get_embedding_model()
    embeddings = _to_vectors(encode([content] + deduped_candidates))
    content_vector = embeddings[0]
    candidate_vectors = embeddings[1:]
    paired_scores = []
    for candidate, vector in zip(deduped_candidates, candidate_vectors):
        paired_scores.append((candidate, round(_cosine_similarity(content_vector, vector), 4)))

    ranked = sorted(paired_scores, key=lambda item: item[1], reverse=True)
    return [candidate for candidate, _score in ranked], [score for _candidate, score in ranked]
