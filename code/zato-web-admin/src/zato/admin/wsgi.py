# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import logging

# Django
from django.core.wsgi import get_wsgi_application

# ################################################################################################################################
# ################################################################################################################################

from zato.admin.zato_settings import update_globals
from zato.common.json_internal import loads
from zato.common.util.open_ import open_r

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

Zato_Dashboard_Base_Dir = os.environ.get('Zato_Dashboard_Base_Dir')
if not Zato_Dashboard_Base_Dir:
    raise Exception('Env. variable Zato_Dashboard_Base_Dir missing')

base_dir_abs = os.path.abspath(Zato_Dashboard_Base_Dir)
repo_dir = os.path.join(base_dir_abs, 'config', 'repo')
web_admin_conf_path = os.path.join(repo_dir, 'web-admin.conf')

if not os.path.exists(web_admin_conf_path):
    error_msg = 'Path not found: '+ web_admin_conf_path
    logger.error(error_msg)
    raise FileNotFoundError(error_msg)

config_content = open_r(web_admin_conf_path).read()
config = loads(config_content)

config['config_dir'] = base_dir_abs # settings.py uses this

original_log_config = config.get('log_config')
if original_log_config:
    if not os.path.isabs(original_log_config):
        config['log_config'] = os.path.join(base_dir_abs, original_log_config)

# This function injects the loaded configuration into the global scope
# where zato.admin.settings can access them.
update_globals(config)

_ = os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zato.admin.settings')

# This will implicitly call django.setup() if not already done
application = get_wsgi_application()

# ################################################################################################################################
# ################################################################################################################################
