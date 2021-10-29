# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
from unittest import main, TestCase

# Bunch
from bunch import bunchify

# Django
import django

# Zato
from zato.admin.zato_settings import update_globals
from zato.common.util import new_cid

# ################################################################################################################################
# ################################################################################################################################

class Config:

    user_name_prefix = 'zato.unit-test.web-admin.'
    user_password = 'sJNlk8XOQs74E'
    user_email = 'test@example.com'

    web_admin_location = os.path.expanduser('~/env/web-admin.test/web-admin')
    web_admin_address  = 'http://localhost:8183'

# ################################################################################################################################
# ################################################################################################################################

class TestAccessWebAdmin(TestCase):

    def _set_up_django(self):

        import pymysql
        pymysql.install_as_MySQLdb()

        config_path = os.path.join(Config.web_admin_location, 'config', 'repo', 'web-admin.conf')
        config = open(config_path).read()
        config = json.loads(config)

        config['config_dir'] = Config.web_admin_location
        config['log_config'] = os.path.join(Config.web_admin_location, config['log_config'])

        update_globals(config, needs_crypto=False)

        os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'
        django.setup()

# ################################################################################################################################

    def _set_up_django_auth(self):
        from zato.cli.web_admin_auth import CreateUser, UpdatePassword

        # User names are limited to 30 characters
        self.user_name = (Config.user_name_prefix + new_cid())[:30]

        create_args = bunchify({
            'path': Config.web_admin_location,
            'username': self.user_name,
            'password': Config.user_password, # This is ignored by CreateUser yet we need it so as not to prompt for it
            'email': Config.user_email,
            'verbose': True,
            'store_log': False,
            'store_config': False
        })

        command = CreateUser(create_args)
        command.is_interactive = False

        try:
            command.execute(create_args, needs_sys_exit=False)
        except Exception:
            # We need to ignore it as there is no specific exception to catch
            # while the underyling root cause is that the user already exists.
            pass

        update_password_args = bunchify({
            'path': Config.web_admin_location,
            'username': self.user_name,
            'password': Config.user_password,
            'verbose': True,
            'store_log': False,
            'store_config': False
        })

        command = UpdatePassword(update_password_args)
        command.execute(update_password_args)

# ################################################################################################################################

    def setUp(self):
        self._set_up_django()
        self._set_up_django_auth()

# ################################################################################################################################

    def test_access(self):

        # At this point we have:
        # * user_name -> self.user_name
        # * password  -> Config.user_password

        '''
        from zato.admin.urls import urlpatterns

        print()
        for item in urlpatterns:
            print(111, item)
        print()
        '''

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
