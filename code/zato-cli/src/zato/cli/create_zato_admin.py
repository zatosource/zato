# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, shutil, uuid
from copy import deepcopy

# Zato
from zato.cli import ZATO_ADMIN_DIR, ZatoCommand, common_logging_conf_contents, common_odb_opts
from zato.common.defaults import zato_admin_host, zato_admin_port
from zato.common.util import encrypt

config_template = """{{
  "host": "{host}",
  "port": {port},
  "db_type": "{db_type}",
  "log_config": "{log_config}",

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
  
  "TECH_ACCOUNT_NAME": "{TECH_ACCOUNT_NAME}",
  "TECH_ACCOUNT_PASSWORD": "{TECH_ACCOUNT_PASSWORD}"
}}
"""

class Create(ZatoCommand):
    needs_empty_dir = True
    allow_empty_secrets = True
    
    opts = deepcopy(common_odb_opts)
    
    opts.append({'name':'pub_key_path', 'help':"Path to the Zato Admin's public key in PEM"})
    opts.append({'name':'priv_key_path', 'help':"Path to the Zato Admin's private key in PEM"})
    opts.append({'name':'cert_path', 'help':"Path to the Zato Admin's certificate in PEM"})
    
    opts.append({'name':'tech_account_name', 'help':'Technical account name to use for connecting to Zato clusters'})
    opts.append({'name':'--tech_account_password', 'help':"Technical account password"})
    
    def __init__(self, args):
        self.target_dir = os.path.abspath(args.path)
        super(Create, self).__init__(args)

    def execute(self, args):

        repo_dir = os.path.join(self.target_dir, 'config', 'repo')

        os.mkdir(os.path.join(self.target_dir, 'logs'))
        os.mkdir(os.path.join(self.target_dir, 'config'))
        os.mkdir(repo_dir)
        
        shutil.copyfile(os.path.abspath(args.pub_key_path), os.path.join(repo_dir, 'zato-admin-pub-key.pem'))
        shutil.copyfile(os.path.abspath(args.priv_key_path), os.path.join(repo_dir, 'zato-admin-priv-key.pem'))
        shutil.copyfile(os.path.abspath(args.cert_path), os.path.join(repo_dir, 'zato-admin-cert.pem'))        
        
        pub_key = open(os.path.join(repo_dir, 'zato-admin-pub-key.pem')).read()
        
        config = {
            'host': zato_admin_host,
            'port': zato_admin_port,
            'db_type': args.odb_type,
            'log_config': 'logging.conf',
            'DATABASE_NAME': args.odb_db_name,
            'DATABASE_USER': args.odb_user,
            'DATABASE_PASSWORD': encrypt(args.odb_password, pub_key),
            'DATABASE_HOST': args.odb_host,
            'DATABASE_PORT': args.odb_port,
            'SITE_ID': uuid.uuid4().int,
            'SECRET_KEY': encrypt(uuid.uuid4().hex, pub_key),
            'TECH_ACCOUNT_NAME':args.tech_account_name,
            'TECH_ACCOUNT_PASSWORD':encrypt(args.tech_account_password, pub_key),
        }
        
        open(os.path.join(self.target_dir, 'config', 'repo', 'logging.conf'), 'w').write(common_logging_conf_contents.format(log_path='./logs/zato-admin.log'))
        open(os.path.join(self.target_dir, 'config', 'repo', 'zato-admin.conf'), 'w').write(config_template.format(**config))
        
        # Initial info
        self.store_initial_info(self.target_dir, self.COMPONENTS.ZATO_ADMIN.code)

        if self.verbose:
            msg = """Successfully created a Zato Admin instance.
You can start it with the 'zato start zato_admin {path}' command.""".format(path=os.path.abspath(os.path.join(os.getcwd(), self.target_dir)))
            self.logger.debug(msg)
        else:
            self.logger.info('OK')
