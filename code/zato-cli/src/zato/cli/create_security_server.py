# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

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
from zato.cli import ZatoCommand, ZATO_SECURITY_SERVER_DIR

config_py_template = \
"""
# -*- coding: utf-8 -*-

# stdlib
import json, uuid

# Don't share it with anyone.
INSTANCE_SECRET = '{instance_secret}'

# May be shared with the outside world.
INSTANCE_UNIQUE = uuid.uuid4().hex

# Crypto
keyfile = './security-server-priv-key.pem'
certfile = './security-server-cert.pem'
ca_certs = './ca-chain.pem'

server_type = 'https'

_config = json.loads(open('./config.yaml').read())

# ##############################################################################

def default():
    return {{
        'ssl': True,
        'ssl-pass-context': True,
        'ssl-wrap-only': True,
        'host': _config['host']
    }}

urls = [
    ('/*', default()),
]
"""

config_yaml_contents = \
"""
{
  "host": "http://localhost:11223"
}
"""



class CreateSecurityServer(ZatoCommand):
    command_name = 'create security-server'

    needs_empty_dir = True

    def __init__(self, target_dir):
        super(CreateSecurityServer, self).__init__()
        self.target_dir = target_dir

    description = "Creates a security server"

    def execute(self, args):

        os.mkdir(self.target_dir)
        os.mkdir(os.path.join(self.target_dir, 'logs'))
        config_py_loc = os.path.join(self.target_dir, 'config.py')
        config_yaml_loc = os.path.join(self.target_dir, 'config.yaml')
        sec_wall_config_marker = os.path.join(self.target_dir, '.sec-wall-config')
        sec_sever_dir_marker = os.path.join(self.target_dir, ZATO_SECURITY_SERVER_DIR)

        config_py = open(config_py_loc, 'w')
        config_py.write(config_py_template.format(instance_secret=uuid.uuid4().hex))
        config_py.close()

        config_yaml = open(config_yaml_loc, 'w')
        config_yaml.write(config_yaml_contents)
        config_yaml.close()

        open(sec_wall_config_marker, 'w').close()
        open(sec_sever_dir_marker, 'w').close()

        msg = """\nSuccessfully created a security server.
You can now and start it with the 'zato start {path}' command.
""".format(path=os.path.abspath(os.path.join(os.getcwd(), self.target_dir)))

        print(msg)

def main(target_dir):
    CreateSecurityServer(target_dir).run()

if __name__ == "__main__":
    main(".")
