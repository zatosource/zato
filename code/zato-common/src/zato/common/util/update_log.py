# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from logging import getLogger, Formatter, DEBUG
from logging.handlers import RotatingFileHandler
from traceback import format_exc

# Zato
from zato.common.defaults import default_env_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strnone

# ################################################################################################################################
# ################################################################################################################################

# The logger of the updater, which Dashboard and the CLI commands look up by this name
Update_Logger_Name = 'zato.common.util.updates'

logger = getLogger(Update_Logger_Name)

# ################################################################################################################################
# ################################################################################################################################

def setup_update_file_logger(base_dir:'strnone'=None, component_name:'str'='unknown') -> 'None':
    """ Sets up file handler for update.log at DEBUG level with rotation.
    Can be called from both Updater and CLI commands.
    """
    try:
        if not base_dir:
            base_dir = default_env_base_dir

        update_log_path = os.path.join(base_dir, 'server1', 'logs', 'update.log')
        os.makedirs(os.path.dirname(update_log_path), exist_ok=True)

        file_handler = RotatingFileHandler(
            update_log_path,
            maxBytes=10 * 1024 * 1024,
            backupCount=100
        )
        file_handler.setLevel(DEBUG)

        formatter = Formatter('%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s')
        formatter.converter = time.localtime
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.setLevel(DEBUG)

        logger.debug('setup_update_file_logger: update.log configured for component [{}] at {}'.format(component_name, update_log_path))
    except Exception:
        logger.error('setup_update_file_logger: failed to setup update logger for component [{}]: {}'.format(component_name, format_exc()))

# ################################################################################################################################
# ################################################################################################################################
