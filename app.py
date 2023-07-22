import functools
from typing import List, Callable
from flask import Flask, request, jsonify, make_response, Response, g
from flask_caching import Cache
import itertools
import time
import redis
import logging
from collections import Counter


app = Flask(__name__)
app.logger.setLevel(logging.INFO)
# cache = Cache(app, config={'CACHE_TYPE': 'simple'})
# Configure Redis as the caching backend
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'  # Replace with your Redis server URL

# Initialize the cache
cache = Cache(app)

with open('words_clean.txt', 'r') as f:
    words_db = set(f.read().splitlines())

total_words = len(words_db)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
redis_client.set('total_requests', 0)
redis_client.set('total_processing_time_key', 0)

CACHE_HEADER = 'X-Cache'
HTTP_200_OK = 200
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_404_NOT_FOUND = 404
LUA_SCRIPT_SET_KEYS = """
local total_requests_key = KEYS[1]
local total_processing_time_key = KEYS[2]
local increment = tonumber(ARGV[1])
local processing_time = tonumber(ARGV[2])

local total_requests = tonumber(redis.call('GET', total_requests_key) or 0)
local total_processing_time = tonumber(redis.call('GET', total_processing_time_key) or 0)

total_requests = total_requests + increment
total_processing_time = total_processing_time + processing_time

redis.call('SET', total_requests_key, total_requests)
redis.call('SET', total_processing_time_key, total_processing_time)

return {total_requests, total_processing_time}
"""
LUA_SCRIPT_GET_KEYS = """
local total_requests_key = KEYS[1]
local total_processing_time_key = KEYS[2]

local total_requests = tonumber(redis.call('GET', total_requests_key) or 0)
local total_processing_time = tonumber(redis.call('GET', total_processing_time_key) or 0)

return {total_requests, total_processing_time}
"""


def update_statistics(response):
    """ Updates total requests number and total processing time"""
    processing_time = int(response.headers.get('X-Runtime', 0))
    total_requests, total_processing_time = redis_client.eval(LUA_SCRIPT_SET_KEYS, 2, 'total_requests',
                                                              'total_processing_time', 1, processing_time)
    app.logger.info(f'Updated totals: {total_requests=}, {total_processing_time=}')


def update_similar_cache(current_request, response: Response):
    if not response.headers[CACHE_HEADER]:
        word = current_request.args.get('word', '').lower()
        count = g.count
        similar_words = response.json().get('similar', [])
        similar_words.append(word)
        cache.set(list(count.items()), similar_words, timeout=60)
        app.logger.info(f'Updated cache for: {count}, {similar_words=}.')


@app.after_request
def after_request_tasks(response):
    current_request = request
    if request.endpoint == 'find_similar_words':
        update_statistics(response)
        update_similar_cache(current_request, response)

    return response


# TODO???
def validate_request(f: Callable) -> Callable:
    @functools.wraps(f)
    def validate_request_headers_and_auth(*args, **kwargs):
        """
        function for HTTP requests to validate authentication and headers.
        """
        request_headers = request.headers
        credentials = request.authorization
        custom_header = request_headers.get('X-Custom')

        if credentials:
            return {'title': 'Authorization failed'}, HTTP_401_UNAUTHORIZED

        return f(*args, **kwargs)

    return validate_request_headers_and_auth


def get_similar_words(word: str) -> List[str]:
    perms = set(''.join(p) for p in itertools.permutations(word))
    similar_words = sorted(w for w in perms if w in words_db and w != word)
    return similar_words


@app.route('/api/v1/similar', methods=['GET'])
def find_similar_words() -> Response:

    headers = {CACHE_HEADER: 0}
    word = request.args.get('word', '').lower()

    if not word or not word.isalpha():
        return make_response(jsonify({"error": "Invalid word. Please provide a valid alphabetic word."}),
                             HTTP_400_BAD_REQUEST)

    count = Counter(word)
    if similar_words := cache.get(count):
        similar_words.delete(word)
        headers[CACHE_HEADER] = 1
    else:
        similar_words = get_similar_words(word)
    similar_words = get_similar_words(word)
    return make_response(jsonify({"similar": similar_words}), HTTP_200_OK, headers)


@app.route('/api/v1/stats', methods=['GET'])
def get_stats() -> Response:
    total_requests, total_processing_time = redis_client.eval(LUA_SCRIPT_GET_KEYS, 2, 'total_requests',
                                                              'total_processing_time')
    avg_processing_time_ns = total_processing_time // total_requests if total_requests > 0 else 0

    return make_response(jsonify({
        "totalWords": total_words,
        "totalRequests": total_requests,
        "avgProcessingTimeNs": avg_processing_time_ns,
    }), HTTP_200_OK)


@app.errorhandler(HTTP_404_NOT_FOUND)
def not_found_error(error) -> Response:
    response_data = {'error': 'Endpoint not found',
                     'description': 'Available endpoints: `/api/v1/similar` `/api/v1/stats`'}
    return make_response(jsonify(response_data), HTTP_404_NOT_FOUND)


if __name__ == '__main__':
    app.run(host='0.0.0.0')

