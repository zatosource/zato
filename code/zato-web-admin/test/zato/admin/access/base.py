# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
from http.client import FOUND, MOVED_PERMANENTLY, NOT_MODIFIED, OK
from unittest import TestCase

# Bunch
from bunch import bunchify

# Django
import django

# Selenium-Wire
if os.environ.get('ZATO_TEST_DASHBOARD'):
    from seleniumwire import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.support import expected_conditions as conditions
    from selenium.webdriver.support.ui import WebDriverWait

# Zato
from zato.admin.zato_settings import update_globals
from zato.common.util import new_cid

# ################################################################################################################################
# ################################################################################################################################

class Config:

    username_prefix = 'zato.unit-test.web-admin.'
    user_password = 'sJNlk8XOQs74E'
    user_email = 'test@example.com'

    web_admin_location = os.path.expanduser('~/env/qs-1/web-admin')
    web_admin_address  = 'http://localhost:8183'

    status_ok = {FOUND, MOVED_PERMANENTLY, NOT_MODIFIED, OK}
    to_skip_status = {
        '/favicon.ico'
    }

# ################################################################################################################################
# ################################################################################################################################

class BaseTestCase(TestCase):

    # Whether we should automatically log in during setUp
    needs_auto_login = True

    # This can be set by each test separately
    run_in_background:'bool'

    # Selenium client
    client: 'webdriver.Firefox'

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
        self.username = (Config.username_prefix + new_cid())[:30]

        create_args = bunchify({
            'path': Config.web_admin_location,
            'username': self.username,
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
            'username': self.username,
            'password': Config.user_password,
            'verbose': True,
            'store_log': False,
            'store_config': False
        })

        command = UpdatePassword(update_password_args)
        command.execute(update_password_args)

# ################################################################################################################################

    def setUp(self):

        if not os.environ.get('ZATO_TEST_DASHBOARD'):
            return

        # Set up everything on Django end ..
        self._set_up_django()
        self._set_up_django_auth()

        # .. add a convenience alias for subclasses ..
        self.config = Config

        # .. log in if requested to.
        if self.needs_auto_login:
            self.login()

# ################################################################################################################################

    def _confirm_not_logged_in(self):
        self.assertEqual(self.client.title, 'Log in - Zato')
        self.assertEqual(self.client.current_url, self.config.web_admin_address + '/accounts/login/?next=/zato/')

# ################################################################################################################################

    def login(self):

        # stdlib
        import os

        if not os.environ.get('ZATO_TEST_DASHBOARD'):
            return

        run_in_background = getattr(self, 'run_in_background', None)
        run_in_background = True if run_in_background is None else run_in_background
        self.run_in_background = run_in_background

        # Custom options for the web client ..
        options = Options()

        if self.run_in_background:
            options.headless = True

        # .. set up our Selenium client ..
        self.client = webdriver.Firefox(options=options)
        self.client.get(self.config.web_admin_address)

        # .. set a wait time in case pages do not load immediately ..
        self.client.implicitly_wait(20)

        # .. confirm that by default we are not logged in ..
        self._confirm_not_logged_in()

        # .. get our form elements ..
        username = self.client.find_element_by_name('username')
        password = self.client.find_element_by_name('password')

        # .. fill out the form ..
        username.send_keys(self.username)
        password.send_keys(self.config.user_password)

        # .. and submit it ..
        password.send_keys(Keys.RETURN)

        # .. wait for the page to load ..
        wait = WebDriverWait(self.client, 2)
        wait.until(conditions.title_contains('Hello'))

        # .. and make sure that everything loaded correctly.
        self.check_response_statuses()

# ################################################################################################################################

    def check_response_statuses(self):
        for item in self.client.requests:
            if item.url.startswith(Config.web_admin_address):
                if 'zato/stats/user/' in item.url:
                    continue
                elif 'zato/groups/' in item.url:
                    continue
                if item.response:
                    if item.response.status_code not in Config.status_ok: # type: ignore
                        if item.path not in Config.to_skip_status:
                            self.fail('Unexpected response `{}` to `{}`'.format(item.response, item))

# ################################################################################################################################

    def tearDown(self):
        if not os.environ.get('ZATO_TEST_DASHBOARD'):
            return

        if self.run_in_background:
            if hasattr(self, 'client'):
                self.client.quit()

        try:
            delattr(self, 'run_in_background')
        except AttributeError:
            pass

# ################################################################################################################################
# ################################################################################################################################
