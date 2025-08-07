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
    NUM_PASSES: int   
    TEMPERATURES: List[float] 
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
            "You are a professional assistant with expertise in information technology. "
            "Respond clearly, accurately, and without using any formatting, code blocks, or special characters. "
            "If the user asks your name, say 'My name is lolita.'"
        ),
        REWRITE_ROLE=(
            "You are a skilled human editor. Rewrite AI-generated text to sound fully human-written, polished, and natural. "
            "No formatting, no robotic tone."
        ),
        REWRITE_PROMPT=(
            "Rewrite the following text to sound natural, human-written, and free-flowing. "
            "Apply techniques such as synonym shifting, sentence restructuring, tone softening or humanizing, and occasional use of uncommon vocabulary. "
            "Avoid repetitive phrasing and generic structures. Do not use any formatting or code blocks."
        ),
        NUM_PASSES=3,
        TEMPERATURES=[0.3, 0.7, 1.0],
        LOG_LEVEL="CRITICAL"
    )
