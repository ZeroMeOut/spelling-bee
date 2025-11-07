import json
from typing import Dict
from pathlib import Path
from functools import lru_cache

## Same stuff as randomwords.py but for definitions
DEFINITIONS_CACHE_FILE = Path(__file__).parent / "wordnet_definitions.json"

def _read_words_from_file(path: Path) -> Dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"Definitions cache not found at: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object mapping words to definitions in the cache file")
    return {str(k): str(v) for k, v in data.items()}


@lru_cache(maxsize=1)
def _get_all_words() -> Dict[str, str]:
    return _read_words_from_file(DEFINITIONS_CACHE_FILE)

def define_words(words: list) -> Dict[str, str]:
    definitions = {}
    all_definitions = _get_all_words()
    for word in words:
        definitions[word] = all_definitions.get(word, "Definition not found.")
    return definitions
if __name__ == "__main__":
    sample_words = ["example"]
    defs = define_words(sample_words)
    for word, definition in defs.items():
        print(f"{word}: {definition}")  