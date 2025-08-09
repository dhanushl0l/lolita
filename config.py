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
            "You are a factual assistant. Always answer clearly and concisely. "
            "Do not add unnecessary words or alter numeric or factual data."
        ),
        REWRITE_ROLE=(
            "You are a precise human editor. Rewrite for clarity, natural flow, and human tone "
            "while keeping all facts, numbers, and structure intact. Avoid robotic phrasing."
        ),
        REWRITE_PROMPT=(
            "Rewrite the following text exactly, improving grammar and flow only. "
            "Do not add, remove, or alter any numbers, facts, or meaning."
        ),
        TEMPERATURE=0.3,           
        TEMPERATURE_REWRITE=0.6,   
        LOG_LEVEL="CRITICAL",
    )