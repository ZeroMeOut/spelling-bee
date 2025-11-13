import json
import nltk
from pathlib import Path
from nltk.corpus import wordnet as wn

nltk.download('wordnet', quiet=True)
## Cache file for words and definitions
## Told Claude to make a cache function to avoid loading from wordnet every time

# Cache file paths - same as in your other modules
WORDS_CACHE_FILE = Path(__file__).parent / "wordnet_alpha_words.json"
DEFINITIONS_CACHE_FILE = Path(__file__).parent / "wordnet_definitions.json"

def create_wordnet_caches():
    """
    Creates cache files for WordNet words and definitions.
    Only includes alphabetic words (no dashes, numbers, etc.)
    and only words with definitions.
    Excludes proper nouns (names of people, places, etc.)
    """
    print("Creating word list from WordNet (this may take a few seconds)...")
    
    # Get all alphabetic words and filter out proper nouns
    all_words = []
    for word in wn.all_lemma_names():
        if not word.isalpha():
            continue
        
        # Check if any synset for this word is a proper noun
        synsets = wn.synsets(word)
        is_proper_noun = any(
            lemma.name()[0].isupper() 
            for synset in synsets 
            for lemma in synset.lemmas() ## Pylance screaming here but idc
        )
        
        if not is_proper_noun:
            all_words.append(word)
    
    print(f"Found {len(all_words)} alphabetic words (excluding proper nouns)")
    
    # Get first definition for each word
    print("Fetching definitions...")
    definitions = {}
    for i, word in enumerate(all_words):
        if i % 10000 == 0:
            print(f"  Processing word {i}/{len(all_words)}...")
        
        synsets = wn.synsets(word)
        if synsets:
            definitions[word] = [synset.definition() for synset in synsets[:3]] ## And here
    
    print(f"Found definitions for {len(definitions)} words")
    
    # Filter words to only those with definitions
    words_with_defs = [word for word in all_words if word in definitions]
    
    # Save words cache
    print(f"Saving {len(words_with_defs)} words to {WORDS_CACHE_FILE}...")
    with WORDS_CACHE_FILE.open('w', encoding='utf-8') as f:
        json.dump(words_with_defs, f, indent=2)
    
    # Save definitions cache
    print(f"Saving {len(definitions)} definitions to {DEFINITIONS_CACHE_FILE}...")
    with DEFINITIONS_CACHE_FILE.open('w', encoding='utf-8') as f:
        json.dump(definitions, f, indent=2)
    
    print("\n✓ Cache creation complete!")
    print(f"  Words: {len(words_with_defs)}")
    print(f"  Definitions: {len(definitions)}")

if __name__ == "__main__":
    try:
        create_wordnet_caches()
    except Exception as e:
        print(f"Error creating caches: {e}")
        import traceback
        traceback.print_exc()