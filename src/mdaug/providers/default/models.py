"""Lazy model loaders used by default non-mock providers."""

from functools import lru_cache
import hashlib
import re


def _fallback_acceptability(content: str) -> dict[str, float]:
    """Fallback acceptability proxy based on sentence length."""
    word_count = len(content.split())
    if word_count == 0:
        return {"score": 0.0}

    if word_count <= 3:
        return {"score": 0.65}
    if word_count <= 12:
        return {"score": 0.9}
    if word_count <= 20:
        return {"score": 0.8}
    return {"score": 0.7}


def _fallback_embed(texts: list[str]) -> list[list[float]]:
    """Fallback deterministic embeddings using hashed token bins."""
    embeddings = []
    for text in texts:
        vector = [0.0] * 32
        tokens = [token.lower() for token in re.findall(r"[A-Za-z0-9]+", text)]
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            index = int(digest[:2], 16) % len(vector)
            vector[index] += 1.0

        norm = sum(value * value for value in vector) ** 0.5 or 1.0
        embeddings.append([round(value / norm, 6) for value in vector])

    return embeddings


def _fallback_generate(content: str, **kwargs) -> list[str]:
    """Fallback text generation by returning sentence-like snippets."""
    _ = kwargs
    parts = [part.strip() for part in re.split(r"[.!?;\n]+", content) if part.strip()]
    if not parts:
        return []

    candidates = []
    for part in parts[:3]:
        tokens = part.split()
        candidates.append(" ".join(tokens[: min(10, len(tokens))]))

    return list(dict.fromkeys(candidate for candidate in candidates if candidate))


def _fallback_keywords(content: str, top_n: int) -> list[str]:
    """Fallback keyword extraction using unique lowercase tokens."""
    tokens = [token.lower() for token in re.findall(r"[A-Za-z0-9]+", content)]
    unique_tokens = list(dict.fromkeys(tokens))
    return unique_tokens[:top_n]


def _unwrap_classification(result) -> list[dict]:
    """Normalize transformers classification outputs into a list of dict items."""
    if isinstance(result, list) and result and isinstance(result[0], list):
        return result[0]

    if isinstance(result, list):
        return result

    if isinstance(result, dict):
        return [result]

    return []


@lru_cache(maxsize=1)
def get_acceptability_model():
    """Return a CoLA-style acceptability scoring callable."""
    try:
        from transformers import pipeline
        classifier = pipeline("text-classification", model="textattack/roberta-base-CoLA")
    except Exception:
        return _fallback_acceptability

    def score_acceptability(content: str) -> dict[str, float]:
        """Compute acceptability score for the supplied string."""
        try:
            result = classifier(content, truncation=True)
            return {"score": float(result[0]["score"])}
        except Exception:
            return _fallback_acceptability(content)

    return score_acceptability


@lru_cache(maxsize=1)
def get_document_model():
    """Return a spaCy model for sentence/entity extraction."""
    try:
        import spacy
    except ModuleNotFoundError:
        class SimpleSentence:
            """Fallback sentence wrapper with text attribute."""

            def __init__(self, text: str):
                self.text = text

        class SimpleDoc:
            """Fallback document wrapper exposing .ents and .sents."""

            def __init__(self, text: str):
                self.ents = []
                parts = [part.strip() for part in re.split(r"[.!?;\n]+", text) if part.strip()]
                self.sents = [SimpleSentence(part) for part in parts]

        def make_doc(text: str):
            """Fallback document constructor without spaCy dependency."""
            return SimpleDoc(text)

        return make_doc

    for model_name in ("en_core_web_lg", "en_core_web_sm"):
        try:
            return spacy.load(model_name)
        except OSError:
            continue

    nlp = spacy.blank("en")
    if "sentencizer" not in nlp.pipe_names:
        nlp.add_pipe("sentencizer")

    return nlp


@lru_cache(maxsize=1)
def get_embedding_model():
    """Return a sentence-transformers embedding encoder callable."""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode
    except Exception:
        return _fallback_embed


