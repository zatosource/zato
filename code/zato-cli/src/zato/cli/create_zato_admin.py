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
import os, uuid

# Zato
from zato.cli import ZATO_ADMIN_DIR, ZatoCommand, common_logging_conf_contents
from zato.common.defaults import zato_admin_host, zato_admin_port

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
  "SECRET_KEY": "{SECRET_KEY}"
}}
"""

class CreateZatoAdmin(ZatoCommand):
    command_name = 'create zato-admin'
    needs_empty_dir = True

    def __init__(self, target_dir):
        super(CreateZatoAdmin, self).__init__()
        self.target_dir = target_dir

    description = 'Creates a Zato Admin instance.'

    def execute(self, args):

        config = {
            'host': zato_admin_host,
            'port': zato_admin_port,
            'db_type': args.odb_type,
            'log_config': 'logging.conf',
            'DATABASE_NAME': args.odb_dbname,
            'DATABASE_USER': args.odb_user,
            'DATABASE_PASSWORD': args.odb_password,
            'DATABASE_HOST': args.odb_host,
            'DATABASE_PORT': args.odb_port,
            'SITE_ID': uuid.uuid4().int,
            'SECRET_KEY': uuid.uuid4().hex,
        }

        os.mkdir(os.path.join(self.target_dir, "logs"))
        open(os.path.join(self.target_dir, 'logging.conf'), 'w').write(common_logging_conf_contents.format(log_path='./logs/admin.log'))
        open(os.path.join(self.target_dir, 'zato-admin.conf'), 'w').write(config_template.format(**config))
        open(os.path.join(self.target_dir, ZATO_ADMIN_DIR), 'w').close()

        msg = """\nSuccessfully created a Zato Admin instance.
You can now go to {path} and start it with the 'zato start zato-admin' command.
""".format(path=os.path.abspath(os.path.join(os.getcwd(), self.target_dir)))

        print(msg)

def main(target_dir):
    CreateZatoAdmin(target_dir).run()

if __name__ == '__main__':
    main('.')
