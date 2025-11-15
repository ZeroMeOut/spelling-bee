import json
import nltk
from pathlib import Path
from nltk.corpus import wordnet as wn
from nltk.corpus import webtext, brown, reuters
from nltk.corpus import stopwords
from nltk import FreqDist

nltk.download("wordnet", quiet=True)
nltk.download("webtext", quiet=True)
nltk.download("brown", quiet=True)
nltk.download("reuters", quiet=True)
nltk.download("stopwords", quiet=True)

# Cache file paths
WORDS_CACHE_FILE = Path(__file__).parent / "common_words_10k.json"
DEFINITIONS_CACHE_FILE = Path(__file__).parent / "common_word_definitions.json"


def create_common_word_caches(top_n=10000, min_length=5):
    """
    Creates cache files for the top `top_n` most common alphabetic words
    that are at least `min_length` characters long, excluding stopwords,
    along with their WordNet definitions.
    
    Uses multiple corpora (WebText, Brown, Reuters) for better coverage.
    """

    print(f"Extracting most common {top_n} words (≥{min_length} chars, no stopwords)...")

    # Get English stopwords
    stop_words = set(stopwords.words('english'))
    print(f"Loaded {len(stop_words)} stopwords to filter out")

    # Collect words from multiple corpora
    all_words = []
    
    print("Loading WebText corpus...")
    all_words.extend([w.lower() for w in webtext.words() if w.isalpha() and w.islower()])
    
    print("Loading Brown corpus...")
    all_words.extend([w.lower() for w in brown.words() if w.isalpha() and w.islower()])
    
    print("Loading Reuters corpus...")
    all_words.extend([w.lower() for w in reuters.words() if w.isalpha() and w.islower()])
    
    print(f"Total words collected: {len(all_words)}")

    # Filter: length >= min_length and not a stopword
    filtered_words = [
        w for w in all_words 
        if len(w) >= min_length and w not in stop_words
    ]
    print(f"After filtering: {len(filtered_words)} words")

    # Calculate frequency distribution
    freq = FreqDist(filtered_words)

    # Take the top N words
    common_words = [word for word, _ in freq.most_common(top_n)]
    print(f"Collected {len(common_words)} candidate common words")

    # Fetch definitions
    print("Fetching WordNet definitions...")

    definitions = {}
    for i, word in enumerate(common_words):
        if i % 1000 == 0:
            print(f"  Processing {i}/{len(common_words)}...")

        synsets = wn.synsets(word)
        if synsets:
            # Store up to the first 3 definitions
            definitions[word] = [s.definition() for s in synsets[:3]]

    print(f"Definitions found for {len(definitions)} of {len(common_words)} words")

    # Keep only words that have definitions
    final_words = [w for w in common_words if w in definitions]

    # Save words cache
    print(f"Saving {len(final_words)} words to {WORDS_CACHE_FILE}...")
    with WORDS_CACHE_FILE.open("w", encoding="utf-8") as f:
        json.dump(final_words, f, indent=2)

    # Save definitions cache
    print(f"Saving {len(definitions)} definitions to {DEFINITIONS_CACHE_FILE}...")
    with DEFINITIONS_CACHE_FILE.open("w", encoding="utf-8") as f:
        json.dump(definitions, f, indent=2)

    print("\n✓ Cache creation complete!")
    print(f"  Words saved: {len(final_words)}")
    print(f"  Definitions saved: {len(definitions)}")
    print(f"  Minimum word length: {min_length} characters")
    print(f"  Stopwords excluded: {len(stop_words)}")


if __name__ == "__main__":
    try:
        create_common_word_caches(top_n=10000, min_length=5)
    except Exception as e:
        print(f"Error creating caches: {e}")
        import traceback
        traceback.print_exc()