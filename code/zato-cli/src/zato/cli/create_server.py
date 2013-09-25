# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, shutil, uuid
from copy import deepcopy
from datetime import datetime
from multiprocessing import cpu_count
from traceback import format_exc

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Zato
from zato.cli import ZatoCommand, common_logging_conf_contents, common_odb_opts, \
     kvdb_opts
from zato.common import SERVER_JOIN_STATUS
from zato.common.defaults import http_plain_server_port
from zato.common.odb.model import Cluster, Server
from zato.common.util import encrypt

server_conf_template = """[main]
gunicorn_bind=localhost:{port}
gunicorn_worker_class=gevent
gunicorn_workers={gunicorn_workers}
gunicorn_timeout=240
gunicorn_user=
gunicorn_group=
gunicorn_proc_name=
gunicorn_logger_class=

deployment_lock_expires=1073741824 # 2 ** 30 seconds ≅ 34 years
deployment_lock_timeout=180

token={token}
service_sources=./service-sources.txt

[crypto]
priv_key_location=zato-server-priv-key.pem
pub_key_location=zato-server-pub-key.pem
cert_location=zato-server-cert.pem
ca_certs_location=zato-server-ca-certs.pem

[odb]
db_name={odb_db_name}
engine={odb_engine}
extra=
host={odb_host}
port={odb_port}
password={odb_password}
pool_size={odb_pool_size}
username={odb_user}

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
""".encode('utf-8')

service_sources_contents = """# Visit https://zato.io/docs for more information.

# All paths are relative to server root so that, for instance,
# ./my-services will resolve to /opt/zato/server1/my-services if a server has been
# installed into /opt/zato/server1 

# List your service sources below, each on a separate line.

# Recommended to be always the very last line so all services that have been
# hot-deployed are picked up last.
./work/hot-deploy/current

# Visit https://zato.io/docs for more information."""

default_odb_pool_size = 1

directories = ('config', 'config/repo', 'config/zdaemon', 'pickup-dir', 'logs', 'work',
               'work/hot-deploy', 'work/hot-deploy/current', 'work/hot-deploy/backup', 'work/hot-deploy/backup/last')
files = {'config/repo/logging.conf':common_logging_conf_contents.format(log_path='./logs/server.log'),
         'config/repo/service-sources.txt':service_sources_contents}

priv_key_location = './config/repo/config-priv.pem'
pub_key_location = './config/repo/config-pub.pem'

class Create(ZatoCommand):
    """ Creates a new Zato server
    """
    needs_empty_dir = True
    allow_empty_secrets = True
    
    opts = deepcopy(common_odb_opts)
    opts.extend(kvdb_opts)
    
    opts.append({'name':'pub_key_path', 'help':"Path to the server's public key in PEM"})
    opts.append({'name':'priv_key_path', 'help':"Path to the server's private key in PEM"})
    opts.append({'name':'cert_path', 'help':"Path to the server's certificate in PEM"})
    opts.append({'name':'ca_certs_path', 'help':"Path to the a PEM list of certificates the server will trust"})
    opts.append({'name':'cluster_name', 'help':'Name of the cluster to join'})
    opts.append({'name':'server_name', 'help':"Server's name"})

    def __init__(self, args):
        super(Create, self).__init__(args)
        self.target_dir = os.path.abspath(args.path)
        self.dirs_prepared = False
        self.token = uuid.uuid4().hex

    def prepare_directories(self, show_output):
        if show_output:
            self.logger.debug('Creating directories..')
            
        for d in sorted(directories):
            d = os.path.join(self.target_dir, d)
            if show_output:
                self.logger.debug('Creating {d}'.format(d=d))
            os.mkdir(d)

        self.dirs_prepared = True

    def execute(self, args, port=http_plain_server_port, show_output=True):
        
        engine = self._get_engine(args)
        session = self._get_session(engine)
        
        cluster = session.query(Cluster).\
                   filter(Cluster.name == args.cluster_name).\
                   first()
        
        if not cluster:
            msg = "Cluster [{}] doesn't exist in the ODB".format(args.cluster_name)
            self.logger.error(msg)
            return self.SYS_ERROR.NO_SUCH_CLUSTER
        
        server = Server()
        server.cluster_id = cluster.id
        server.name = args.server_name
        server.token = self.token
        server.last_join_status = SERVER_JOIN_STATUS.ACCEPTED
        server.last_join_mod_by = self._get_user_host()
        server.last_join_mod_date = datetime.utcnow()
        
        session.add(server)

        try:
            if not self.dirs_prepared:
                self.prepare_directories(show_output)
    
            repo_dir = os.path.join(self.target_dir, 'config', 'repo')
            self.copy_server_crypto(repo_dir, args)
            pub_key = open(os.path.join(repo_dir, 'zato-server-pub-key.pem')).read()
            
            if show_output:
                self.logger.debug('Created a Bazaar repo in {}'.format(repo_dir))
                self.logger.debug('Creating files..')
                
            for file_name, contents in sorted(files.items()):
                file_name = os.path.join(self.target_dir, file_name)
                if show_output:
                    self.logger.debug('Creating {}'.format(file_name))
                f = file(file_name, 'w')
                f.write(contents)
                f.close()
    
            logging_conf_loc = os.path.join(self.target_dir, 'config/repo/logging.conf')
    
            logging_conf = open(logging_conf_loc).read()
            open(logging_conf_loc, 'w').write(logging_conf.format(
                log_path=os.path.join(self.target_dir, 'logs', 'zato.log')))
    
            if show_output:
                self.logger.debug('Logging configuration stored in {}'.format(logging_conf_loc))
    
            server_conf_loc = os.path.join(self.target_dir, 'config/repo/server.conf')
            server_conf = open(server_conf_loc, 'w')
            server_conf.write(
                server_conf_template.format(
                    port=port,
                    gunicorn_workers=cpu_count(),
                    odb_db_name=args.odb_db_name, 
                    odb_engine=args.odb_type, 
                    odb_host=args.odb_host,
                    odb_port=args.odb_port,
                    odb_password=encrypt(args.odb_password, pub_key), 
                    odb_pool_size=default_odb_pool_size, 
                    odb_user=args.odb_user, 
                    token=self.token, 
                    kvdb_host=args.kvdb_host,
                    kvdb_port=args.kvdb_port, 
                    kvdb_password=encrypt(args.kvdb_password, pub_key) if args.kvdb_password else '',
                    initial_cluster_name=args.cluster_name, 
                    initial_server_name=args.server_name, 
                    ))
            server_conf.close()
            
            if show_output:
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
            self.logger.error(msg)
            session.rollback()
        else:
            if show_output:
                self.logger.debug('Server added to the ODB')

        if show_output:
            if self.verbose:
                msg = """Successfully created a new server.
You can now start it with the 'zato start {}' command.""".format(self.target_dir)
                self.logger.debug(msg)
            else:
                self.logger.info('OK')
