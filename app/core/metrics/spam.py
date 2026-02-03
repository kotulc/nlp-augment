import numpy

from app.models.sentiment import get_spam_model, get_toxicity_model

from app.core.common.text import SPAM_TEXT, HAM_TEXT, NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT, SAMPLE_TEXT


# Get pre-trained toxicity and spam detection models
spam_classifier = get_spam_model()
toxicity_classifier = get_toxicity_model()


def score_spam(content: str) -> dict:
    """Compute spam scores for the supplied text content"""
    score = round(float(spam_classifier(content)['score']), 4)
    label = "ham" if score < 0.5 else "spam"
    return dict(score=score, label=label)


def score_toxicity(content: str) -> dict:
    """Compute toxicity scores for the supplied text content"""
    # Simply apply the toxicity classifier to the input
    score = round(float(toxicity_classifier(content)['score']), 4)
    label = "neutral" if score < 0.5 else "toxic"
    return dict(score=score, label=label)


# Example usage and testing function
def demo_spam():
    """Test the spam scoring functions with different parameters"""
    # Group all labels and content
    content_labels = ('spam', 'ham', 'negative', 'neutral', 'positive', 'document')
    content_strings = (SPAM_TEXT, HAM_TEXT, NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT, SAMPLE_TEXT)

    print("\n== Spam Classification ===")
    for label, content in zip(content_labels, content_strings):
        # Get predicted labels and map labels to class names
        result = score_spam(content)
        score = result['score']
        label = result['label']

        print(f"\n{label.capitalize()} text: {content}\nPrediction: {label}")    
        print("Spam score:", score)
        
        result = score_toxicity(content)
        print("Toxicity result:", result)


if __name__ == "__main__":
    demo_spam()
