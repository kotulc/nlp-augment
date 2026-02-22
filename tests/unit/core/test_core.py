from app.core.metrics import polarity, sentiment, spam, style
from app.core.common import headings, generate, extract


def test_polarity():
    """Run the polarity metric function demo and ensure it runs without error"""
    polarity.demo_polarity()


def test_sentiment():
    """Run the sentiment metric function demo and ensure it runs without error"""
    sentiment.demo_sentiment()


def test_spam():
    """Run the spam metric function demo and ensure it runs without error"""
    spam.demo_spam()


def test_style():
    """Run the toxicity metric function demo and ensure it runs without error"""
    style.demo_style()


def test_generator():
    """Run the summary generation function demo and ensure it runs without error"""
    generate.demo_generator()


def test_headings():
    """Run the heading generation function demo and ensure it runs without error"""
    headings.demo_headings()


def test_extract():
    """Run the tagging function demo and ensure it runs without error"""
    extract.demo_tagger()
