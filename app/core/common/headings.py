import numpy

from app.core.common.generate import generate_summary
from app.core.common.relevance import composite_scores
from app.models.general import get_document_model
from app.settings import get_settings

from app.core.common.text import SAMPLE_TEXT

# Extract module-level constants from settings
settings = get_settings()
MODEL_PROMPTS = settings.model.prompts.model_dump()

# Define module-level variables
doc_model = get_document_model()


def get_headings(content: str, heading: str, top_n: int) -> tuple[list, list]:
    """Generate a list of short heading summaries for the supplied content"""
    if not heading in MODEL_PROMPTS:
        raise ValueError(f"Supplied heading type '{heading}' is not a supported value.")
    
    # Define common generation kwargs
    generation_kwargs = dict(format="list", max_new_tokens=top_n * 12)

    candidates = []
    for prompt in MODEL_PROMPTS[heading][:-1]:
        # Generate candidate tiles for each prompt
        candidates += generate_summary(content=content, prompt=prompt, **generation_kwargs)

    # Combine all generated titles into a new content string
    title_content = " ".join(candidates)

    # Add some more variety detached from the source content
    re_prompt = MODEL_PROMPTS[heading][-1]
    candidates += generate_summary(content=title_content, prompt=re_prompt, **generation_kwargs)
    candidates, scores = composite_scores(content=content, candidates=candidates)

    return candidates[:top_n], scores[:top_n]


def get_title(content: str, top_n: int=3) -> tuple[list, list]:
    """Generate a list of titles for the supplied content"""
    return get_headings(content, heading="title", top_n=top_n)


def get_subtitle(content: str, top_n: int=3) -> tuple[list, list]:
    """Generate a list of short subtitles for the supplied content"""
    return get_headings(content, heading="subtitle", top_n=top_n)


def get_description(content: str, top_n: int=3) -> tuple[list, list]:
    """Generate a list of short description summaries for the supplied content"""
    return get_headings(content, heading="description", top_n=top_n)


def get_outline(content: str, n_sections: int=3) -> list:
    """Perform map-reduce sentence summarization to generate an outline"""
    # Split the supplied content string into individual sentences
    content_sentences = [s.text for s in doc_model(content).sents]

    if len(content_sentences) == 0:
        raise ValueError("Supplied content string must contain one or more sentences.")

    # Split the document into n_sections and iteratively combine sentences 
    sections = []
    n_sentences = int(numpy.ceil(len(content_sentences) / n_sections))
    for i in range(0, n_sentences * n_sections, n_sentences):
        sections.append(" ".join(content_sentences[i:i + n_sentences]))

    # Define outline-specific generation kwargs
    generation_kwargs = dict(format="list", max_new_tokens=32)

    # Generate candidate section descriptions
    section_summaries, section_scores = [], []
    for section in sections:
        # Generate candidate summaries for each prompt
        section_candidates = []
        for prompt in MODEL_PROMPTS["description"][:-1]:
            section_candidates += generate_summary(content=section, prompt=prompt, **generation_kwargs)
        
        # Score and select the top_n descriptions for each section
        candidates, scores = composite_scores(content=section, candidates=section_candidates)
        section_summaries.append(candidates[0])
        section_scores.append(scores[0])

    return section_summaries, section_scores


# Example usage and testing function
def demo_headings():
    """Test the heading and section outline generation functionality"""
    print("\n=== Generate Headings ===")
    n_sections, top_n = 3, 5
    for heading in MODEL_PROMPTS.keys():
        result = get_headings(SAMPLE_TEXT, heading=heading, top_n=top_n)
        print(f"\nGenerated {heading}s:", result)

    print("\n=== Generate Outline ===")
    result = get_outline(SAMPLE_TEXT, n_sections=n_sections)
    for i in range(n_sections):
        section_summaries = [section[i] for section in result if len(section) > i]
        print(f"\nOutline candidate {i + 1}:")
        for section_summary in section_summaries:
            print("\t-", section_summary)


if __name__ == "__main__":
    demo_headings()
