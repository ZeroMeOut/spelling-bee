import json
import random
from typing import List
from pathlib import Path
from functools import lru_cache

## At first I was using an api (see the txt file) but now I am switching to nltk's wordnet corpus
## See cache_file.py for caching implementation
## Man lru_cache is stupid fast og
WORDS_CACHE_FILE = Path(__file__).parent / "wordnet_alpha_words.json"


def _read_words_from_file(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Words cache not found at: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of words in the cache file")
    return [str(w) for w in data]


@lru_cache(maxsize=1)
def _get_all_words() -> List[str]:
    return _read_words_from_file(WORDS_CACHE_FILE)

def get_random_words(n: int = 1000) -> List[str]:
    all_words = _get_all_words()
    n = max(0, min(n, len(all_words)))
    if n == 0:
        return []
    sample = random.sample(all_words, n)
    return sorted(sample, key=len)


if __name__ == "__main__":
    print(get_random_words(100))


