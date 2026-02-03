from app.core.metrics import polarity, sentiment, spam, style
from app.core.common.headings import get_title, get_subtitle, get_description, get_outline
from app.core.common.extract import extract_entities, extract_keywords, extract_related


METRIC_TYPES = {
    "diction": style.score_diction,         # Vocabulary, formality and complexity of text
    "genre": style.score_genre,             # The assessed literary category
    "mode": style.score_mode,               # The writing style or voice
    "tone": style.score_tone,               # The expressed subjectivity (from dogmatic to impartial)
    "sentiment": sentiment.score_sentiment, # The negative, neutral, and positive class scores [0.0, 1.0]
    "polarity": polarity.score_polarity,    # The degree of negative or positive sentiment [-1.0, 1.0]
    "toxicity": spam.score_toxicity,        # The computed toxcicity score [0.0, 1.0] 
    "spam": spam.score_spam,                # The negative and positive spam class scores [0.0, 1.0]
}

SUMMARY_TYPES = {
    "title": get_title,                     # Suggested content titles
    "subtitle": get_subtitle,               # Candidate content subtitles 
    "description": get_description,         # Basic content summaries
    "outline": get_outline                  # A list of content section key points or themes
}

TAG_TYPES = {
    "entities": extract_entities,           # Named entities such as people, organizations, locations, etc.
    "keywords": extract_keywords,           # Important keywords and phrases that capture the main topics
    "related": extract_related              # Related topics and concepts derived from the content
}


def get_metrics(content: str, metrics: list=None) -> dict:
    """Return a dictionary of the requested metrics for the supplied content"""
    results = {}
    # Default to all metrics if none are specified
    metrics = metrics if metrics else list(METRIC_TYPES.keys())
    for metric in metrics:
        if metric in METRIC_TYPES:
            results[metric] = METRIC_TYPES[metric](content)
    # Return a dict of all requested metrics
    return results


def get_summary(content: str, summary: str='description', **kwargs) -> tuple:
    """Return a dictionary of entities, keywords, and related topic tags"""
    summaries, scores = [], []
    # Get requested summary type
    if summary in SUMMARY_TYPES:
        summary_function = SUMMARY_TYPES[summary]
        summaries, scores = summary_function(content, **kwargs)
    # Return a dict of lists (summaries, scores)
    return dict(summaries=summaries, scores=scores)


def get_tags(content: str, min_length: int=1, max_length: int=3, top_n: int=10) -> dict:
    """Return a dictionary of entities, keywords, and related topic tags"""
    # Extract entities, keywords, and related tags with similarity scores
    entities, entity_scores = extract_entities(content, top_n)
    keywords, keyword_scores = extract_keywords(content, top_n)
    related, related_scores = extract_related(content, min_length, max_length, top_n)
    # Return a pair of dictionaries for tags and scores
    tags = dict(entities=entities, keywords=keywords, related=related)
    scores = dict(entities=entity_scores, keywords=keyword_scores, related=related_scores)
    # Return a dict of lists (tags, scores)
    return dict(tags=tags, scores=scores)

# TODO: Update get methods to accept dependencies
def get_result(operation: str, dependencies: dict, request: dict) -> dict:
    """Return a dictionary of results from the specified operation"""
    content = request.get("content", "")
    parameters = request.get("parameters", {})
    match operation:
        case "metrics":
            return get_metrics(content, **parameters)
        case "summary":
            return get_summary(content, **parameters)
        case "tags":
            return get_tags(content, **parameters)
