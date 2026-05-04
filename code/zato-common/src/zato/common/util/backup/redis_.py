# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# redis
import redis as redis_lib

# cryptography
from cryptography.fernet import Fernet

# Zato
from zato.common.json_internal import loads
from zato.common.util.backup.config import BackupConfig, redis_key_password, redis_key_settings

# ################################################################################################################################
# ################################################################################################################################

def get_redis_connection(config:'BackupConfig') -> 'redis_lib.Redis':
    out = redis_lib.Redis(
        host=config.redis_host,
        port=config.redis_port,
        db=config.redis_db,
        decode_responses=True,
    )
    return out

# ################################################################################################################################

def load_settings_from_redis(config:'BackupConfig', fernet_key:'str') -> 'dict':
    connection = get_redis_connection(config)
    raw = connection.get(redis_key_settings)

    if not raw:
        raise Exception('No backup settings found in Redis. Configure backup settings in the dashboard first.')

    if isinstance(fernet_key, str):
        fernet_key_bytes = fernet_key.encode('utf-8')
    else:
        fernet_key_bytes = fernet_key

    fernet = Fernet(fernet_key_bytes)

    if isinstance(raw, str):
        raw_bytes = raw.encode('utf-8')
    else:
        raw_bytes = raw

    decrypted = fernet.decrypt(raw_bytes)
    out = loads(decrypted.decode('utf-8'))
    return out

# ################################################################################################################################

def load_password_from_redis(config:'BackupConfig', fernet_key:'str') -> 'str':
    connection = get_redis_connection(config)
    raw = connection.get(redis_key_password)

    if not raw:
        raise Exception('No backup password found in Redis. Configure backup settings in the dashboard first.')

    if isinstance(fernet_key, str):
        fernet_key_bytes = fernet_key.encode('utf-8')
    else:
        fernet_key_bytes = fernet_key

    fernet = Fernet(fernet_key_bytes)

    if isinstance(raw, str):
        raw_bytes = raw.encode('utf-8')
    else:
        raw_bytes = raw

    decrypted = fernet.decrypt(raw_bytes)
    out = decrypted.decode('utf-8')
    return out

# ################################################################################################################################

def build_config_from_redis(
    fernet_key:'str',
    redis_host:'str'='localhost',
    redis_port:'int'=6379,
    redis_db:'int'=0,
    ) -> 'BackupConfig':

    config = BackupConfig()
    config.redis_host = redis_host
    config.redis_port = redis_port
    config.redis_db = redis_db

    settings = load_settings_from_redis(config, fernet_key)
    config.provider = settings['provider']
    config.bucket_name = settings['bucket_name']
    config.access_key = settings['access_key']
    config.secret_key = settings['secret_key']
    config.env_dir = settings['env_dir']

    return config

# ################################################################################################################################
# ################################################################################################################################
