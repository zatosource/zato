# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from tempfile import gettempdir

# Django
import django
from django.conf import settings

# Zato
import zato.admin.zato_settings as zato_settings
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

# The values the settings module reads at import time ..
_directory_name = 'zato-middleware-client-' + CryptoManager.generate_hex_string()
_work_directory = os.path.join(gettempdir(), _directory_name)

_repo_directory = os.path.join(_work_directory, 'config', 'repo')
os.makedirs(_repo_directory)

_database_path = os.path.join(_work_directory, 'web-admin.db')

_default_database = {'NAME': _database_path, 'USER': '', 'PASSWORD': '', 'HOST': '', 'PORT': ''}

zato_settings.db_type               = 'sqlite'
zato_settings.DATABASES             = {'default': _default_database}
zato_settings.config_dir            = _work_directory
zato_settings.log_config            = ''
zato_settings.ADMIN_INVOKE_NAME     = 'admin.invoke'
zato_settings.ADMIN_INVOKE_PASSWORD = CryptoManager.generate_password(to_str=True)
zato_settings.SECRET_KEY            = CryptoManager.generate_secret(as_str=True)

# ################################################################################################################################
# ################################################################################################################################

# .. and Django itself is configured once per test run.
if not settings.configured:
    settings.configure(
        DATABASES={},
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'zato.admin.web',
        ],
    )

    django.setup()

# ################################################################################################################################
# ################################################################################################################################
