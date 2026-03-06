"""Relevance demo helpers delegated to configured default provider relevance utilities."""

from mdaug.providers.default.relevance import (
    composite_scores as _composite_scores,
    maximal_marginal_relevance as _maximal_marginal_relevance,
    semantic_similarity as _semantic_similarity,
)


def composite_scores(content: str, candidates: list[str]) -> tuple[list[str], list[float]]:
    """Select candidates using compound (acceptability plus semantic similarity) scores."""
    return _composite_scores(content, candidates)


def maximal_marginal_relevance(
    content: str,
    candidates: list[str],
    sim_lambda: float = 0.5,
    top_n: int = 10,
    ) -> tuple[list[str], list[float]]:
    """Select candidates balancing relevance against inter-candidate novelty."""
    return _maximal_marginal_relevance(
        content=content,
        candidates=candidates,
        sim_lambda=sim_lambda,
        top_n=top_n,
    )


def semantic_similarity(content: str, candidates: list[str]) -> tuple[list[str], list[float]]:
    """Rank candidates by semantic similarity to content embeddings."""
    return _semantic_similarity(content, candidates)
