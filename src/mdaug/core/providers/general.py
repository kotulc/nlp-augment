import spacy

from functools import lru_cache

from sentence_transformers import SentenceTransformer
from transformers import pipeline


@lru_cache(maxsize=1)
def get_classifier_model():
    """Return the zero-shot classification pipeline or a mock function in debug mode"""
    pipe = pipeline(model='facebook/bart-large-mnli')

    def score_labels(content: str, candidate_labels: list, **kwargs) -> list:
        """Return the classification scores for the candidate labels"""
        result = pipe(content, candidate_labels=candidate_labels, **kwargs)
        scores = {label: score for label, score in zip(result['labels'], result['scores'])} 

        # Return scores in the order the labels were provided
        return [scores[k] for k in candidate_labels]
    
    return score_labels


@lru_cache(maxsize=1)
def get_embedding_model():
    """Return the language embedding model or a mock function in debug mode"""
    return SentenceTransformer('all-MiniLM-L6-v2').encode


@lru_cache(maxsize=1)
def get_document_model():
    """Return the spacy NLP model or a blank model in debug mode"""
    return spacy.load("en_core_web_lg")
