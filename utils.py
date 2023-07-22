from flask import g, Response, Request
from constans import LUA_SCRIPT_SET_KEYS, CACHE_HEADER, LUA_SCRIPT_GET_KEYS


def get_statistics(redis_client):
    """ Get statistics from the database"""
    total_requests, total_processing_time = redis_client.eval(LUA_SCRIPT_GET_KEYS, 2, 'total_requests',
                                                              'total_processing_time')
    avg_processing_time_ns = total_processing_time // total_requests if total_requests > 0 else 0
    return total_requests, avg_processing_time_ns


def update_statistics(redis_client, app):
    """ Updates total requests number and total processing time """
    processing_time = g.process_time
    total_requests, total_processing_time = redis_client.eval(LUA_SCRIPT_SET_KEYS, 2, 'total_requests',
                                                              'total_processing_time', 1, processing_time)
    app.logger.info(f'Updated statistics: {total_requests=}, {total_processing_time=}')

