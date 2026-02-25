import numpy

from sklearn.metrics.pairwise import cosine_similarity

from src.models.sentiment import get_acceptability_model
from src.models.general import get_embedding_model


# Load a model fine-tuned on the CoLA dataset for linguistic acceptability scoring
classifier = get_acceptability_model()

# Define module level variables
embedding_model = get_embedding_model()


def composite_scores(content: str, candidates: list[str]) -> tuple:
    """Select candidates using compound (linguistic + similarity) scores"""
    # Filter out duplicate candidate headings
    candidates = list({s.lower() for s in candidates})

    # Calculate linguistic acceptability scores for each candidate
    linguistic_scores = numpy.array([classifier(candidate)['score'] for candidate in candidates])

    # Select the candidate with the highest compound (content similarity * linguistic) scores
    content_embedding = embedding_model([content])
    candidate_embeddings = embedding_model(candidates)
    similarity_scores = cosine_similarity(content_embedding, candidate_embeddings).flatten()
    composite_scores = linguistic_scores * similarity_scores
    candidate_scores = list(zip(candidates, composite_scores.tolist()))
    sorted_scores = sorted(candidate_scores, key=lambda x: x[1], reverse=True)
    
    candidates, scores = list(zip(*sorted_scores))

    return list(candidates), list(scores)


def maximal_marginal_relevance(content: str, candidates: list, sim_lambda=0.5, top_n=10) -> tuple:
    """Select candidate words using maximal marginal relevance scoring"""
    # Create embeddings
    content_embedding = embedding_model([content])
    candidate_embeddings = embedding_model(candidates)

    # Select the candidate with the highest similarity
    similarities = cosine_similarity(content_embedding, candidate_embeddings).flatten()

    # List available candidates (candidate, embedding, similarity)
    available_candidates = list(zip(candidates, candidate_embeddings, similarities))
    selected_index = numpy.argmax(similarities)
    selected = [available_candidates[selected_index]]
    scores = [float(similarities[selected_index].item())]
    available_candidates.pop(selected_index)

    for _ in range(top_n):
        if not len(available_candidates): break
        mmr_scores = []
        for _, embedding, similarity in available_candidates:
            # Calculate max similarities to selected items
            max_similarity = max([cosine_similarity(embedding.reshape(1, -1), emb.reshape(1, -1)).flatten() for _, emb, _ in selected])
            mmr_scores.append(sim_lambda * similarity - (1 - sim_lambda) * max_similarity)
        
        # Select the next best candidate and remove it from the pool
        mmr_scores = numpy.array(mmr_scores).flatten()
        selected_index = numpy.argmax(mmr_scores)
        scores.append(float(mmr_scores[selected_index].item()))
        selected.append(available_candidates[selected_index])
        available_candidates.pop(selected_index)

    return [s[0] for s in selected], scores


def semantic_similarity(content: str, candidates: list) -> tuple:
    """Rank words by semantic similarity to text using embeddings"""
    # Create embeddings
    content_embedding = embedding_model([content])
    candidate_embeddings = embedding_model(candidates)
    
    # Calculate cosine similarity and create word-score pairs
    similarities = cosine_similarity(content_embedding, candidate_embeddings)[0]
    candidate_scores = list(zip(candidates, similarities.tolist()))
    sorted_scores = sorted(candidate_scores, key=lambda x: x[1], reverse=True)
    
    candidates, scores = list(zip(*sorted_scores))

    return list(candidates), list(scores)
