# ======== PATHS ========
WORDS_CLEAN_PATH = 'words_clean.txt'
HOST = 'localhost'

# ======== RETURN CODES ========
HTTP_200_OK = 200
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_404_NOT_FOUND = 404

# ======== CACHE & REDIS RELATED ========
CACHE_TYPE = 'redis'
REDIS_PORT = 6379
CACHE_REDIS_URL = f'redis://localhost:{REDIS_PORT}/0'

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
