from typing import Set
import itertools
from collections import Counter
from constans import CACHE_HIT, CACHE_MISS, CACHE_HEADER
from flask import Response, g, Request
from flask_caching import Cache


class WordsDatabase:
    def __init__(self, path: str, logger):
        self.words_set = self._load_txt(path=path)
        self.logger = logger

    def __len__(self):
        return len(self.words_set)

    def __iter__(self):
        return self.words_set

    @staticmethod
    def _load_txt(path: str) -> Set[str]:
        with open(path, 'r') as f:
            words_set = set(f.read().splitlines())
        return words_set

    def get_similar_words(self, word: str, cache: Cache):
        """Get similar words from the database, try get from cache if not present get from the db"""
        g.count_str = ''.join(f'{letter}{count}' for letter, count in sorted(Counter(word).items()))

        if similar_words := cache.get(g.count_str):
            similar_words.remove(word)
            return similar_words, CACHE_HIT
        else:
            perms = set(''.join(p) for p in itertools.permutations(word))
            similar_words = sorted(w for w in perms if w in self.words_set and w != word)
            return similar_words, CACHE_MISS

    def update_similar_cache(self, current_request: Request, response: Response, cache: Cache):
        """ Updates the cache for similar words search """
        if not int(response.headers[CACHE_HEADER]):
            word = current_request.args.get('word', '').lower()
            similar_words = response.json.get('similar', [])
            similar_words.append(word)
            cache.set(g.count_str, similar_words, timeout=180)
            self.logger.info(f'Updated cache for: {g.count_str}, {similar_words=}.')