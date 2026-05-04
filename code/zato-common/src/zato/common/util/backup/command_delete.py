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
from zato.common.util.backup.cloud import delete_from_cloud
from zato.common.util.backup.common import json_response, write_response
from zato.common.util.backup.config import BackupConfig

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def command_delete(config:'BackupConfig', backup_key:'str') -> 'None':
    try:
        delete_from_cloud(config, backup_key)

        response = json_response(
            True,
            deleted=backup_key,
        )
        write_response(response)

    except Exception:
        logger.error('Delete backup failed: %s', format_exc())
        response = json_response(False, error=format_exc())
        write_response(response)
        sys.exit(1)

# ################################################################################################################################
# ################################################################################################################################
