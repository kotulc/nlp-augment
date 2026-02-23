from app.core.common.generate import generate_summary
from app.core.common.relevance import maximal_marginal_relevance, semantic_similarity
from app.models.general import get_document_model
from app.models.keyword import get_keyword_model
from app.config import get_settings

from app.core.common.text import SAMPLE_TEXT


# Define module level constants
settings = get_settings()
TAG_PROMPTS = settings.model.prompts.tag

# Get module level variables
doc_model = get_document_model()
keyword_model = get_keyword_model(top_n=10)


def extract_entities(content: str, top_n: int=5) -> list:
    """Extract entities and return the top_n results"""
    # Extract entity tags from spacy pipeline
    entities = list({entity.text.strip() for entity in doc_model(content).ents})

    if len(entities):
        entities, scores = semantic_similarity(content, entities)
        return entities[:top_n], scores[:top_n]
    else:
        return [], []


def extract_keywords(content: str, top_n: int=10) -> list:
    """Extract entities and return the top_n most relevant results"""
    # Extract keywords and compare source relevance with cosine similiarty
    candidates = keyword_model(content)
    keywords, scores = semantic_similarity(content, candidates)

    return keywords[:top_n], scores[:top_n]


def extract_related(content: str, min_length: int=1, max_length: int=3, top_n: int=10) -> dict:
    """Use language models to generate lists of related concepts and topics"""
    # Generate related topics, themes, and concepts
    tag_strings = []
    for prompt in TAG_PROMPTS:
        tag_strings += generate_summary(
            content=content,
            prompt=prompt,
            format="list", 
            max_new_tokens=top_n * 12, 
            temperature=0.7
        )

    # Filter generated tag by length and return the top_n similarity results    
    candidates = [s for s in tag_strings if len(s.split()) >= min_length and len(s.split()) <= max_length]
    tags, scores = maximal_marginal_relevance(content, candidates)

    return tags[:top_n], scores[:top_n]


# Example usage and testing function
def demo_tagger():
    """Test the tagging functionality with different parameters."""
    print("\n=== Basic Tagging ===")
    result = extract_entities(SAMPLE_TEXT, top_n=5)
    print("\nExtracted entities:", result)

    result = extract_keywords(SAMPLE_TEXT, top_n=8)
    print("\nExtracted keywords:", result)

    result = extract_related(SAMPLE_TEXT, min_length=1, max_length=3, top_n=5)
    print("\nExtracted related tags (min ngram=1):", result)

    result = extract_related(SAMPLE_TEXT, min_length=2, max_length=5, top_n=5)
    print("\nExtracted related tags (min ngram=2):", result)


if __name__ == "__main__":
    demo_tagger()
