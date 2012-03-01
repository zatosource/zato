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
from zato.cli import ZATO_BROKER_DIR, ZatoCommand, common_logging_conf_contents

config_template = """{{
  "host": "{host}",
  "start_port": {start_port},
  "token": "{token}",
  "log_invalid_tokens": true,
  "log_config": "{log_config}"
}}
"""

class CreateBroker(ZatoCommand):
    command_name = 'create broker'
    needs_empty_dir = True

    def __init__(self, target_dir):
        super(CreateBroker, self).__init__()
        self.target_dir = target_dir
        self.token = uuid.uuid4().hex

    description = 'Creates a Zato broker.'

    def execute(self, args):

        config = {
            'host': args.broker_host,
            'start_port': args.broker_start_port,
            'log_config': 'logging.conf',
            'token': self.token
        }

        os.mkdir(os.path.join(self.target_dir))
        os.mkdir(os.path.join(self.target_dir, 'config'))
        os.mkdir(os.path.join(self.target_dir, 'config/repo'))
        os.mkdir(os.path.join(self.target_dir, 'config/zdaemon'))
        os.mkdir(os.path.join(self.target_dir, 'logs'))
        open(os.path.join(self.target_dir, 'config/repo', 'logging.conf'), 'w').write(common_logging_conf_contents.format(log_path='../../logs/broker.log'))
        open(os.path.join(self.target_dir, 'config/repo', 'broker.conf'), 'w').write(config_template.format(**config))
        open(os.path.join(self.target_dir, ZATO_BROKER_DIR), 'w').close()

        msg = """\nSuccessfully created a Zato broker.
You can now go to {path} and start it with the 'zato start .' command.
""".format(path=os.path.abspath(os.path.join(os.getcwd(), self.target_dir)))

        print(msg)

def main(target_dir):
    CreateBroker(target_dir).run()

if __name__ == '__main__':
    main('.')
