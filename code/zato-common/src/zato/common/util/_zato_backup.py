"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import argparse
import io
import os
import sys
import tarfile
from datetime import datetime, timezone
from getpass import getpass
from logging import getLogger
from traceback import format_exc

import redis
from argon2.low_level import Type, hash_secret_raw
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from libcloud.storage.providers import get_driver
from libcloud.storage.types import Provider
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

enc_extension = '.tar.gz.enc'
backup_prefix = 'zato-backup-'

redis_key_settings = 'zato:backup:settings'
redis_key_schedule = 'zato:backup:schedule'
redis_key_password = 'zato:backup:password'

kdf_salt_len = 16
aes_key_len = 32
aes_nonce_len = 12
argon2_time_cost = 3
argon2_memory_cost = 65536
argon2_parallelism = 4

provider_map = {
    'aws': Provider.S3,
    'gcs': Provider.GOOGLE_STORAGE,
    'azure': Provider.AZURE_BLOBS,
}

exclude_dirs = {
    'config/auto-generated',
    '__pycache__',
    '.env',
    '.vscode',
    '.git',
    'logs',
}

exclude_files = {
    '.env',
}

# ################################################################################################################################
# ################################################################################################################################

class BackupConfig:

    def __init__(self):
        self.provider = ''
        self.bucket_name = ''
        self.access_key = ''
        self.secret_key = ''
        self.env_dir = ''
        self.redis_host = 'localhost'
        self.redis_port = 6379
        self.redis_db = 0

# ################################################################################################################################
# ################################################################################################################################

def _derive_key(password, salt):
    secret = password.encode('utf-8')
    return hash_secret_raw(
        secret=secret,
        salt=salt,
        time_cost=argon2_time_cost,
        memory_cost=argon2_memory_cost,
        parallelism=argon2_parallelism,
        hash_len=aes_key_len,
        type=Type.ID,
    )

# ################################################################################################################################

def _encrypt_archive(archive_bytes, password):
    salt = os.urandom(kdf_salt_len)
    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(aes_nonce_len)
    ciphertext = aesgcm.encrypt(nonce, archive_bytes, None)
    result = salt + nonce + ciphertext
    return result

# ################################################################################################################################

def _should_exclude(path, rel_path):
    parts = rel_path.split(os.sep)

    for part in parts:
        if part in exclude_dirs:
            return True

    basename = os.path.basename(path)
    if basename in exclude_files:
        return True

    return False

# ################################################################################################################################

def _create_tar_gz(env_dir):
    buf = io.BytesIO()

    with tarfile.open(fileobj=buf, mode='w:gz') as tar:
        for dirpath, dirnames, filenames in os.walk(env_dir):

            rel_dir = os.path.relpath(dirpath, env_dir)
            if rel_dir == '.':
                rel_dir = ''

            if _should_exclude(dirpath, rel_dir):
                dirnames.clear()
                continue

            for filename in filenames:
                full_path = os.path.join(dirpath, filename)

                if rel_dir:
                    rel_path = os.path.join(rel_dir, filename)
                else:
                    rel_path = filename

                if _should_exclude(full_path, rel_path):
                    continue

                tar.add(full_path, arcname=rel_path)

    result = buf.getvalue()
    return result

# ################################################################################################################################

def _get_libcloud_driver(config):
    provider_const = provider_map[config.provider]
    driver_cls = get_driver(provider_const)
    driver = driver_cls(config.access_key, config.secret_key)
    return driver

# ################################################################################################################################

def _upload_to_cloud(config, object_name, encrypted_data):
    driver = _get_libcloud_driver(config)
    container = driver.get_container(config.bucket_name)
    stream = io.BytesIO(encrypted_data)
    driver.upload_object_via_stream(stream, container, object_name)

# ################################################################################################################################

def _get_redis_connection(config):
    conn = redis.Redis(
        host=config.redis_host,
        port=config.redis_port,
        db=config.redis_db,
        decode_responses=True,
    )
    return conn

# ################################################################################################################################

def _load_settings_from_redis(config, fernet_key):
    conn = _get_redis_connection(config)
    raw = conn.get(redis_key_settings)

    if not raw:
        raise Exception('No backup settings found in Redis. Configure backup settings in the dashboard first.')

    if isinstance(fernet_key, str):
        fernet_key_bytes = fernet_key.encode('utf-8')
    else:
        fernet_key_bytes = fernet_key

    f = Fernet(fernet_key_bytes)

    if isinstance(raw, str):
        raw_bytes = raw.encode('utf-8')
    else:
        raw_bytes = raw

    decrypted = f.decrypt(raw_bytes)
    settings = loads(decrypted.decode('utf-8'))
    return settings

