import keybert
import yake

from functools import lru_cache


@lru_cache(maxsize=1)
def get_keyword_model(top_n: int=10):
    """Return the keyword extraction model or a mock function in debug mode"""
    key_bert = keybert.KeyBERT('all-MiniLM-L6-v2')
    yake_extractor = yake.KeywordExtractor(
            lan="en", 
            n=1, 
            dedupLim=0.9, 
            dedupFunc="seqm", 
            top=top_n // 2, 
            features=None
        )
    
    def extract_keywords(content: str) -> list:
        """Extract bert and yake keywords"""
        bert_keywords = key_bert.extract_keywords(
            content, 
            keyphrase_ngram_range=(1, 1), 
            stop_words='english', 
            top_n=top_n // 2, 
            use_mmr=False
        )
        bert_keywords = [phrase for phrase, score in bert_keywords]
        yake_keywords = yake_extractor.extract_keywords(content)
        yake_keywords = [phrase for phrase, score in yake_keywords]

        # Get unique combined keywords
        keywords = bert_keywords + yake_keywords
        return list({k.lower() for k in keywords})
    
    return extract_keywords
