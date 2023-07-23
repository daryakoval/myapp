import unittest
from collections import defaultdict
from unittest.mock import MagicMock
from code.words_db import WordsDatabase
import tempfile
from code.utils import get_statistics, update_statistics
from flask import Flask, g


class TestWordsDatabase(unittest.TestCase):
    def setUp(self):
        self.words_set = {"stressed", "destress", "desserts"}
        self.words_db = defaultdict(list)
        self.words_db["d1e2r1s3t1"] = ["stressed", "destress", "desserts"]
        self.logger = MagicMock()

        tmp_file = tempfile.NamedTemporaryFile()

        self.db = WordsDatabase(path=tmp_file.name, logger=self.logger)
        self.db.words_set = self.words_set
        self.db.words_db = self.words_db

    def test_get_similar_words(self):
        word = "stressed"
        expected_similar_words = ["destress", "desserts"]
        similar_words = self.db.get_similar_words(word)
        self.assertEqual(similar_words, expected_similar_words)

        word_not_in_db = "banana"
        similar_words_not_in_db = self.db.get_similar_words(word_not_in_db)
        self.assertEqual(similar_words_not_in_db, [])


class TestStatisticsFunctions(unittest.TestCase):
    def setUp(self):
        self.redis_client = MagicMock()
        self.logger = MagicMock()
        self.app = Flask(__name__)

    def test_get_statistics(self):
        self.redis_client.eval.return_value = (10, 5000)  # total_requests, total_processing_time

        total_requests, avg_processing_time_ns = get_statistics(self.redis_client, self.logger)

        self.assertEqual(total_requests, 10)
        self.assertEqual(avg_processing_time_ns, 500)

    def test_update_statistics(self):
        self.redis_client.eval.return_value = (11, 5500)  # total_requests, total_processing_time

        with self.app.test_request_context():
            g.start_time = 1627465957
            update_statistics(self.redis_client, self.logger)
        self.logger.debug.assert_called_with('Updated statistics: total_requests=11, total_processing_time=5500.')


if __name__ == '__main__':
    unittest.main()
