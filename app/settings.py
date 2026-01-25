import tomllib
import yaml

from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Define path to local transformers config file
TRANSFORMERS_PATH = Path("app/transformers.yaml")

# Define some fallback default headings in case the local config is missing
HEADING_PROMPTS = {
    "title": [
        "In 5 words or less, list multiple concise and engaging titles for the following text",
        "In as few words as possible, list several short, attention grabbing titles for the following text",
        "In as few words as possible, list various potential headlines related to the following text",
        "Rephrase the following terms into a list of short pithy titles"
    ],
    "subtitle": [
        "state several terse and succinct statements describing the following text",
        "list several short, attention grabbing captions for the following text",
        "In 8 words or less, list various subtitles for the following text",
        "Rephrase the following statements into a list of short pithy subtitles"
    ],
    "description": [
        "Generate many short concise single-sentence descriptions of the following text",
        "List several brief, thematic explanations of the following text",
        "List multiple varied summaries of the following text",
        "Rephrase the following statements into a list of concise summaries"
    ],
}

# Define several different tag generation prompts for variety
TAGS_PROMPTS = [
    "With as few words as possible, list several related trending topics from the following text",
    "With as few words as possible, list high level ideas and themes of the following text",
    "With as few words as possible, list several tangentially related concepts to the following text",
]


# Define database settings class
class DatabaseSettings(BaseSettings):
    """Define database connection settings"""
    file: str = "sql_app.db"
    url: str = "sqlite:///./sql_app.db"
    connect_args: dict = {"check_same_thread": False}

# Define Transformers generation settings 
class TransformersSettings(BaseSettings):
    """Define default keyword arguments for Transformers generation"""
    max_new_tokens: int = 128
    num_return_sequences: int = 1
    repetition_penalty: float = 1.2
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50

# Define function default argument settings yaml class
class ModelSettings(BaseSettings):
    """Define default keyword argument for core functions"""
    # Also tested with "microsoft/Phi-4-mini-instruct" 
    language_model: str = "google/gemma-3-1b-it"
    transformers: TransformersSettings = Field(default_factory=TransformersSettings)
    prompt_template: str = Field(default="{prompt}:\n\nText: {content}\n\n{delimiter}") 
    title_prompts: list[str] = Field(default=HEADING_PROMPTS["title"], min_length=4)
    subtitle_prompts: list[str] = Field(default=HEADING_PROMPTS["subtitle"], min_length=4)
    description_prompts: list[str] = Field(default=HEADING_PROMPTS["description"], min_length=4)
    tag_prompts: list[str] = Field(default=TAGS_PROMPTS, min_length=3)
    
    @classmethod
    def from_yaml(cls, path: str):
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

# Define the application-level settings class which loads values from a .env file
class ApplicationSettings(BaseSettings):
    """Define all application-level settings"""
    # Load variables from a .env file if it exists
    model_config = SettingsConfigDict(env_file='.env')
    name: str = "NLP Service"

    with open(Path(__file__).parent.parent / "pyproject.toml", "rb") as f:
        version: str = tomllib.load(f)["project"]["version"]
    
    # Get database settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    
    # Load user transformers configurations if they exist
    if TRANSFORMERS_PATH.exists():
        # If the defaults.yaml file exists, load default settings from it
        model: ModelSettings = ModelSettings.from_yaml(TRANSFORMERS_PATH)
    else:
        model: ModelSettings = Field(default_factory=ModelSettings)


@lru_cache()
def get_settings() -> ApplicationSettings:
    return ApplicationSettings()
