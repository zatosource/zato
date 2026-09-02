# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile

# The URL config imports every view module, and the views pull in the Dashboard's
# settings module, which expects the values `zato start` would have injected -
# so the same values are seeded here first, over a throwaway SQLite database.
_work_dir = tempfile.mkdtemp()
os.makedirs(os.path.join(_work_dir, 'config', 'repo'))

_db_path = os.path.join(_work_dir, 'web-admin.db')

# Zato
import zato.admin.zato_settings as zato_settings
from zato.common.typing_ import any_, cast_

# The settings module receives these values dynamically, the way update_globals injects them.
_settings:'any_' = cast_('any_', zato_settings)

_settings.db_type = 'sqlite'
_settings.DATABASES = {'default': {'NAME': _db_path, 'USER': '', 'PASSWORD': '', 'HOST': '', 'PORT': ''}}
_settings.config_dir = _work_dir
_settings.log_config = ''
_settings.ADMIN_INVOKE_NAME = 'admin.invoke'
_settings.ADMIN_INVOKE_PASSWORD = 'test-password'
_settings.SECRET_KEY = 'test-secret-key'

# Django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=False,
        DATABASES={},
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'zato.admin.web',
        ],
        USE_TZ=True,
        DEFAULT_CHARSET='utf-8',
    )

    import django
    django.setup()

# ################################################################################################################################
# ################################################################################################################################
