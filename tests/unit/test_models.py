import pytest

from app.models import loader
from app.models import sentiment, generative, keyword, utility


# Define mock inputs for testing
MOCK_CONTENT = "This is test input for the model"
MOCK_LABELS = ["label1", "label2"]


def patch_test(monkeypatch, model_callable, debug_callable):
    # Reset model function LRU cache
    model_callable.cache_clear()
    
    # Test with debug True (use debug model)
    monkeypatch.setattr(loader.settings, "debug", debug_callable)

    # Verify function is callable and I/O is as expected
    assert callable(model_callable)


@pytest.mark.parametrize("debug_callable", [True, False])
def test_classifier_model(monkeypatch, debug_callable):
    patch_test(monkeypatch, utility.get_classifier_model, debug_callable)

    # All model callables should align with the request/response models
    utility.classifierRequest(content=MOCK_CONTENT, candidate_labels=MOCK_LABELS)
    model_output = utility.get_classifier_model()(MOCK_CONTENT, candidate_labels=MOCK_LABELS)
    utility.classifierResponse(results=model_output)


# TODO: Add remaining sentiment models after fixing current issues
@pytest.mark.parametrize("model_callable, request_model, response_model", [
    (generative.get_generative_model, generative.generativeRequest, generative.generativeResponse),
    (keyword.get_keyword_model, keyword.keywordRequest, keyword.keywordResponse),
    (sentiment.get_acceptability_model, sentiment.sentimentRequest, sentiment.sentimentResponse),
    (sentiment.get_polarity_model, sentiment.sentimentRequest, sentiment.sentimentResponse),
    (sentiment.get_sentiment_model, sentiment.sentimentRequest, sentiment.sentimentResponse),
    (sentiment.get_spam_model, sentiment.sentimentRequest, sentiment.sentimentResponse),
    (sentiment.get_toxicity_model, sentiment.sentimentRequest, sentiment.sentimentResponse),
])
@pytest.mark.parametrize("debug_callable", [True, False])
def test_model_io(monkeypatch, model_callable, request_model, response_model, debug_callable):
    patch_test(monkeypatch, model_callable, debug_callable)

    # All model callables should align with the request/response models
    request_model(content=MOCK_CONTENT) 
    model_output = model_callable()(MOCK_CONTENT)
    response_model(results=model_output)
