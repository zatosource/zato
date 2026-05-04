# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from datetime import datetime, timezone
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.util.backup.cloud import delete_from_cloud, list_cloud_objects
from zato.common.util.backup.common import json_response, write_response
from zato.common.util.backup.config import BackupConfig, backup_prefix

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def command_cleanup(config:'BackupConfig', retention_days:'int') -> 'None':
    try:
        now = datetime.now(timezone.utc)
        cloud_objects = list_cloud_objects(config)

        deleted = []

        for cloud_object in cloud_objects:
            name = cloud_object.name

            # ..  only consider objects that match the backup naming pattern.
            if not name.startswith(backup_prefix):
                continue

            last_modified_raw = cloud_object.extra.get('last_modified', '')
            if not last_modified_raw:
                continue

            last_modified = datetime.fromisoformat(last_modified_raw)
            if last_modified.tzinfo is None:
                last_modified = last_modified.replace(tzinfo=timezone.utc)

            age_days = (now - last_modified).days

            if age_days > retention_days:
                delete_from_cloud(config, name)
                deleted.append(name)

        response = json_response(
            True,
            deleted=deleted,
            total_deleted=len(deleted),
            retention_days=retention_days,
        )
        write_response(response)

    except Exception:
        logger.error('Cleanup failed: %s', format_exc())
        response = json_response(False, error=format_exc())
        write_response(response)
        sys.exit(1)

# ################################################################################################################################
# ################################################################################################################################
