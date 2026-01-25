import torch

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

from functools import lru_cache

from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification


@lru_cache(maxsize=1)
def get_acceptability_model():
    """Return the acceptability classifier pipeline or a mock function in debug mode"""
    pipe = pipeline("text-classification", model="textattack/roberta-base-CoLA")

    def score_acceptability(content: str) -> float:
        """Compute acceptability score for the supplied string"""
        result = pipe(content)
        return {'score': result[0]['score']}
    
    return score_acceptability


@lru_cache(maxsize=1)
def get_polarity_model():
    """Return the TextBlob polarity model or a mock function in debug mode"""
    # For both sets of scores: -1 most extreme negative, +1 most extreme positive
    analyzer = SentimentIntensityAnalyzer()
    
    def score_polarity(content: str) -> dict:
        """Compute blob and vader polarity for the supplied string"""
        blob_score = TextBlob(content).sentiment.polarity
        vader_score = analyzer.polarity_scores(content)['compound']
        return {'score': (blob_score + vader_score) / 2}

    return score_polarity


@lru_cache(maxsize=1)
def get_sentiment_model():
    """Return the vader sentiment model or a mock function in debug mode"""
    analyzer = SentimentIntensityAnalyzer()

    def score_sentiment(content: str) -> dict:
        """Compute bart and vader sentiment scores for the supplied string"""
        # TODO: Add BART sentiment model and combine here
        sentiment_scores = analyzer.polarity_scores(content)
        sentiment_scores = {k: sentiment_scores[k] for k in ('neg', 'neu', 'pos')}
        return sentiment_scores
    
    return score_sentiment


@lru_cache(maxsize=1)
def get_spam_model():
    """Return the spam classifier tokenizer and model or a mock function in debug mode"""
    spam_tokenizer = AutoTokenizer.from_pretrained("AntiSpamInstitute/spam-detector-bert-MoE-v2.2")
    spam_classifier = AutoModelForSequenceClassification.from_pretrained("AntiSpamInstitute/spam-detector-bert-MoE-v2.2")
    
    def score_spam(content: str) -> float:
        """Compute spam scores for the supplied text content"""
        # Tokenize the input
        inputs = spam_tokenizer(content, return_tensors="pt")

        # Get model predictions
        with torch.no_grad():
            outputs = spam_classifier(**inputs)
            logits = outputs.logits

        # Apply softmax to get probabilities
        probabilities = torch.softmax(logits, dim=1)
        return {'score': probabilities.flatten()[1].item()}

    return score_spam


@lru_cache(maxsize=1)
def get_toxicity_model():
    """Return the toxicity classifier pipeline or a mock function in debug mode"""
    pipe = pipeline("text-classification", model="unitary/toxic-bert")

    def score_toxicity(content: str) -> float:
        """Compute toxicity score for the supplied string"""
        result = pipe(content)
        return {'score': result[0]['score']}

    return score_toxicity
