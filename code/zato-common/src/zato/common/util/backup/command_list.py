# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.util.backup.cloud import list_cloud_objects
from zato.common.util.backup.common import json_response, write_response
from zato.common.util.backup.config import BackupConfig, backup_prefix

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def command_list(config:'BackupConfig') -> 'None':
    try:
        cloud_objects = list_cloud_objects(config)

        backups = []

        for cloud_object in cloud_objects:
            name = cloud_object.name

            # ..  only include objects that match the backup naming pattern.
            if not name.startswith(backup_prefix):
                continue

            entry = {
                'name': name,
                'size': cloud_object.size,
                'last_modified': cloud_object.extra.get('last_modified', ''),
            }
            backups.append(entry)

        # ..  sort by name descending so that the most recent backup is first.
        backups.sort(key=lambda item: item['name'], reverse=True)

        response = json_response(
            True,
            backups=backups,
            total=len(backups),
        )
        write_response(response)

    except Exception:
        logger.error('List backups failed: %s', format_exc())
        response = json_response(False, error=format_exc())
        write_response(response)
        sys.exit(1)

# ################################################################################################################################
# ################################################################################################################################
