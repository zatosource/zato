# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
from datetime import datetime, timezone
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.util.backup.cloud import upload_to_cloud
from zato.common.util.backup.common import json_response, write_response
from zato.common.util.backup.config import BackupConfig, backup_prefix, encrypted_extension
from zato.common.util.backup.crypto import encrypt_archive
from zato.common.util.backup.tar import create_tar_gz

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def command_backup(config:'BackupConfig', password:'str') -> 'None':
    try:
        now = datetime.now(timezone.utc)
        timestamp = now.strftime('%Y-%m-%dT%H-%M-%S')
        env_name = os.path.basename(config.env_dir.rstrip('/'))
        object_name = f'{backup_prefix}{env_name}-{timestamp}{encrypted_extension}'

        archive_bytes = create_tar_gz(config.env_dir)
        encrypted_data = encrypt_archive(archive_bytes, password)
        upload_to_cloud(config, object_name, encrypted_data)

        response = json_response(
            True,
            object_name=object_name,
            size=len(encrypted_data),
            timestamp=now.isoformat(),
        )
        write_response(response)

    except Exception:
        logger.error('Backup failed: %s', format_exc())
        response = json_response(False, error=format_exc())
        write_response(response)
        sys.exit(1)

# ################################################################################################################################
# ################################################################################################################################
