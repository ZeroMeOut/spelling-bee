from typing import List, Dict, Any
from utils import randomwords, definition, S3toBytes

## Idk if this is optimal but this will do for now
class SpellingBeeGame:
    target_words: List[str]
    definitions: Dict[str, List[str]]
    definition_indices: Dict[str, int]
    lifes: int
    score: int
    current_target_word_index: int
    target_word: str

    def __init__(self):
        self.target_words = randomwords.get_random_words()
        self.definitions = {}
        self.definition_indices = {}
        self.lifes = 3
        self.score = 0
        self.current_target_word_index = 0
        self.target_word = self.target_words[self.current_target_word_index]

    def _ensure_definition_indices(self):
        if not hasattr(self, 'definition_indices'):
            self.definition_indices = {}

    def get_current_word_definition(self) -> str:
        self._ensure_definition_indices()
        
        if self.target_word not in self.definitions:
            defs = definition.define_words([self.target_word])[self.target_word]
            if isinstance(defs, str):
                import ast
                try:
                    defs = ast.literal_eval(defs)
                except:
                    defs = [defs]
            self.definitions[self.target_word] = defs if isinstance(defs, list) else [defs]
            self.definition_indices[self.target_word] = 0
        
        if self.target_word not in self.definition_indices:
            self.definition_indices[self.target_word] = 0
        
        defs_list = self.definitions[self.target_word]
        current_idx = self.definition_indices[self.target_word]
        return defs_list[current_idx]
    
    def cycle_definition(self) -> str:
        self._ensure_definition_indices()
        
        if self.target_word not in self.definitions:
            return self.get_current_word_definition()
        
        defs_list = self.definitions[self.target_word]
        if len(defs_list) > 1:
            if self.target_word not in self.definition_indices:
                self.definition_indices[self.target_word] = 0
            
            self.definition_indices[self.target_word] = (
                self.definition_indices[self.target_word] + 1
            ) % len(defs_list)
        
        return self.get_current_word_definition()
    
    def get_definition_count(self) -> int:
        self._ensure_definition_indices()
        
        if self.target_word not in self.definitions:
            self.get_current_word_definition()
        
        defs_list = self.definitions.get(self.target_word, [])
        return len(defs_list)

    def get_audio_bytes_of_current_word(self) -> bytes:
        return S3toBytes.get_presigned_audio_bytes(self.target_word)

    def one_game_session(self, word: str) -> Dict[str, Any]:
        if word.lower() == self.target_word.lower():
            self.score += 1
            self.current_target_word_index += 1

            if self.current_target_word_index >= len(self.target_words):
                return {
                    "correct": True,
                    "score": self.score,
                    "lifes": self.lifes,
                    "target_word": self.target_word,
                    "end_game": True,
                }
            else:
                self.target_word = self.target_words[self.current_target_word_index]
                return {
                    "correct": True,
                    "score": self.score,
                    "lifes": self.lifes,
                    "target_word": self.target_word,
                    "end_game": False,
                }
        else:
            self.lifes -= 1
            return {
                "correct": False,
                "score": self.score,
                "lifes": self.lifes,
                "target_word": self.target_word if self.lifes <= 0 else None,
                "end_game": self.lifes <= 0,
            }

    def reset_game(self) -> None:
        self.target_words = randomwords.get_random_words()
        self.definitions = {}
        self.definition_indices = {}
        self.lifes = 3
        self.score = 0
        self.current_target_word_index = 0
        self.target_word = self.target_words[self.current_target_word_index]
