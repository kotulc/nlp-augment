import numpy

from textblob import TextBlob

from app.models.general import get_classifier_model

from app.core.common.text import NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT, SAMPLE_TEXT


# Define elements of literary analysis
# Attempt to define labels on a scale of very low to very high in a given linguistic quality
DICTION_LABELS = ['formal', 'concrete', 'informal', 'colloquial', 'literary', 'poetic', 'abstract']
GENRE_LABELS = ['romance', 'drama', 'suspense', 'historical', 'non-fiction', 'adventure', 'sci-fi', 'fantasy']
MODE_LABELS = ['expository', 'descriptive', 'persuasive', 'narrative', 'creative', 'experimental']
TONE_LABELS = ['dogmatic', 'subjective', 'neutral', 'objective', 'impartial']

# Define module-level variables
classifier = get_classifier_model()


def classify_content(content: str, labels: list, multi_label=False) -> list:
    """Return the zero-shot classification scores in the order of the supplied labels"""
    # NOTE: If more than one label can be correct, set multi_label=True
    result = classifier(content, candidate_labels=labels, multi_label=multi_label)
    scores = {label: score for label, score in zip(result['labels'], result['scores'])} 

    # Return scores in the order the labels were provided
    return [scores[k] for k in labels]


def score_diction(content: str) -> tuple[(list, str)]:
    """Return the zero-shot classification scores for diction"""
    # Zero-shot diction score (ideally this uses a fine-tuned a model)
    result = classifier(content, DICTION_LABELS)
    scores = dict(zip(DICTION_LABELS, [round(float(v), 4) for v in result]))

    return scores, DICTION_LABELS[numpy.argmax(result)]


def score_genre(content: str) -> tuple[(list, str)]:
    """Return the zero-shot classification scores for genre"""
    # Zero-shot genre score (ideally this uses a fine-tuned a model)
    result = classifier(content, GENRE_LABELS)
    scores = dict(zip(GENRE_LABELS, [round(float(v), 4) for v in result]))

    return scores, GENRE_LABELS[numpy.argmax(result)]


def score_mode(content: str) -> tuple[(list, str)]:
    """Return the zero-shot classification scores for style"""
    # Zero-shot style score (ideally this uses a fine-tuned a model)
    result = classifier(content, MODE_LABELS)
    scores = dict(zip(MODE_LABELS, [round(float(v), 4) for v in result]))
    
    return scores, MODE_LABELS[numpy.argmax(result)]


def score_tone(content: str) -> tuple[(list, str)]:
    """Return the zero-shot classification and textblob scores for subjectivity (tone)"""
    # Textblob subjectvitiy scores range [0.0, 1.0] with 1.0 being highly subjective
    blob_score = TextBlob(content).sentiment.subjectivity

    # Find distances from value to each label 'bucket'
    buckets = numpy.linspace(0, 1, len(TONE_LABELS))
    distances = numpy.abs(numpy.array(buckets) - blob_score)
    
    # Calculate gaussian kernel weights and normalize to sum to 1
    weights = numpy.exp(-1 * (distances**2) / 0.1)
    distribution = weights / numpy.sum(weights)

    # Zero-shot subjectivity score (ideally this uses a fine-tuned a model)
    result = classifier(content, TONE_LABELS)

    # Combine scores and re-normalize
    result = (result + distribution) / numpy.sum(result + distribution)
    scores = dict(zip(TONE_LABELS, [round(float(v), 4) for v in result]))

    return scores, TONE_LABELS[numpy.argmax(result)]


# Example usage and testing function
def demo_style():
    """Test the style scoring function with different parameters"""
    content_labels = ('negative', 'neutral', 'positive', 'document')
    content_text = (NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT, SAMPLE_TEXT)
    
    print("\n== Document Analysis ===")
    for content_label, content in zip(content_labels, content_text):
        print(f"\nText: {content_label}")
        
        # Diction score and label
        scores, label = score_diction(content)
        print("Diction score:", scores, "Label:", label)

        # Genre score and label
        scores, label = score_genre(content)
        print("Genre score:", scores, "Label:", label)

        # Mode score and label
        scores, label = score_mode(content)
        print("Mode score:", scores, "Label:", label)

        # Subjectivity score and label
        scores, label = score_tone(content)
        print("Tone score:", scores, "Label:", label)


if __name__ == "__main__":
    demo_style()
