# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

import os
import sys
import logging

from django.core.wsgi import get_wsgi_application

# Basic logging for WSGI setup process
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("Zato Dashboard WSGI: Initializing...')

# Zato specific imports (must be findable via PYTHONPATH)
# Ensure the .../code/zato-web-admin/src/ directory is in your PYTHONPATH
# or Gunicorn is run from that directory.
try:
    from zato.admin.zato_settings import update_globals
    from zato.common.json_internal import loads
    from zato.common.util.open_ import open_r
except ImportError as e:
    logger.error(f'Zato Dashboard WSGI: Failed to import Zato utility modules: {e}. "
                    "Ensure PYTHONPATH is set correctly to include the 'src' directory "
                    "containing the 'zato' package.')
    raise

# Determine base_dir_abs: This MUST point to your Zato web-admin component's instance directory
# (e.g., /opt/zato/env1/web-admin or wherever config/repo/web-admin.conf is located).
# This script relies on the Zato_Dashboard_Base_Dir environment variable.
Zato_Dashboard_Base_Dir = os.environ.get('Zato_Dashboard_Base_Dir')
if not Zato_Dashboard_Base_Dir:
    error_msg = (
        "Zato_Dashboard_Base_Dir environment variable is not set. "
        "This is required for the Zato Dashboard WSGI application to find its configuration. "
        "Set it to the path of your web-admin component's instance/runtime directory "
        "(the directory containing 'config/repo/web-admin.conf')."
    )
    logger.error(error_msg)
    raise RuntimeError(error_msg)

base_dir_abs = os.path.abspath(Zato_Dashboard_Base_Dir)
repo_dir = os.path.join(base_dir_abs, 'config', 'repo')
web_admin_conf_path = os.path.join(repo_dir, 'web-admin.conf')

if not os.path.exists(web_admin_conf_path):
    error_msg = (
        f'web-admin.conf not found at '{web_admin_conf_path}'. "
        f'Ensure Zato_Dashboard_Base_Dir (currently set to '{Zato_Dashboard_Base_Dir}') points to the correct directory."
    )
    logger.error(error_msg)
    raise FileNotFoundError(error_msg)

logger.info(f'Zato Dashboard WSGI: Loading configuration using Zato_Dashboard_Base_Dir='{base_dir_abs}'.')
logger.info(f'Zato Dashboard WSGI: Expecting web-admin.conf at '{web_admin_conf_path}'.')

# Load web-admin.conf and update globals for settings.py
try:
    config_content = open_r(web_admin_conf_path).read()
    config = loads(config_content)
except Exception as e:
    logger.error(f'Zato Dashboard WSGI: Error loading or parsing {web_admin_conf_path}: {e}')
    raise

config['config_dir'] = base_dir_abs # settings.py uses this

# If log_config in web-admin.conf is relative, it's relative to Zato_Dashboard_Base_Dir.
original_log_config = config.get('log_config')
if original_log_config:
    if not os.path.isabs(original_log_config):
        config['log_config'] = os.path.join(base_dir_abs, original_log_config)
        logger.info(f'Zato Dashboard WSGI: Resolved relative log_config to '{config['log_config']}'.')
    else:
        logger.info(f'Zato Dashboard WSGI: Using absolute log_config '{original_log_config}'.')
else:
    logger.info("Zato Dashboard WSGI: 'log_config' not found in web-admin.conf.')


# This function injects the loaded configuration into the global scope
# where zato.admin.settings can access them.
update_globals(config)
logger.info("Zato Dashboard WSGI: Zato-specific global settings updated.')

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zato.admin.settings')
logger.info(f'Zato Dashboard WSGI: DJANGO_SETTINGS_MODULE set to '{os.environ['DJANGO_SETTINGS_MODULE']}'.')

# This will implicitly call django.setup() if not already done
application = get_wsgi_application()

logger.info("Zato Dashboard WSGI: Django application initialized successfully. Ready for Gunicorn.')
