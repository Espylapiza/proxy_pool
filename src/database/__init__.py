from redis import StrictRedis
from settings import DB_PORT, DB_NUM, DB_PASSWD, DB_BASE_PROXY_EXPIRE, DB_PROXY_EXPIRE

_redis = StrictRedis(host="localhost", port=DB_PORT, db=DB_NUM, password=DB_PASSWD)
_redis.expire("base_proxy", DB_BASE_PROXY_EXPIRE)
_redis.expire("proxy", DB_PROXY_EXPIRE)


def base_proxy_add(proxy):
    return _redis.sadd("base_proxy", proxy)


def base_proxy_rem(proxy):
    return _redis.srem("base_proxy", proxy)


def base_proxy_rand(num=None):
    return _redis.srandmember("base_proxy", num)


def base_proxy_exists(proxy):
    return _redis.sismember("base_proxy", proxy)


def add(proxy):
    return _redis.sadd("proxy", proxy)


def rem(proxy):
    return _redis.srem("proxy", proxy)


def rand():
    return _redis.srandmember("proxy")


def exists(proxy):
    return _redis.sismember("proxy", proxy)
