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
import os

# Zato
from zato.cli import ZatoCommand, ZATO_SERVER_DIR, common_logging_conf_contents
from zato.common.util import encrypt
from zato.server.repo import RepoManager

custom_config_contents = """# -*- coding: utf-8 -*-

# Spring Python
from springpython.config import Object
from springpython.config import PythonConfig

class CustomContext(PythonConfig):
    pass

    # Uncomment below to set a custom HTTP port.

    # @Object
    # def http_port(self):
    #     return 9876
"""

server_conf_template = """[bind]
host=localhost
starting_port=17010

[crypto]
priv_key_location=zs-priv-key.pem
pub_key_location=zs-pub-key.pem
cert_location=zs-cert.pem
ca_certs_location=ca-chain.pem

[odb]
db_name={odb_db_name}
engine={odb_engine}
extra={{}}
host={odb_host}
password={odb_password}
pool_size={odb_pool_size}
user={odb_user}

[scheduler]
job_list_location=job-list.yml
destroy_wait_time=10

[services]
service_store_config_location=service-store-data.yml

[pickup]
pickup_dir=../../pickup-dir
work_dir=../../work

[custom_context]
custom_xml_config_location=
custom_yaml_config_location=
"""

haproxy_conf_contents = """
# ##############################################################################

global
    log 127.0.0.1:514 local0 info
    stats socket ./haproxy-stat.sock

# ##############################################################################

defaults
    log global
    option httpclose

    stats uri /zato-server-stats

    timeout connect 5000
    timeout client 5000
    timeout server 5000

    stats enable
    stats realm   Haproxy\ Statistics
    stats auth    admin1:admin1
    stats refresh 5s

# ##############################################################################

backend bck_http_plain
    mode http
    balance roundrobin

    {backends_http_plain}

# ##############################################################################

frontend front_http_plain

    mode http
    bind 0.0.0.0:27021 # ZATO frontend front_http_plain:bind
    monitor-uri /zato-server-alive # ZATO frontend front_http_plain:monitor-uri
"""

default_odb_pool_size = 4

directories = ('config', 'config/repo', 'config/zdaemon', 'pickup-dir', 'logs')
files = {ZATO_SERVER_DIR: '',
         'config/repo/custom-config.yml': '',
         'config/repo/custom-config.xml':'',
         'config/repo/custom_config.py': custom_config_contents,
         'config/repo/__init__.py': '',
         'config/repo/logging.conf':common_logging_conf_contents.format(log_path='./logs/server.log'),
}

priv_key_location = './config/repo/config-priv.pem'
pub_key_location = './config/repo/config-pub.pem'

class CreateServer(ZatoCommand):
    command_name = 'create server'

    needs_empty_dir = True

    def __init__(self, target_dir):
        super(CreateServer, self).__init__()
        self.target_dir = os.path.abspath(target_dir)
        self.dirs_prepared = False

    description = 'Creates a new Zato server.'

    def prepare_directories(self):
        print('Creating directories..')
        for d in sorted(directories):
            d = os.path.join(self.target_dir, d)
            print('Creating {d}'.format(d=d))
            os.mkdir(d)

        self.dirs_prepared = True

    def execute(self, args, server_pub_key=None):
        if not self.dirs_prepared:
            self.prepare_directories()

        repo_dir = os.path.join(self.target_dir, 'config/repo')
        pub_key = open(os.path.join(repo_dir, 'zs-pub-key.pem')).read()

        repo_manager = RepoManager(repo_dir)
        repo_manager.ensure_repo_consistency()
        print('\nCreated a Bazaar repo in {repo_dir}'.format(repo_dir=repo_dir))

        print('')
        print('Creating files..')
        for file_name, contents in sorted(files.items()):
            file_name = os.path.join(self.target_dir, file_name)
            print('Creating {file_name}'.format(file_name=file_name))
            f = file(file_name, 'w')
            f.write(contents)
            f.close()

        logging_conf_loc = os.path.join(self.target_dir, 'config/repo/logging.conf')

        logging_conf = open(logging_conf_loc).read()
        open(logging_conf_loc, 'w').write(logging_conf.format(
            log_path=os.path.join(self.target_dir, 'logs', 'zato.log')))

        print('')
        print('Logging configuration stored in {logging_conf_loc}'.format(logging_conf_loc=logging_conf_loc))

        server_conf_loc = os.path.join(self.target_dir, 'config/repo/server.conf')
        server_conf = open(server_conf_loc, 'w')
        server_conf.write(server_conf_template.format(odb_db_name=args.odb_dbname,
                            odb_engine=args.odb_type,
                        odb_host=args.odb_host,
                        odb_password=encrypt(args.odb_password, pub_key),
                        odb_pool_size=default_odb_pool_size, 
                        odb_user=args.odb_user))
        server_conf.close()
        
        print('Core configuration stored in {server_conf_loc}'.format(server_conf_loc=server_conf_loc))

        msg = """\nSuccessfully created a new server.
You can now start it with the 'zato start {path}' command.
""".format(path=os.path.abspath(os.path.join(os.getcwd(), self.target_dir)))

        print(msg)

def main(target_dir):
    CreateServer(target_dir).run()

if __name__ == '__main__':
    main('.')
