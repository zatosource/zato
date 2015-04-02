# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, uuid
from copy import deepcopy
from datetime import datetime
from traceback import format_exc

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Zato
from zato.cli import ZatoCommand, common_logging_conf_contents, common_odb_opts, kvdb_opts
from zato.common import CONTENT_TYPE, SERVER_JOIN_STATUS
from zato.common.defaults import http_plain_server_port
from zato.common.odb.model import Cluster, Server
from zato.common.util import encrypt

server_conf_template = """[main]
gunicorn_bind=localhost:{{port}}
gunicorn_worker_class=gevent
gunicorn_workers={{gunicorn_workers}}
gunicorn_timeout=240
gunicorn_user=
gunicorn_group=
gunicorn_proc_name=
gunicorn_logger_class=

deployment_lock_expires=1073741824 # 2 ** 30 seconds ≅ 34 years
deployment_lock_timeout=180

token={{token}}
service_sources=./service-sources.txt

[crypto]
use_tls=False
tls_protocol=TLSv1
tls_ciphers=EECDH+AES:EDH+AES:-SHA1:EECDH+RC4:EDH+RC4:RC4-SHA:EECDH+AES256:EDH+AES256:AES256-SHA:!aNULL:!eNULL:!EXP:!LOW:!MD5
tls_client_certs=optional
priv_key_location=zato-server-priv-key.pem
pub_key_location=zato-server-pub-key.pem
cert_location=zato-server-cert.pem
ca_certs_location=zato-server-ca-certs.pem

[odb]
db_name={{odb_db_name}}
engine={{odb_engine}}
extra=
host={{odb_host}}
port={{odb_port}}
password={{odb_password}}
pool_size={{odb_pool_size}}
username={{odb_user}}
use_async_driver=True

[hot_deploy]
pickup_dir=../../pickup-dir
work_dir=../../work
backup_history=100
backup_format=bztar
delete_after_pick_up=True

# These three are relative to work_dir
current_work_dir=./hot-deploy/current
backup_work_dir=./hot-deploy/backup
last_backup_work_dir=./hot-deploy/backup/last

[deploy_patterns_allowed]
order=true_false
*=True

[invoke_patterns_allowed]
order=true_false
*=True

[invoke_target_patterns_allowed]
order=true_false
*=True

[singleton]
initial_sleep_time=2500

# If a server doesn't update its keep alive data in
# connector_server_keep_alive_job_time * grace_time_multiplier seconds
# it will be considered down and another server from the cluster will assume
# the control of connectors
connector_server_keep_alive_job_time=30 # In seconds
grace_time_multiplier=3

[spring]
context_class=zato.server.spring_context.ZatoContext

[misc]
return_internal_objects=False
internal_services_may_be_deleted=False
initial_cluster_name={{initial_cluster_name}}
initial_server_name={{initial_server_name}}
queue_build_cap=30 # All queue-based connections need to initialize in that many seconds
http_proxy=
locale=
ensure_sql_connections_exist=True
http_server_header=Zato
zeromq_connect_sleep=0.1
aws_host=
use_soap_envelope=True

[stats]
expire_after=168 # In hours, 168 = 7 days = 1 week

[kvdb]
host={{kvdb_host}}
port={{kvdb_port}}
unix_socket_path=
password={{kvdb_password}}
db=0
socket_timeout=
charset=
errors=
use_redis_sentinels=False
redis_sentinels=
redis_sentinels_master=
shadow_password_in_logs=True
log_connection_info_sleep_time=5 # In seconds

[startup_services_first_worker]
zato.helpers.input-logger=Sample payload for a startup service (first worker)
zato.notif.init-notifiers=
zato.pubsub.move-to-target-queues=
zato.pubsub.delete-expired=
zato.pubsub.invoke-callbacks=
zato.kvdb.log-connection-info=

[startup_services_any_worker]
zato.helpers.input-logger=Sample payload for a startup service (any worker)

[pubsub]
move_to_target_queues_interval=3 # In seconds
delete_expired_interval=180 # In seconds
invoke_callbacks_interval=2 # In seconds

[profiler]
enabled=False
profiler_dir=profiler
log_filename=profiler.log
cachegrind_filename=cachegrind.out
discard_first_request=True
flush_at_shutdown=True
url_path=/zato-profiler
unwind=False

[user_config]
# All paths are either absolute or relative to the directory server.conf is in
user=./user.conf

[newrelic]
config=
environment=
ignore_errors=
log_file=
log_level=

[sentry]
dsn=
timeout=5
level=WARN

[rbac]
custom_auth_list_service=

[component_enabled]
stats=True
slow_response=True

[content_type]
json = {JSON}
plain_xml = {PLAIN_XML}
soap11 = {SOAP11}
soap12 = {SOAP12}

[os_environ]
sample_key=sample_value
""".format(**CONTENT_TYPE).encode('utf-8')

