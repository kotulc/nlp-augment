import re

from src.mdaug.core.config import get_settings
from src.models.generative import get_generative_model
from src.core.common.text import SAMPLE_TEXT


# Extract constants from settings
settings = get_settings()
DEFAULT_MODEL = settings.model.language_model
DEFAULT_TEMPLATE = settings.model.prompts.template
DEFAULT_KWARGS = settings.model.transformers.model_dump()

# Load the tokenizer and model
generator = get_generative_model()


def generate_response(content: str, prompt: str, delimiter: str="Output:", **kwargs) -> list[str]:
    """Generate a content summary string using a specified model and prompt"""
    # Apply the prompt template and generate the summary
    text_prompt = DEFAULT_TEMPLATE.format(prompt=prompt, content=content, delimiter=delimiter)
    return generator(text_prompt, **kwargs)


def generate_summary(content: str, prompt: str, format: str=None, tone: str=None, **kwargs) -> list[str]:
    """Generate a summary with the provided prompt and parse the model output accordingly"""
    # Add a conversational tone to the supplied prompt if requested
    if tone: prompt += f" in a {tone} tone"

    # Apply the prompt template and generate the summary text
    if format:
        # Use the supplied summary type as the generated text output delimeter
        response = generate_response(content, prompt, delimiter=f"<|{format}|>:", **kwargs)
    else:
        # Use the default delimiter
        response = generate_response(content, prompt, **kwargs)
    
    # Parse and format the generated text based on known special characters:
    if format and format.lower() in ("outline", "list", "points"):
        # Split results on common list delimiters
        regex_pattern = r"[.,:;<>\[\]`|\n*-]|\*\*|--|---"
    else:
        # Simply attempt to split results into sentences or phrases
        regex_pattern = r"[.,:;<>\[\]`|\n]"

    # Return a list of extracted summary items
    parsed_list = []
    for response_string in response:
        # Filter out empty or 1 character strings and strings without alphabetic characters
        if len(response_string) >= 2:
            substrings = re.split(regex_pattern, response_string)
            parsed_list.extend([s.strip() for s in substrings if s and re.search(r'[a-zA-Z]', s)])

    return parsed_list 


# Example usage and testing function
def demo_generator():
    """Test the summarization function with different parameters"""
    # Define generation parameters, prompt, and related arguments
    sample_kwargs = [
        dict(content=SAMPLE_TEXT, prompt="In 5 words or less, generate several concise and engaging titles", format="titles"),
        dict(content=SAMPLE_TEXT, prompt="In as few words as possible, list several tangentially related concepts", format="list"),
        dict(content=SAMPLE_TEXT, prompt="In as few words as possible, outline the following text", format="outline"),
        dict(content=SAMPLE_TEXT, prompt="Provide a list of 2-5 word summaries of the following text", format="list"),
        dict(content=SAMPLE_TEXT, prompt="Briefly summarize the following text", format="summary", tone='academic')
    ]

    print("\n== Basic Summary ===")
    print(f"Model: {DEFAULT_MODEL}")
    result = generate_summary(SAMPLE_TEXT, "Provide a short summary of the following text")
    print(result)

    print("\n=== With Custom Prompt ===")
    for kwargs in sample_kwargs:
        result = generate_summary(**kwargs)
        print(kwargs.get("prompt"), result)


if __name__ == "__main__":
    demo_generator()
