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

# Cryptography
from cryptography.fernet import Fernet

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Zato
from zato.cli import ZatoCommand, common_logging_conf_contents, common_odb_opts, kvdb_opts
from zato.common import CONTENT_TYPE, SERVER_JOIN_STATUS
from zato.common.defaults import http_plain_server_port
from zato.common.odb.model import Cluster, Server
from zato.common.util import encrypt

server_conf_template = """[main]
gunicorn_bind=0.0.0.0:{{port}}
gunicorn_worker_class=gevent
gunicorn_workers={{gunicorn_workers}}
gunicorn_timeout=240
gunicorn_user=
gunicorn_group=
gunicorn_proc_name=
gunicorn_logger_class=
gunicorn_graceful_timeout=1

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
pickup_dir=../../pickup/incoming/services
work_dir=../../work
backup_history=100
backup_format=bztar
delete_after_pick_up=False

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
fifo_response_buffer_size=0.2 # In MB
jwt_secret={{jwt_secret}}
enforce_service_invokes=False
return_tracebacks=True
default_error_message="An error has occurred"

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
zato.kvdb.log-connection-info=
zato.pubsub.cleanup.delete-expired=10
zato.pubsub.cleanup.delete-delivered=10
zato.updates.check-updates=

[startup_services_any_worker]
zato.helpers.input-logger=Sample payload for a startup service (any worker)

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
live_msg_browser=False
cassandra=True
email=True
search=True
msg_path=True
websphere_mq=False
odoo=True
stomp=True
zeromq=True
patterns=True
target_matcher=False
invoke_matcher=False
sms=True

[live_msg_browser]
include_internal=False
service=True
out=True

[content_type]
json = {JSON}
plain_xml = {PLAIN_XML}
soap11 = {SOAP11}
soap12 = {SOAP12}

[zeromq_mdp]
linger=0
poll_interval=100
heartbeat=3
workers_pool_initial = 10
workers_pool_mult = 2
workers_pool_max = 250

[updates]
notify_major_versions=True
notify_minor_versions=True
notify_if_from_source=True

[preferred_address]
address=
ip=10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, eth0
boot_if_preferred_not_found=False
allow_loopback=False

[apispec]
pub_enabled=False
pub_name=API specification
pub_css_style="color:#eee; font-weight:bold; font-size:17px; padding-left:2px"

[shmem]
size=0.1 # In MB

[os_environ]
sample_key=sample_value
""".format(**CONTENT_TYPE).encode('utf-8')

pickup_conf = """[json]
pickup_from=./pickup/incoming/json
move_processed_to=./pickup/processed/json
patterns=*.json
recipients=zato.pickup.log-json
parse_with=py:rapidjson.loads

[xml]
pickup_from=./pickup/incoming/xml
move_processed_to=./pickup/processed/xml
patterns=*.xml
recipients=zato.pickup.log-xml
parse_with=py:lxml.objectify.fromstring

[csv]
pickup_from=./pickup/incoming/csv
move_processed_to=./pickup/processed/csv
patterns=*.csv
recipients=zato.pickup.log-csv
read_on_pickup=False
parse_on_pickup=False
delete_after_pickup=False

[user_conf]
pickup_from=./config/repo/user-conf
patterns=*.conf
recipients=zato.pickup.update-user-conf
parse_on_pickup=False

[static]
pickup_from=./pickup/incoming/static
patterns=*
recipients=zato.pickup.update-static
parse_on_pickup=False
"""

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
    'config/repo/user-conf',
    'logs',
    'pickup',
    'pickup/incoming',
    'pickup/processed',
    'pickup/incoming/services',
    'pickup/incoming/static',
    'pickup/incoming/json',
    'pickup/incoming/xml',
    'pickup/incoming/csv',
    'pickup/processed/static',
    'pickup/processed/json',
    'pickup/processed/xml',
    'pickup/processed/csv',
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
    opts.append({'name':'jwt_secret', 'help':"Server's JWT secret (must be the same for all servers in a cluster)"})

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
                    gunicorn_workers=1,
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
                    jwt_secret=getattr(args, 'jwt_secret', Fernet.generate_key()),
                ))
            server_conf.close()

            pickup_conf_loc = os.path.join(self.target_dir, 'config/repo/pickup.conf')
            pickup_conf_file = open(pickup_conf_loc, 'w')
            pickup_conf_file.write(pickup_conf)
            pickup_conf_file.close()

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
