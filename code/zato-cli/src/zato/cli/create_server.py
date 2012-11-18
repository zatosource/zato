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
from datetime import datetime
from multiprocessing import cpu_count

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Zato
from zato.cli import ZatoCommand, ZATO_SERVER_DIR, common_logging_conf_contents, common_odb_opts, \
     kvdb_opts
from zato.common import SERVER_JOIN_STATUS
from zato.common.defaults import http_plain_server_port
from zato.common.odb.model import Cluster, Server
from zato.common.util import encrypt
from zato.server.repo import RepoManager

server_conf_template = """[bind]
host=localhost
starting_port={starting_port}
parallel_count={parallel_count}

[crypto]
priv_key_location=zs-priv-key.pem
pub_key_location=zs-pub-key.pem
cert_location=zs-cert.pem
ca_certs_location=ca-chain.pem

[odb]
db_name={odb_db_name}
engine={odb_engine}
extra=
host={odb_host}
password={odb_password}
pool_size={odb_pool_size}
username={odb_user}
token={odb_token}

[hot_deploy]
pickup_dir=../../pickup-dir
work_dir=../../work
backup_history=100
backup_format=bztar

# These three are relative to work_dir
current_work_dir=./hot-deploy/current
backup_work_dir=./hot-deploy/backup
last_backup_work_dir=./hot-deploy/backup/last

[singleton]
initial_sleep_time=500

# If a server doesn't update its keep alive data in 
# connector_server_keep_alive_job_time * grace_time_multiplier seconds
# it will be considered down and another server from the cluster will assume
# the control of connectors
connector_server_keep_alive_job_time=30 # In seconds
grace_time_multiplier=3

[spring]
context_class=zato.server.spring_context.ZatoContext

[misc]
internal_services_may_be_deleted=False
initial_cluster_name = {initial_cluster_name}
initial_server_name = {initial_server_name}

[kvdb]
host={kvdb_host}
port={kvdb_port}
unix_socket_path=
password={kvdb_password}
db=0
socket_timeout=
charset=
errors=
"""

default_odb_pool_size = 1

directories = ('config', 'config/repo', 'config/zdaemon', 'pickup-dir', 'logs', 'work',
               'work/hot-deploy', 'work/hot-deploy/current', 'work/hot-deploy/backup', 'work/hot-deploy/backup/last')
files = {ZATO_SERVER_DIR: '',
         'config/repo/logging.conf':common_logging_conf_contents.format(log_path='./logs/server.log'),
}

priv_key_location = './config/repo/config-priv.pem'
pub_key_location = './config/repo/config-pub.pem'

