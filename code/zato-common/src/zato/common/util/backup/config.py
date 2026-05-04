# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# libcloud
from libcloud.storage.types import Provider

# ################################################################################################################################
# ################################################################################################################################

encrypted_extension = '.tar.gz.enc'
backup_prefix = 'zato-backup-'

redis_key_settings = 'zato:backup:settings'
redis_key_schedule = 'zato:backup:schedule'
redis_key_password = 'zato:backup:password'

kdf_salt_length = 16
aes_key_length = 32
aes_nonce_length = 12
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

    provider:    'str' = ''
    bucket_name: 'str' = ''
    access_key:  'str' = ''
    secret_key:  'str' = ''
    env_dir:     'str' = ''
    redis_host:  'str' = 'localhost'
    redis_port:  'int' = 6379
    redis_db:    'int' = 0

# ################################################################################################################################
# ################################################################################################################################