service_sources_contents = """# Visit https://zato.io/docs for more information.

# All paths are relative to server root so that, for instance,
# ./my-services will resolve to /opt/zato/server1/my-services if a server has been
# installed into /opt/zato/server1

# List your service sources below, each on a separate line.

# Recommended to be always the very last line so all services that have been
# hot-deployed are picked up last.
./work/hot-deploy/current

# Visit https://zato.io/docs for more information."""

user_conf_contents = """[sample_section]
string_key=sample_string
list_key=sample,list

"""

lua_zato_rename_if_exists = """
-- Checks whether a from_key exists and if it does renames it to to_key.
-- Returns an error code otherwise.

-- Return codes:
-- 10 = Ok, renamed from_key -> to_key
-- 11 = No such from_key

local from_key = KEYS[1]
local to_key = KEYS[2]

if redis.call('exists', from_key) == 1 then
    redis.call('rename', from_key, to_key)
    return 10
else
    return 11
end
"""

default_odb_pool_size = 1

directories = (
    'config',
    'config/repo',
    'logs',
    'pickup-dir',
    'profiler',
    'work',
    'work/hot-deploy',
    'work/hot-deploy/current',
    'work/hot-deploy/backup',
    'work/hot-deploy/backup/last',
    'config/repo/lua',
    'config/repo/lua/internal',
    'config/repo/lua/user',
    'config/repo/static',
    'config/repo/tls',
    'config/repo/tls/keys-certs',
    'config/repo/tls/ca-certs',
)

files = {
    'config/repo/logging.conf':common_logging_conf_contents.format(log_path='./logs/server.log'),
    'config/repo/service-sources.txt':service_sources_contents,
    'config/repo/lua/internal/zato.rename_if_exists.lua':lua_zato_rename_if_exists
}

priv_key_location = './config/repo/config-priv.pem'
priv_key_location = './config/repo/config-pub.pem'

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
            priv_key = open(os.path.join(repo_dir, 'zato-server-priv-key.pem')).read()
            
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

            odb_engine=args.odb_type
            if odb_engine.startswith('postgresql'):
                odb_engine = 'postgresql+pg8000'

            server_conf_loc = os.path.join(self.target_dir, 'config/repo/server.conf')
            server_conf = open(server_conf_loc, 'w')
            server_conf.write(
                server_conf_template.format(
                    port=port,
                    gunicorn_workers=2,
                    odb_db_name=args.odb_db_name or args.sqlite_path,
                    odb_engine=odb_engine,
                    odb_host=args.odb_host or '',
                    odb_port=args.odb_port or '',
                    odb_password=encrypt(args.odb_password, priv_key) if args.odb_password else '',  
                    odb_pool_size=default_odb_pool_size, 
                    odb_user=args.odb_user or '', 
                    token=self.token, 
                    kvdb_host=args.kvdb_host,
                    kvdb_port=args.kvdb_port,
                    kvdb_password=encrypt(args.kvdb_password, priv_key) if args.kvdb_password else '',
                    initial_cluster_name=args.cluster_name,
                    initial_server_name=args.server_name,
                ))
            server_conf.close()

            user_conf_loc = os.path.join(self.target_dir, 'config/repo/user.conf')
            user_conf = open(user_conf_loc, 'w')
            user_conf.write(user_conf_contents)
            user_conf.close()

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
