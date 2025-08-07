import json
from dataclasses import dataclass
from typing import List

@dataclass
class Config:
    API_KEY: str
    MODEL: str
    BASE_URL: str
    NUM_PASSES: int       
    TEMPERATURES: List[float] 
    LOG_LEVEL: str


def load_config_from_json(filepath: str) -> Config:
    with open(filepath, 'r') as f:
        data = json.load(f)
    return Config(**data)