# ################################################################################################################################

def _load_password_from_redis(config, fernet_key):
    conn = _get_redis_connection(config)
    raw = conn.get(redis_key_password)

    if not raw:
        raise Exception('No backup password found in Redis. Configure backup settings in the dashboard first.')

    if isinstance(fernet_key, str):
        fernet_key_bytes = fernet_key.encode('utf-8')
    else:
        fernet_key_bytes = fernet_key

    f = Fernet(fernet_key_bytes)

    if isinstance(raw, str):
        raw_bytes = raw.encode('utf-8')
    else:
        raw_bytes = raw

    decrypted = f.decrypt(raw_bytes)
    password = decrypted.decode('utf-8')
    return password

# ################################################################################################################################

def _build_config_from_redis(fernet_key, redis_host='localhost', redis_port=6379, redis_db=0):
    config = BackupConfig()
    config.redis_host = redis_host
    config.redis_port = redis_port
    config.redis_db = redis_db

    settings = _load_settings_from_redis(config, fernet_key)
    config.provider = settings['provider']
    config.bucket_name = settings['bucket_name']
    config.access_key = settings['access_key']
    config.secret_key = settings['secret_key']
    config.env_dir = settings['env_dir']

    return config

# ################################################################################################################################

def _json_response(success, **kwargs):
    result = {'success': success}
    result.update(kwargs)
    out = dumps(result)
    return out

# ################################################################################################################################

def _write_response(response):
    sys.stdout.write(response)
    sys.stdout.write('\n')
    sys.stdout.flush()

# ################################################################################################################################
# ################################################################################################################################

def cmd_backup(config, password):
    try:
        now = datetime.now(timezone.utc)
        timestamp = now.strftime('%Y-%m-%dT%H-%M-%S')
        env_name = os.path.basename(config.env_dir.rstrip('/'))
        object_name = f'{backup_prefix}{env_name}-{timestamp}{enc_extension}'

        archive_bytes = _create_tar_gz(config.env_dir)
        encrypted_data = _encrypt_archive(archive_bytes, password)
        _upload_to_cloud(config, object_name, encrypted_data)

        response = _json_response(
            True,
            object_name=object_name,
            size=len(encrypted_data),
            timestamp=now.isoformat(),
        )
        _write_response(response)

    except Exception:
        logger.error('Backup failed: %s', format_exc())
        response = _json_response(False, error=format_exc())
        _write_response(response)
        sys.exit(1)

# ################################################################################################################################
# ################################################################################################################################

def main():

    parser = argparse.ArgumentParser(description='Zato environment backup tool')
    subparsers = parser.add_subparsers(dest='command')

    backup_parser = subparsers.add_parser('backup')
    backup_parser.add_argument('--password', default='')
    backup_parser.add_argument('--fernet-key', default='')
    backup_parser.add_argument('--dir', dest='env_dir', default='')
    backup_parser.add_argument('--provider', default='')
    backup_parser.add_argument('--bucket', default='')
    backup_parser.add_argument('--access-key', default='')
    backup_parser.add_argument('--secret-key', default='')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'backup':

        config = BackupConfig()

        if args.fernet_key:
            config = _build_config_from_redis(args.fernet_key)

        if args.env_dir:
            config.env_dir = args.env_dir

        if args.provider:
            config.provider = args.provider

        if args.bucket:
            config.bucket_name = args.bucket

        if args.access_key:
            config.access_key = args.access_key

        if args.secret_key:
            config.secret_key = args.secret_key

        if not config.env_dir:
            response = _json_response(False, error='--dir is required')
            _write_response(response)
            sys.exit(1)

        if not config.provider:
            response = _json_response(False, error='--provider is required (aws, gcs, azure)')
            _write_response(response)
            sys.exit(1)

        if not config.bucket_name:
            response = _json_response(False, error='--bucket is required')
            _write_response(response)
            sys.exit(1)

        password = args.password

        if not password:
            if args.fernet_key:
                password = _load_password_from_redis(config, args.fernet_key)
            else:
                password = getpass('Backup encryption password: ')

        cmd_backup(config, password)

# ################################################################################################################################

if __name__ == '__main__':
    main()