@lru_cache(maxsize=4)
def get_generative_model(model_name: str = "sshleifer/tiny-gpt2"):
    """Return a text generation callable using a transformers pipeline."""
    try:
        from transformers import pipeline
        generator = pipeline("text-generation", model=model_name)
    except Exception:
        return _fallback_generate

    default_kwargs = {
        "max_new_tokens": 96,
        "num_return_sequences": 3,
        "temperature": 0.7,
        "top_p": 0.9,
        "do_sample": True,
    }

    def infer(content: str, **kwargs) -> list[str]:
        """Return generated text from the configured language model."""
        model_kwargs = default_kwargs.copy()
        model_kwargs.update(kwargs)
        try:
            sequences = generator(content, return_full_text=False, **model_kwargs)
            return [str(sequence.get("generated_text", "")).strip() for sequence in sequences]
        except Exception:
            return _fallback_generate(content, **kwargs)

    return infer


@lru_cache(maxsize=4)
def get_keyword_model(top_n: int = 10):
    """Return a combined KeyBERT + YAKE keyword extraction callable."""
    half_top_n = max(1, top_n // 2)

    try:
        import keybert
        import yake
        keybert_model = keybert.KeyBERT("all-MiniLM-L6-v2")
        yake_extractor = yake.KeywordExtractor(
            lan="en",
            n=1,
            dedupLim=0.9,
            dedupFunc="seqm",
            top=half_top_n,
            features=None,
        )
    except Exception:
        return lambda content: _fallback_keywords(content, top_n)

    def extract_keywords(content: str) -> list[str]:
        """Extract and combine KeyBERT and YAKE keyword candidates."""
        try:
            keybert_pairs = keybert_model.extract_keywords(
                content,
                keyphrase_ngram_range=(1, 1),
                stop_words="english",
                top_n=half_top_n,
                use_mmr=False,
            )
            keybert_keywords = [phrase for phrase, _score in keybert_pairs]
            yake_keywords = [phrase for phrase, _score in yake_extractor.extract_keywords(content)]
            unique_keywords = list(dict.fromkeys(keybert_keywords + yake_keywords))
            return [keyword.lower() for keyword in unique_keywords if keyword]
        except Exception:
            return _fallback_keywords(content, top_n)

    return extract_keywords


@lru_cache(maxsize=1)
def get_polarity_model():
    """Return a polarity scoring callable using TextBlob and VADER."""
    try:
        from textblob import TextBlob
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
    except Exception:
        return lambda content: {"score": 0.0 if not content.strip() else 0.2}

    def score_polarity(content: str) -> dict[str, float]:
        """Compute polarity score by averaging TextBlob and VADER compound polarity."""
        try:
            blob_score = float(TextBlob(content).sentiment.polarity)
            vader_score = float(analyzer.polarity_scores(content)["compound"])
            return {"score": (blob_score + vader_score) / 2}
        except Exception:
            return {"score": 0.0}

    return score_polarity


@lru_cache(maxsize=1)
def get_sentiment_model():
    """Return sentiment class scoring callable using VADER."""
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
    except Exception:
        return lambda content: {"negative": 0.0, "neutral": 1.0, "positive": 0.0}

    def score_sentiment(content: str) -> dict[str, float]:
        """Compute negative/neutral/positive sentiment scores."""
        try:
            sentiment = analyzer.polarity_scores(content)
            return {
                "negative": float(sentiment["neg"]),
                "neutral": float(sentiment["neu"]),
                "positive": float(sentiment["pos"]),
            }
        except Exception:
            return {"negative": 0.0, "neutral": 1.0, "positive": 0.0}

    return score_sentiment


@lru_cache(maxsize=1)
def get_toxicity_model():
    """Return a toxicity scoring callable backed by a transformer model when available."""
    classifier = None
    model_loaded = False

    toxic_terms = ("idiot", "stupid", "hate", "trash", "worthless", "moron", "dumb")

    def _load_classifier():
        """Load the toxicity classifier once, only when needed."""
        nonlocal classifier, model_loaded
        if model_loaded:
            return classifier

        model_loaded = True
        try:
            from transformers import pipeline
            classifier = pipeline("text-classification", model="unitary/toxic-bert", top_k=None)
        except Exception:
            classifier = None

        return classifier

    def score_toxicity(content: str) -> dict[str, float]:
        """Compute toxicity score as probability-like value in [0.0, 1.0]."""
        lowered = content.lower()
        has_toxic_cue = "!" in content or any(term in lowered for term in toxic_terms)
        if not has_toxic_cue:
            return {"score": 0.0}

        loaded_classifier = _load_classifier()
        if loaded_classifier is not None:
            try:
                predictions = _unwrap_classification(loaded_classifier(content, truncation=True))
                if predictions:
                    by_label = {
                        str(item.get("label", "")).lower(): float(item.get("score", 0.0))
                        for item in predictions
                    }
                    if "toxic" in by_label:
                        return {"score": round(by_label["toxic"], 4)}

                    return {"score": round(max(by_label.values(), default=0.0), 4)}
            except Exception:
                pass

        term_hits = sum(1 for term in toxic_terms if term in lowered)
        exclamations = content.count("!")
        return {"score": min(1.0, round((term_hits + exclamations) / 8.0, 4))}

    return score_toxicity


@lru_cache(maxsize=1)
def get_spam_model():
    """Return a spam scoring callable with legacy model path and fallback proxy."""
    torch = None
    spam_tokenizer = None
    spam_classifier = None
    model_loaded = False

    spam_terms = ("congratulations", "winner", "won", "gift card", "claim", "click", "free", "offer")
    spam_index = 1

    def _load_classifier():
        """Load the legacy spam classifier once, only when needed."""
        nonlocal torch, spam_tokenizer, spam_classifier, spam_index, model_loaded
        if model_loaded:
            return spam_tokenizer, spam_classifier, torch, spam_index

        model_loaded = True
        try:
            import torch as torch_module
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            spam_tokenizer = AutoTokenizer.from_pretrained("AntiSpamInstitute/spam-detector-bert-MoE-v2.2")
            spam_classifier = AutoModelForSequenceClassification.from_pretrained(
                "AntiSpamInstitute/spam-detector-bert-MoE-v2.2"
            )
            torch = torch_module

            labels = {
                int(index): str(label).lower()
                for index, label in spam_classifier.config.id2label.items()
            }
            matched = [index for index, label in labels.items() if "spam" in label]
            if matched:
                spam_index = matched[0]
        except Exception:
            torch = None
            spam_tokenizer = None
            spam_classifier = None

        return spam_tokenizer, spam_classifier, torch, spam_index

    def score_spam(content: str) -> dict[str, float]:
        """Compute spam score as probability-like value in [0.0, 1.0]."""
        lowered = content.lower()
        has_spam_cue = (
            any(term in lowered for term in spam_terms)
            or "$" in content
            or "http://" in lowered
            or "https://" in lowered
            or "www." in lowered
            or "click here" in lowered
        )
        if not has_spam_cue:
            return {"score": 0.0}

        loaded_tokenizer, loaded_classifier, loaded_torch, loaded_spam_index = _load_classifier()
        if loaded_tokenizer is not None and loaded_classifier is not None and loaded_torch is not None:
            try:
                inputs = loaded_tokenizer(content, return_tensors="pt", truncation=True)
                with loaded_torch.no_grad():
                    outputs = loaded_classifier(**inputs)

                probabilities = loaded_torch.softmax(outputs.logits, dim=1).flatten()
                score = float(probabilities[loaded_spam_index].item())
                return {"score": round(score, 4)}
            except Exception:
                pass

        matches = sum(1 for term in spam_terms if term in lowered)
        return {"score": min(1.0, round((matches + content.count("!")) / 8.0, 4))}

    return score_spam
