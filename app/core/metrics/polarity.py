from app.models.sentiment import get_polarity_model
from app.models.general import get_document_model

from app.core.common.text import NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT, SAMPLE_TEXT


# Get module level variables
polarity_model = get_polarity_model()
doc_model = get_document_model()


def score_polarity(content: str) -> dict:
    """Compute blob and vader polarity for the supplied string"""
    # For both sets of scores: -1 most extreme negative, +1 most extreme positive
    doc = doc_model(content)
    return round(polarity_model(doc.text)['score'], 4)


def sentence_polarity(content: str) -> list:
    """Compute blob and vader polarity for each sentence in the supplied string"""
    doc = doc_model(content)

    sentence_list, score_list = [], []
    for sentence in doc.sents:
        # For both sets of scores: -1 most extreme negative, +1 most extreme positive
        sentence_text = sentence.text
        sentence_list.append(sentence_text)
        score_list.append(round(polarity_model(sentence_text)['score'], 4))

    return sentence_list, score_list


# Example usage and testing function
def demo_polarity():
    """Test the polarity functions with different parameters"""
    content_labels = ('negative', 'neutral', 'positive', 'document')
    content_text = (NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT, SAMPLE_TEXT)

    print("\n== Document Polarity ===")
    for label, content in zip(content_labels, content_text):
        print(f"\nText: {label}")
        
        polarity_score = score_polarity(content)
        print(f"Content Polarity:", polarity_score)
        
    print("\n== Sentence Polarity ===")
    print(f"\nText: sample_text")
    # Textblob and vader_score polarity scores range from [-1.0, 1.0] with 1 being the most positive
    sentences, scores = sentence_polarity(SAMPLE_TEXT)
    
    # Format document sentence in a more readable way
    print(f"Sentence Polarity:")
    for s, score in zip(sentences, scores):
        clean_text = "'" + " ".join(s.strip().split())[:60] + "...':"
        print(f"{clean_text:<64}", score)


if __name__ == "__main__":
    demo_polarity()
