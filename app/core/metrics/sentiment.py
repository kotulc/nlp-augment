from app.models.sentiment import get_sentiment_model
from app.models.general import get_document_model

from app.core.common.text import SAMPLE_TEXT, NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT


# Define sentiment class constant
SENTIMENT_CLASSES = ["negative", "neutral", "positive"]

# Get module level variables
sentiment_model = get_sentiment_model()
doc_model = get_document_model()


def score_sentiment(content: str) -> dict[str, float]:
    """Compute bart and vader sentiment scores for the supplied string"""
    doc = doc_model(content)
    return sentiment_model(doc.text)


def sentence_sentiment(content: str) -> dict[str, list]:
    """Compute bart and vader sentiment scores for each sentence in the supplied string"""
    doc = doc_model(content)

    sentence_list, score_list = [], []
    for sentence in doc.sents:
        # Get bart and vader scores in an equivalent format (including precision)
        sentence_list.append(sentence.text)
        score_list.append(sentiment_model(sentence.text))

    return dict(sentences=sentence_list, scores=score_list)


# Example usage and testing function
def demo_sentiment():
    """Test the sentiment functions with different parameters"""
    content_labels = ('negative', 'neutral', 'positive', 'document')
    content_text = (NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT, SAMPLE_TEXT)
    print("\n== Document Sentiment ===")

    for label, content in zip(content_labels, content_text):
        print(f"\nText: {label}")
        sentiment_score = score_sentiment(content)
        print(f"Content Sentiment:", sentiment_score)
        
    print("\n== Sentence Sentiment ===")
    print(f"\nText: sample_text")
    sentiment_dict = sentence_sentiment(SAMPLE_TEXT)
    print(f"Sentence Sentiment:")
    for s, score in zip(sentiment_dict['sentences'], sentiment_dict['scores']):
        clean_text = "'" + " ".join(s.strip().split())[:60] + "...':"
        print(f"{clean_text:<64}", score)


if __name__ == "__main__":
    demo_sentiment()
