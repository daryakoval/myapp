from flask import Flask, request, jsonify, make_response, Response, g
import time
import redis
import logging
from code.constans import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, REDIS_PORT, WORDS_CLEAN_PATH, HOST
from code.words_db import WordsDatabase
from code.utils import update_statistics, get_statistics

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

words_database = WordsDatabase(path=WORDS_CLEAN_PATH, logger=app.logger)

redis_client = redis.StrictRedis(host=HOST, port=REDIS_PORT, db=0)
redis_client.set('total_requests', 0)
redis_client.set('total_processing_time_key', 0)


@app.before_request
def before_request_tasks():
    """ Setting the request start time """
    g.start_time = time.time()


@app.after_request
def after_request_tasks(response):
    """ Update Statistics """
    if request.endpoint == 'get_similar':
        update_statistics(redis_client=redis_client, logger=app.logger)
    return response


@app.route('/api/v1/similar', methods=['GET'])
def get_similar() -> Response:
    """ Returns similar words to the given word"""
    word = request.args.get('word', '').lower()

    if not word or not word.isalpha():
        return make_response(jsonify({"error": "Invalid word. Please provide a valid alphabetic word."}),
                             HTTP_400_BAD_REQUEST)

    similar_words = words_database.get_similar_words(word)
    return make_response(jsonify({"similar": similar_words}), HTTP_200_OK)


@app.route('/api/v1/stats', methods=['GET'])
def get_stats() -> Response:
    """ Returns statistics - total requests and average processing time"""
    total_requests, avg_processing_time_ns = get_statistics(redis_client=redis_client, logger=app.logger)

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
