from collections import Counter, defaultdict
from typing import Set, List


class WordsDatabase:
    def __init__(self, path: str, logger):
        self.words_db, self.words_set = self._load_db(path=path)
        self.logger = logger

    def __len__(self) -> int:
        return len(self.words_set)

    @staticmethod
    def _load_db(path: str) -> tuple[defaultdict[str, List[str]], Set[str]]:
        with open(path, 'r') as f:
            words_set = set(f.read().splitlines())
        db = defaultdict(lambda: [])
        for word in words_set:
            count_str = ''.join(f'{letter}{count}' for letter, count in sorted(Counter(word).items()))
            db[count_str].append(word)
        return db, words_set

    def get_similar_words(self, word: str) -> List[str]:
        """Get similar words from the database"""
        count_str = ''.join(f'{letter}{count}' for letter, count in sorted(Counter(word).items()))
        all_similar_words = self.words_db.get(count_str, [])
        self.logger.debug(f'Word: [{word}]. All similar words are {all_similar_words}.')
        similar_words = list(filter(lambda e: e != word, all_similar_words))
        return similar_words
