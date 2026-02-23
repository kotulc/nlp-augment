import torch
import transformers

from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForCausalLM

from app.config import get_settings


# Extract constants from settings
settings = get_settings()
DEFAULT_MODEL = settings.model.language_model
DEFAULT_KWARGS = settings.model.transformers.model_dump()


@lru_cache(maxsize=1)
def get_generative_model():
    """Return the text generation pipeline or a mock function in debug mode"""
    # Initialize the content generation model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(DEFAULT_MODEL)
    model = AutoModelForCausalLM.from_pretrained(DEFAULT_MODEL, torch_dtype=torch.bfloat16, device_map="auto")
    generator = transformers.pipeline("text-generation", model=model, tokenizer=tokenizer)
    default_kwargs = DEFAULT_KWARGS.copy()

    def get_model_inference(content: str, **kwargs) -> list:
        """Return generated text from the model"""
        if len(kwargs):
            model_kwargs = default_kwargs.copy()
            model_kwargs.update(kwargs)
        else:
            model_kwargs = default_kwargs

        # For each returned text sequence extract the generated content
        sequences = generator(content, do_sample=True, return_full_text=False, **model_kwargs)
        return [sequence["generated_text"] for sequence in sequences]

    return get_model_inference
