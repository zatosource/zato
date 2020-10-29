# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy

# Zato
from zato.cli import common_odb_opts, ZatoCommand

config_template = """{{
  "host": "{host}",
  "port": {port},
  "db_type": "{db_type}",
  "log_config": "./config/repo/{log_config}",
  "lb_agent_use_tls": {lb_agent_use_tls},
  "lb_use_tls": false,
  "lb_tls_verify": true,
  "zato_secret_key": "{zato_secret_key}",
  "well_known_data": "{well_known_data}",
  "is_totp_enabled": false,

  "DEBUG": 0,
  "ALLOWED_HOSTS": ["*"],

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
  "ADMIN_INVOKE_PATH": "/zato/admin/invoke"
}}
"""

initial_data_json = """[{{
"pk": {SITE_ID},
"model": "sites.site",
"fields": {{
    "name": "web admin",
    "domain":"webadmin-{SITE_ID}.example.com"
    }}
}}]
"""

class Create(ZatoCommand):
    """ Creates a new web admin web console
    """
    needs_empty_dir = True
    allow_empty_secrets = True

    opts = deepcopy(common_odb_opts)

    opts.append({'name':'--pub_key_path', 'help':"Path to the web admin's public key in PEM"})
    opts.append({'name':'--priv_key_path', 'help':"Path to the web admin's private key in PEM"})
    opts.append({'name':'--cert_path', 'help':"Path to the web admin's certificate in PEM"})
    opts.append({'name':'--ca_certs_path', 'help':"Path to a bundle of CA certificates to be trusted"})
    opts.append({'name':'--admin-invoke-password', 'help':'Password for web-admin to connect to servers with'})

    def __init__(self, args):

        # stdlib
        import os

        self.target_dir = os.path.abspath(args.path)
        super(Create, self).__init__(args)

    def execute(self, args, show_output=True, admin_password=None, needs_admin_created_flag=False):

        try:
            import pymysql
            pymysql.install_as_MySQLdb()
        except ImportError:
            pass

        # stdlib
        import os, json
        from random import getrandbits
        from uuid import uuid4

        # Django
        from django.core.management import call_command

        # Python 2/3 compatibility
        from past.builtins import unicode

        # Zato
        # TODO: There really shouldn't be any direct dependency between zato-cli and zato-web-admin
        from zato.admin.zato_settings import update_globals

        from zato.cli import common_logging_conf_contents, is_arg_given
        from zato.common.crypto.api import WebAdminCryptoManager
        from zato.common.crypto.const import well_known_data
        from zato.common.defaults import web_admin_host, web_admin_port

        os.chdir(self.target_dir)

        repo_dir = os.path.join(self.target_dir, 'config', 'repo')
        web_admin_conf_path = os.path.join(repo_dir, 'web-admin.conf')
        initial_data_json_path = os.path.join(repo_dir, 'initial-data.json')

        os.mkdir(os.path.join(self.target_dir, 'logs'))
        os.mkdir(os.path.join(self.target_dir, 'config'))
        os.mkdir(repo_dir)

        user_name = 'admin'
        admin_password = admin_password if admin_password else WebAdminCryptoManager.generate_password()

        # If we have a CA's certificate then it implicitly means that there is some CA
        # which tells us that we are to trust both the CA and the certificates that it issues,
        # and the only certificate we are interested in is the one to the load-balancer.
        # This is why, if we get ca_certs_path, it must be because we are to use TLS
        # in communication with the load-balancer's agent which in turn means that we have crypto material on input.
        has_crypto = is_arg_given(args, 'ca_certs_path')

        if has_crypto:
            self.copy_web_admin_crypto(repo_dir, args)

        zato_secret_key = WebAdminCryptoManager.generate_key()
        cm = WebAdminCryptoManager.from_secret_key(zato_secret_key)

        django_secret_key = uuid4().hex.encode('utf8')
        django_site_id = getrandbits(20)

        admin_invoke_password = getattr(args, 'admin_invoke_password', None)

        if not admin_invoke_password:
            admin_invoke_password = 'create_wa.admin.' + uuid4().hex

        if isinstance(admin_invoke_password, unicode):
            admin_invoke_password = admin_invoke_password.encode('utf8')

        odb_password = args.odb_password or ''
        odb_password = odb_password.encode('utf8')


        config = {
            'host': web_admin_host,
            'port': web_admin_port,
            'db_type': args.odb_type,
            'log_config': 'logging.conf',
            'lb_agent_use_tls': 'true' if has_crypto else 'false',
            'zato_secret_key':zato_secret_key,
            'well_known_data': cm.encrypt(well_known_data.encode('utf8')),
            'DATABASE_NAME': args.odb_db_name or args.sqlite_path,
            'DATABASE_USER': args.odb_user or '',
            'DATABASE_PASSWORD': cm.encrypt(odb_password),
            'DATABASE_HOST': args.odb_host or '',
            'DATABASE_PORT': args.odb_port or '',
            'SITE_ID': django_site_id,
            'SECRET_KEY': cm.encrypt(django_secret_key),
            'ADMIN_INVOKE_NAME':'admin.invoke',
            'ADMIN_INVOKE_PASSWORD':cm.encrypt(admin_invoke_password),
        }

        for name in 'zato_secret_key', 'well_known_data', 'DATABASE_PASSWORD', 'SECRET_KEY', 'ADMIN_INVOKE_PASSWORD':
            config[name] = config[name].decode('utf8')

        open(os.path.join(repo_dir, 'logging.conf'), 'w').write(
            common_logging_conf_contents.format(log_path='./logs/web-admin.log'))
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
            user.set_password(admin_password)
            user.save()

        except IntegrityError:
            # This will happen if user 'admin' already exists, e.g. if this is not the first cluster in this database
            admin_created = False
            connection._rollback()

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
