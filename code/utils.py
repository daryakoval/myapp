import time
from flask import g
from code.constans import LUA_SCRIPT_SET_KEYS, LUA_SCRIPT_GET_KEYS


def get_statistics(redis_client, logger):
    """ Get statistics from the database"""
    total_requests, total_processing_time = redis_client.eval(LUA_SCRIPT_GET_KEYS, 2, 'total_requests',
                                                              'total_processing_time')
    avg_processing_time_ns = total_processing_time // total_requests if total_requests > 0 else 0
    logger.debug(f'Get statistics: {total_requests=}, {total_processing_time=}.')
    return total_requests, avg_processing_time_ns


def update_statistics(redis_client, logger):
    """ Updates total requests number and total processing time """
    processing_time = int((time.time() - g.start_time) * 1e9)
    total_requests, total_processing_time = redis_client.eval(LUA_SCRIPT_SET_KEYS, 2, 'total_requests',
                                                              'total_processing_time', 1, processing_time)
    logger.debug(f'Updated statistics: {total_requests=}, {total_processing_time=}.')
