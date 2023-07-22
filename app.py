from flask import Flask, request, jsonify, make_response, Response, g
from flask_caching import Cache
import time
import redis
import logging
from constans import CACHE_HEADER, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, \
    CACHE_TYPE, CACHE_REDIS_URL, REDIS_PORT, WORDS_CLEAN_PATH
from words_db import WordsDatabase
from utils import update_statistics, get_statistics

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.config['CACHE_TYPE'] = CACHE_TYPE
app.config['CACHE_REDIS_URL'] = CACHE_REDIS_URL

# TODO: maybe move to Words DB
cache = Cache(app)

words_database = WordsDatabase(path=WORDS_CLEAN_PATH)

redis_client = redis.StrictRedis(host='localhost', port=REDIS_PORT, db=0)
redis_client.set('total_requests', 0)
redis_client.set('total_processing_time_key', 0)


@app.after_request
def after_request_tasks(response):
    """ Update Statistics and Cache """
    current_request = request
    if request.endpoint == 'find_similar_words':
        update_statistics(redis_client=redis_client, app=app)
        words_database.update_similar_cache(current_request=current_request, response=response,
                                            cache=cache, logger=app.logger)

    return response


@app.route('/api/v1/similar', methods=['GET'])
def find_similar_words() -> Response:
    """ Returns similar words to the given word"""
    headers = {}
    word = request.args.get('word', '').lower()

    if not word or not word.isalpha():
        return make_response(jsonify({"error": "Invalid word. Please provide a valid alphabetic word."}),
                             HTTP_400_BAD_REQUEST)

    start_time = time.time()

    similar_words, cache_val = words_database.get_similar_words(word, cache)

    headers[CACHE_HEADER] = cache_val
    g.process_time = int((time.time() - start_time) * 1e9)
    return make_response(jsonify({"similar": similar_words}), HTTP_200_OK, headers)


@app.route('/api/v1/stats', methods=['GET'])
def get_stats() -> Response:
    """ Returns statistics - total requests and average processing time"""
    total_requests, avg_processing_time_ns = get_statistics(redis_client)

    return make_response(
        jsonify({
            "totalWords": len(words_database),
            "totalRequests": total_requests,
            "avgProcessingTimeNs": avg_processing_time_ns,
        }), HTTP_200_OK)


@app.errorhandler(HTTP_404_NOT_FOUND)
def not_found_error(error) -> Response:
    """ Handles Not Found Errors """
    response_data = {'error': 'Endpoint not found',
                     'description': 'Available endpoints: `/api/v1/similar` `/api/v1/stats`'}
    return make_response(jsonify(response_data), HTTP_404_NOT_FOUND)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
