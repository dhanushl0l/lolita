import json
from dataclasses import asdict, dataclass
from typing import List

@dataclass
class Config:
    API_KEY: str
    MODEL: str
    BASE_URL: str
    ROLE: str
    REWRITE_ROLE: str
    REWRITE_PROMPT: str
    TEMPERATURE: float 
    TEMPERATURE_REWRITE: float 
    LOG_LEVEL: str


def load_config_from_json(filepath: str) -> Config:
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return Config(**data)
    except Exception as e:
        print(f"Failed to load config from {filepath}: {e}")
        return login_tty(filepath)

def login_tty(filepath: str) -> Config:
    api_key = input("Enter your API key: ").strip()
    config = get_default_config_with_api_key(api_key)
    
    try:
        with open(filepath, 'w') as f:
            json.dump(asdict(config), f, indent=4)
        print(f"Default config written to {filepath}")
    except Exception as write_error:
        print(f"Failed to write config to {filepath}: {write_error}")
    
    return config

def get_default_config_with_api_key(api_key: str) -> Config:
    return Config(
        API_KEY=api_key,
        MODEL="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        BASE_URL="https://api.together.xyz/v1",
        ROLE=(
            "Write in natural, fluent, and professional journalistic style. "
            "Every sentence should sound human-written and authentic. "
            "Avoid any robotic tone or AI-like phrasing. "
            "Add subtle personal voice or small relatable touches where appropriate. "
            "Vary sentence length and structure to create a natural reading rhythm. "
            "Use informal yet precise language instead of overly uniform or overly polished phrasing. "
            "Avoid strictly linear thought patterns—let the flow feel organic and conversational, "
            "as if an experienced human journalist is telling the story."
        ),
        REWRITE_ROLE=(
            "Refine the text so it reads like a skilled human journalist wrote it. "
            "Ensure smooth, varied sentence structures and natural word choice. "
            "Incorporate minor personal voice or relatable observations if it adds warmth and realism. "
            "Vary sentence length and rhythm deliberately to sound natural. "
            "Replace overly formal or repetitive phrases with more human-like expressions. "
            "Avoid predictable, mechanical patterns that could trigger AI detection tools."
        ),
        REWRITE_PROMPT=(
            "Rewrite the text so it feels authentically human-written, "
            "as if crafted by an experienced journalist. "
            "Add subtle personal or relatable touches when fitting. "
            "Vary sentence length and structure to create a natural rhythm. "
            "Use precise yet conversational language, avoiding robotic or overly polished phrasing. "
            "Keep all facts accurate and unchanged."
        ),
        TEMPERATURE=0.3,
        TEMPERATURE_REWRITE=0.7, 
        LOG_LEVEL="CRITICAL",
    )
