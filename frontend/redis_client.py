import redis

redis_client = redis.StrictRedis(
    host="localhost",  # Địa chỉ Redis
    port=6379,         # Cổng Redis
    decode_responses=True  # Giải mã dữ liệu về string
)