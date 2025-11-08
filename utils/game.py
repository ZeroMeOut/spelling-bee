from typing import List, Dict, Optional, Any
from utils import TTS, randomwords, definition

## Idk if this is optimal but this will do for now
class SpellingBeeGame:
    target_words: List[str]
    definitions: Dict[str, str]
    lifes: int
    score: int
    current_target_word_index: int
    target_word: str

    def __init__(self):
        self.target_words = randomwords.get_random_words()

        self.definitions = {}
        self.lifes = 3
        self.score = 0
        self.current_target_word_index = 0
        self.target_word = self.target_words[self.current_target_word_index]

    def get_current_word_definition(self) -> str:
        if self.target_word not in self.definitions:
            self.definitions[self.target_word] = definition.define_words([self.target_word])[self.target_word]
        return self.definitions[self.target_word]

    def get_audio_bytes_of_current_word(self) -> bytes:
        return TTS.synthesize_text_to_wav_bytes(self.target_word)

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
        self.lifes = 3
        self.score = 0
        self.current_target_word_index = 0
        self.target_word = self.target_words[self.current_target_word_index]
