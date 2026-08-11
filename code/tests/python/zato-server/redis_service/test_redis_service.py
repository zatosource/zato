# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.redis_env import get_redis_conn_from_values, get_redis_values_from_section
from zato.server.connection.cache import CacheAPI

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from redis import Redis
    from zato.common.typing_ import anydict

    anydict = anydict
    Redis = Redis

# ################################################################################################################################
# ################################################################################################################################

class _TestConfigManager:
    """ A minimal stand-in for ConfigManager - a service reads self.redis from cache_api.redis.
    """
    def __init__(self, cache_api:'CacheAPI') -> 'None':
        self.cache_api = cache_api

# ################################################################################################################################
# ################################################################################################################################

def _get_service_redis(redis_server:'anydict') -> 'Redis':
    """ Builds the Redis client the way the server does - from a [redis]-style section
    through zato.common.redis_env - and returns it the way a service gets self.redis.
    """
    section = {
        'host': redis_server['host'],
        'port': redis_server['port'],
    }

    values = get_redis_values_from_section(section)
    client = get_redis_conn_from_values(values, decode_responses=True)

    config_manager = _TestConfigManager(CacheAPI(client))

    # The same attribute access the Service class performs
    out = config_manager.cache_api.redis
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_redis_round_trip(redis_server:'anydict') -> 'None':
    """ A set, get and delete round trip over the same client a service sees as self.redis.
    """
    redis = _get_service_redis(redis_server)

    key = 'test.redis.service.' + CryptoManager.generate_hex_string()
    value = 'test-value-' + CryptoManager.generate_hex_string()

    # Store the value ..
    _ = redis.set(key, value)

    # .. read it back ..
    read_value = redis.get(key)
    assert read_value == value, f'Expected `{value}`, got: {read_value}'

    # .. delete it ..
    _ = redis.delete(key)

    # .. and confirm it is gone.
    read_value = redis.get(key)
    assert read_value is None, f'Expected the key to be gone, got: {read_value}'

# ################################################################################################################################

def test_redis_data_structures(redis_server:'anydict') -> 'None':
    """ Lists and hashes work over the same client, the way services use self.redis directly.
    """
    redis = _get_service_redis(redis_server)

    list_key = 'test.redis.service.list.' + CryptoManager.generate_hex_string()
    hash_key = 'test.redis.service.hash.' + CryptoManager.generate_hex_string()

    # A list keeps its order ..
    _ = redis.rpush(list_key, 'first', 'second', 'third')

    list_values = redis.lrange(list_key, 0, -1)
    assert list_values == ['first', 'second', 'third'], f'Unexpected list contents: {list_values}'

    # .. and a hash keeps its fields.
    _ = redis.hset(hash_key, 'field-name', 'field-value')

    hash_value = redis.hget(hash_key, 'field-name')
    assert hash_value == 'field-value', f'Unexpected hash value: {hash_value}'

    _ = redis.delete(list_key, hash_key)

# ################################################################################################################################

def test_kvdb_and_cache_are_aliases(redis_server:'anydict') -> 'None':
    """ The kvdb and cache attributes are plain assignments of the redis one,
    mirroring how the Service class wires them.
    """
    redis = _get_service_redis(redis_server)

    # The same three assignments the Service class makes
    kvdb = redis
    cache = redis

    assert kvdb is redis
    assert cache is redis

    # A value written through one alias is visible through the others
    key = 'test.redis.service.alias.' + CryptoManager.generate_hex_string()
    value = 'alias-value-' + CryptoManager.generate_hex_string()

    _ = kvdb.set(key, value)

    read_value = cache.get(key)
    assert read_value == value, f'Expected `{value}`, got: {read_value}'

    _ = redis.delete(key)

# ################################################################################################################################
# ################################################################################################################################
