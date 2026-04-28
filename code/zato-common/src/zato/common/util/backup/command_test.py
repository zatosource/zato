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
from zato.common.util.backup.cloud import _test_cloud_connection
from zato.common.util.backup.common import _json_response, _write_response
from zato.common.util.backup.config import BackupConfig

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def command_test(config:'BackupConfig') -> 'None':
    try:
        _test_cloud_connection(config)

        response = _json_response(
            True,
            message=f'Connection to bucket {config.bucket_name!r} successful',
        )
        _write_response(response)

    except Exception:
        logger.error('Connection test failed: %s', format_exc())
        response = _json_response(False, error=format_exc())
        _write_response(response)
        sys.exit(1)

# ################################################################################################################################
# ################################################################################################################################
