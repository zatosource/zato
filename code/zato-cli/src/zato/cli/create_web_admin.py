# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

# stdlib
import os, json, uuid
from copy import deepcopy
from random import getrandbits
from traceback import format_exc

# Django
from django.core.management import call_command

# Zato
# TODO: There really shouldn't be any direct dependency between zato-cli and zato-web-admin
from zato.admin.zato_settings import update_globals

from zato.cli import get_tech_account_opts, common_logging_conf_contents, common_odb_opts, ZatoCommand
from zato.common.defaults import web_admin_host, web_admin_port
from zato.common.markov_passwords import generate_password
from zato.common.util import encrypt

config_template = """{{
  "host": "{host}",
  "port": {port},
  "db_type": "{db_type}",
  "log_config": "./config/repo/{log_config}",

  "DEBUG": 1,

  "DATABASE_NAME": "{DATABASE_NAME}",
  "DATABASE_USER": "{DATABASE_USER}",
  "DATABASE_PASSWORD": "{DATABASE_PASSWORD}",
  "DATABASE_HOST": "{DATABASE_HOST}",
  "DATABASE_PORT": "{DATABASE_PORT}",

  "TIME_ZONE": "America/New_York",
  "LANGUAGE_CODE": "en-us",

  "SITE_ID": {SITE_ID},
  "SECRET_KEY": "{SECRET_KEY}",

  "ADMIN_INVOKE_NAME": "{ADMIN_INVOKE_NAME}",
  "ADMIN_INVOKE_PASSWORD": "{ADMIN_INVOKE_PASSWORD}",
  "ADMIN_INVOKE_PATH": "/zato/admin/invoke",

  "OPENID_SSO_SERVER_URL": ""
}}
"""

initial_data_json = """[{{
"pk": {SITE_ID},
"model": "sites.site",
"fields": {{
    "name": "web admin",
    "domain":"webadmin.example.com"
    }}
}}]
"""

class Create(ZatoCommand):
    """ Creates a new web admin web console
    """
    needs_empty_dir = True
    allow_empty_secrets = True

    opts = deepcopy(common_odb_opts)

    opts.append({'name':'pub_key_path', 'help':"Path to the web admin's public key in PEM"})
    opts.append({'name':'priv_key_path', 'help':"Path to the web admin's private key in PEM"})
    opts.append({'name':'cert_path', 'help':"Path to the web admin's certificate in PEM"})
    opts.append({'name':'ca_certs_path', 'help':"Path to a bundle of CA certificates to be trusted"})

    opts += get_tech_account_opts()

    def __init__(self, args):
        self.target_dir = os.path.abspath(args.path)
        super(Create, self).__init__(args)

    def execute(self, args, show_output=True, password=None, needs_admin_created_flag=False):
        os.chdir(self.target_dir)

        repo_dir = os.path.join(self.target_dir, 'config', 'repo')
        web_admin_conf_path = os.path.join(repo_dir, 'web-admin.conf')
        initial_data_json_path = os.path.join(repo_dir, 'initial-data.json')

        os.mkdir(os.path.join(self.target_dir, 'logs'))
        os.mkdir(os.path.join(self.target_dir, 'config'))
        os.mkdir(repo_dir)

        user_name = 'admin'
        password = password if password else generate_password()

        self.copy_web_admin_crypto(repo_dir, args)
        priv_key = open(os.path.join(repo_dir, 'web-admin-priv-key.pem')).read()

        config = {
            'host': web_admin_host,
            'port': web_admin_port,
            'db_type': args.odb_type,
            'log_config': 'logging.conf',
            'DATABASE_NAME': args.odb_db_name or args.sqlite_path,
            'DATABASE_USER': args.odb_user or '',
            'DATABASE_PASSWORD': encrypt(args.odb_password, priv_key) if args.odb_password else '',
            'DATABASE_HOST': args.odb_host or '',
            'DATABASE_PORT': args.odb_port or '',
            'SITE_ID': getrandbits(20),
            'SECRET_KEY': encrypt(uuid.uuid4().hex, priv_key),
            'ADMIN_INVOKE_NAME':'admin.invoke',
            'ADMIN_INVOKE_PASSWORD':encrypt(getattr(args, 'admin_invoke_password', None) or getattr(args, 'tech_account_password'), priv_key),
        }

        open(os.path.join(repo_dir, 'logging.conf'), 'w').write(common_logging_conf_contents.format(log_path='./logs/web-admin.log'))
        open(web_admin_conf_path, 'w').write(config_template.format(**config))
        open(initial_data_json_path, 'w').write(initial_data_json.format(**config))

        # Initial info
        self.store_initial_info(self.target_dir, self.COMPONENTS.WEB_ADMIN.code)

        config = json.loads(open(os.path.join(repo_dir, 'web-admin.conf')).read())
        config['config_dir'] = self.target_dir
        update_globals(config, self.target_dir)

        os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'

        import django
        django.setup()
        self.reset_logger(args, True)

        # Can't import these without DJANGO_SETTINGS_MODULE being set
        from django.contrib.auth.models import User
        from django.db import connection
        from django.db.utils import IntegrityError

        call_command('migrate', run_syncdb=True, interactive=False, verbosity=0)
        call_command('loaddata', initial_data_json_path, verbosity=0)

        try:
            call_command(
                'createsuperuser', interactive=False, username=user_name, first_name='admin-first-name',
                last_name='admin-last-name', email='admin@invalid.example.com')
            admin_created = True

            user = User.objects.get(username=user_name)
            user.set_password(password)
            user.save()

        except IntegrityError, e:
            admin_created = False
            connection._rollback()
            self.logger.info('Ignoring IntegrityError e:[%s]', format_exc(e).decode('utf-8'))

        # Needed because Django took over our logging config
        self.reset_logger(args, True)

        if show_output:
            if self.verbose:
                msg = """Successfully created a web admin instance.
    You can start it with the 'zato start {path}' command.""".format(path=os.path.abspath(os.path.join(os.getcwd(), self.target_dir)))
                self.logger.debug(msg)
            else:
                self.logger.info('OK')

        # We return it only when told to explicitly so when the command runs from CLI
        # it doesn't return a non-zero exit code.
        if needs_admin_created_flag:
            return admin_created