class Create(ZatoCommand):
    needs_empty_dir = True
    allow_empty_secrets = True
    
    opts = deepcopy(common_odb_opts)
    opts.extend(deepcopy(kvdb_opts))
    
    opts.append({'name':'pub_key_path', 'help':"Path to the server's public key in PEM"})
    opts.append({'name':'priv_key_path', 'help':"Path to the server's private key in PEM"})
    opts.append({'name':'cert_path', 'help':"Path to the server's certificate in PEM"})
    opts.append({'name':'cluster_name', 'help':'Name of the cluster to join'})
    opts.append({'name':'server_name', 'help':"Server's name"})

    def __init__(self, args):
        super(Create, self).__init__(args)
        self.target_dir = os.path.abspath(args.path)
        self.dirs_prepared = False
        self.odb_token = uuid.uuid4().hex

    def prepare_directories(self):
        self.logger.debug('Creating directories..')
        for d in sorted(directories):
            d = os.path.join(self.target_dir, d)
            self.logger.debug('Creating {d}'.format(d=d))
            os.mkdir(d)

        self.dirs_prepared = True

    def execute(self, args, server_pub_key=None, starting_port=http_plain_server_port,
                parallel_count=cpu_count() * 2):
        
        engine = self._get_engine(args)
        session = self._get_session(engine)
        
        cluster = session.query(Cluster).\
                   filter(Cluster.name == args.cluster_name).\
                   first()
        
        if not cluster:
            msg = "Cluster [{}] doesn't exist in the ODB".format(args.cluster_name)
            return self.SYS_ERROR.NO_SUCH_CLUSTER
        
        server = Server()
        server.cluster_id = cluster.id
        server.name = args.server_name
        server.odb_token = self.odb_token
        server.last_join_status = SERVER_JOIN_STATUS.ACCEPTED
        server.last_join_mod_by = self._get_user_host()
        server.last_join_mod_date = datetime.utcnow()
        
        session.add(server)

        try:
            if not self.dirs_prepared:
                self.prepare_directories()
    
            repo_dir = os.path.join(self.target_dir, 'config/repo')
    
            shutil.copyfile(os.path.abspath(args.pub_key_path), os.path.join(repo_dir, 'zs-pub-key.pem'))
            shutil.copyfile(os.path.abspath(args.priv_key_path), os.path.join(repo_dir, 'zs-priv-key.pem'))
            shutil.copyfile(os.path.abspath(args.cert_path), os.path.join(repo_dir, 'zs-cert.pem'))
            
            pub_key = open(os.path.join(repo_dir, 'zs-pub-key.pem')).read()
    
            repo_manager = RepoManager(repo_dir)
            repo_manager.ensure_repo_consistency()
            self.logger.debug('Created a Bazaar repo in {}'.format(repo_dir))
    
            self.logger.debug('Creating files..')
            for file_name, contents in sorted(files.items()):
                file_name = os.path.join(self.target_dir, file_name)
                self.logger.debug('Creating {}'.format(file_name))
                f = file(file_name, 'w')
                f.write(contents)
                f.close()
    
            logging_conf_loc = os.path.join(self.target_dir, 'config/repo/logging.conf')
    
            logging_conf = open(logging_conf_loc).read()
            open(logging_conf_loc, 'w').write(logging_conf.format(
                log_path=os.path.join(self.target_dir, 'logs', 'zato.log')))
    
            self.logger.debug('Logging configuration stored in {}'.format(logging_conf_loc))
    
            server_conf_loc = os.path.join(self.target_dir, 'config/repo/server.conf')
            server_conf = open(server_conf_loc, 'w')
            server_conf.write(
                server_conf_template.format(
                    starting_port=starting_port,
                    parallel_count=parallel_count, 
                    odb_db_name=args.odb_db_name, 
                    odb_engine=args.odb_type, 
                    odb_host=args.odb_host,
                    odb_password=encrypt(args.odb_password, pub_key), 
                    odb_pool_size=default_odb_pool_size, 
                    odb_user=args.odb_user, 
                    odb_token=self.odb_token, 
                    kvdb_host=args.kvdb_host,
                    kvdb_port=args.kvdb_port, 
                    kvdb_password=encrypt(args.kvdb_password, pub_key) if args.kvdb_password else '',
                    initial_cluster_name=args.cluster_name, 
                    initial_server_name=args.server_name, 
                    ))
            server_conf.close()
            
            self.logger.debug('Core configuration stored in {}'.format(server_conf_loc))
            
            # Initial info
            self.store_initial_info(self.target_dir, self.COMPONENTS.SERVER.code)
            
            session.commit()

        except IntegrityError, e:
            msg = 'Server name [{}] already exists'.format(args.server_name)
            if self.verbose:
                msg += '. Caught an exception:[{}]'.format(format_exc(e))
                self.logger.error(msg)
            self.logger.error(msg)
            session.rollback()
            
            return self.SYS_ERROR.SERVER_NAME_ALREADY_EXISTS
            
        except Exception, e:
            msg = 'Could not create the server, e:[{}]'.format(format_exc(e))
            session.rollback()
        else:
            self.logger.debug('Server added to the ODB')        

        if self.verbose:
            msg = """Successfully created a new server.
You can now start it with the 'zato start {}' command.""".format(self.target_dir)
        else:
            self.logger.info('OK')
