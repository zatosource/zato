# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

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

# Python 2/3 compatibility
from six import PY3

# Zato
from zato.cli import ZatoCommand, common_logging_conf_contents, common_odb_opts, kvdb_opts, sql_conf_contents
from zato.cli._apispec_default import apispec_files
from zato.common import CONTENT_TYPE, default_internal_modules, SERVER_JOIN_STATUS
from zato.common.crypto import well_known_data
from zato.common.defaults import http_plain_server_port
from zato.common.odb.model import Cluster, Server

# ################################################################################################################################

server_conf_dict = deepcopy(CONTENT_TYPE)
server_conf_dict.deploy_internal = {}

deploy_internal = []

for key, value in default_internal_modules.items():
    deploy_internal.append('{}={}'.format(key, value))

server_conf_dict.deploy_internal = '\n'.join(deploy_internal)

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

deployment_lock_expires=1073741824 # 2 ** 30 seconds = +/- 34 years
deployment_lock_timeout=180

token=zato+secret://zato.server_conf.main.token
service_sources=./service-sources.txt

[crypto]
use_tls=False
tls_protocol=TLSv1
tls_ciphers=ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA256:DHE-RSA-AES256-SHA:ECDHE-ECDSA-DES-CBC3-SHA:ECDHE-RSA-DES-CBC3-SHA:EDH-RSA-DES-CBC3-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:DES-CBC3-SHA:!DSS
tls_client_certs=optional
priv_key_location=zato-server-priv-key.pem
pub_key_location=zato-server-pub-key.pem
cert_location=zato-server-cert.pem
ca_certs_location=zato-server-ca-certs.pem

[odb]
db_name={{odb_db_name}}
engine={{odb_engine}}
extra=echo=False
host={{odb_host}}
port={{odb_port}}
password=zato+secret://zato.server_conf.odb.password
pool_size={{odb_pool_size}}
username={{odb_user}}
use_async_driver=True

[hot_deploy]
pickup_dir=../../pickup/incoming/services
work_dir=../../work
backup_history=100
backup_format=bztar
delete_after_pick_up=False
max_batch_size=1000 # In kilobytes, default is 1 megabyte
redeploy_on_parent_change=True

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
jwt_secret=zato+secret://zato.server_conf.misc.jwt_secret
enforce_service_invokes=False
return_tracebacks=True
default_error_message="An error has occurred"
startup_callable=
return_json_schema_errors=False

[http]
methods_allowed=GET, POST, DELETE, PUT, PATCH, HEAD, OPTIONS

[ibm_mq]
ipc_tcp_start_port=34567

[stats]
expire_after=168 # In hours, 168 = 7 days = 1 week

[kvdb]
host={{kvdb_host}}
port={{kvdb_port}}
unix_socket_path=
password=zato+secret://zato.server_conf.kvdb.password
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
zato.sso.cleanup.cleanup=300
zato.updates.check-updates=
pub.zato.channel.web-socket.cleanup-wsx=

[startup_services_any_worker]
zato.helpers.input-logger=Sample payload for a startup service (any worker)
pub.zato.channel.web-socket.cleanup-wsx=

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

[[auth_type_hook]]

[component_enabled]
stats=True
slow_response=True
cassandra=True
email=True
search=True
msg_path=True
ibm_mq=False
odoo=True
stomp=True
zeromq=True
patterns=True
target_matcher=False
invoke_matcher=False
sms=True
sso=False

[pubsub]
wsx_gateway_service_allowed=zato.pubsub.subscription.create-wsx-subscription, pubsub.subscription.get-list, pubsub.subscription.unsubscribe
log_if_deliv_server_not_found=True
log_if_wsx_deliv_server_not_found=False
data_prefix_len=2048
data_prefix_short_len=64
sk_server_table_columns=6, 15, 8, 6, 17, 75

[pubsub_meta_topic]
enabled=True
store_frequency=1

[pubsub_meta_endpoint_pub]
enabled=True
store_frequency=1
max_history=100
data_len=0

[pubsub_meta_endpoint_sub]
enabled=True
store_frequency=1
max_history=100
data_len=0

[wsx]
hook_service=

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

[shmem]
size=0.1 # In MB

[logging]
http_access_log_ignore=

[os_environ]
sample_key=sample_value

[deploy_internal]
{deploy_internal}

""".format(**server_conf_dict)


pickup_conf = """[json]
pickup_from=./pickup/incoming/json
move_processed_to=./pickup/processed/json
patterns=*.json
parse_with=py:rapidjson.loads
services=zato.pickup.log-json
topics=

[xml]
pickup_from=./pickup/incoming/xml
move_processed_to=./pickup/processed/xml
patterns=*.xml
parse_with=py:lxml.objectify.fromstring
services=zato.pickup.log-xml
topics=

[csv]
pickup_from=./pickup/incoming/csv
move_processed_to=./pickup/processed/csv
patterns=*.csv
read_on_pickup=False
parse_on_pickup=False
delete_after_pickup=False
services=zato.pickup.log-csv
topics=

[user_conf]
pickup_from=./pickup/incoming/user-conf
patterns=*.conf
parse_on_pickup=False
delete_after_pickup=False
services=zato.pickup.update-user-conf
topics=

[static]
pickup_from=./pickup/incoming/static
patterns=*
parse_on_pickup=False
delete_after_pickup=False
services=zato.pickup.update-static
topics=
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

sso_conf_contents = '''[main]
encrypt_email=True
encrypt_password=True
smtp_conn=

[backend]
default=sql

[sql]
name=

[hash_secret]
rounds=100000
salt_size=64 # In bytes = 512 bits

[apps]
all=CRM
default=CRM
http_header=X-Zato-SSO-Current-App
signup_allowed=
login_allowed=CRM
login_metadata_allowed=
inform_if_app_invalid=True

[login]
reject_if_not_listed=False
inform_if_locked=True
inform_if_not_confirmed=True
inform_if_not_approved=True

[user_address_list]

[session]
expiry=60 # In minutes

[password]
expiry=730 # In days, 365 days * 2 years = 730 days
inform_if_expired=False
inform_if_about_to_expire=True
inform_if_must_be_changed=True
inform_if_invalid=True
about_to_expire_threshold=30 # In days
log_in_if_about_to_expire=True
min_length=8
max_length=256
reject_list = """
  111111
  123123
  123321
  123456
  123qwe
  1q2w3e
  1q2w3e4r
  1q2w3e4r5t
  222222
  333333
  444444
  555555
  654321
  666666
  777777
  888888
  999999
  987654321
  google
  letmein
  mynoob
  password
  qwerty
  zxcvbnm
"""

[signup]
inform_if_user_exists=False
inform_if_user_invalid=False
inform_if_email_exists=False
inform_if_email_invalid=False
email_required=True
max_length_username=128
max_length_email=128
password_allow_whitespace=True
always_return_confirm_token=True
is_email_required=True
is_approval_needed=True
callback_service_list=

email_confirm_enabled=True
email_confirm_from=confirm@example.com
email_confirm_cc=
email_confirm_bcc=
email_confirm_template=sso-confirm.txt

email_welcome_enabled=True
email_welcome_from=welcome@example.com
email_welcome_cc=
email_welcome_bcc=
email_welcome_template=sso-welcome.txt

[user_validation]
service=zato.sso.signup.validate
reject_username=zato, admin, root, system, sso
reject_email=zato, admin, root, system, sso

[search]
default_page_size=50
max_page_size=100
'''

sso_confirm_template = """
Hello {data.display_name},

your account is almost ready - all we need to do is make sure that this is your email.

Use this URL to confirm your address:

https://example.com/zato/sso/confirm?token={data.token}

If you didn't want to create the account, just delete this email and everything will go back to the way it was.

--
Your Zato SSO team.
""".strip()

sso_welcome_template = """
Hello {data.display_name}!

Thanks for joining us. Here are a couple great ways to get started:

* https://example.com/link/1
* https://example.com/link/2
* https://example.com/link/3

--
Your Zato SSO team.
""".strip()

secrets_conf_template = """
[secret_keys]
key1={keys_key1}

[zato]
well_known_data={zato_well_known_data} # Pi number
server_conf.kvdb.password={zato_kvdb_password}
server_conf.main.token={zato_main_token}
server_conf.misc.jwt_secret={zato_misc_jwt_secret}
server_conf.odb.password={zato_odb_password}
"""

simple_io_conf_contents = """
[int]
exact=id
suffix=_count, _id, _size, _size_min, _size_max, _timeout

[bool]
prefix=by_, has_, is_, may_, needs_, should_

[secret]
exact=auth_data, auth_token, password, password1, password2, secret, secret_key, tls_pem_passphrase, token

[bytes_to_str]
encoding={bytes_to_str_encoding}
""".lstrip()

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

default_odb_pool_size = 15

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
    'pickup/incoming/user-conf',
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
    'config/repo/schema',
    'config/repo/schema/json',
    'config/repo/static',
    'config/repo/static/email',
    'config/repo/tls',
    'config/repo/tls/keys-certs',
    'config/repo/tls/ca-certs',
)

files = {
    'config/repo/logging.conf': common_logging_conf_contents.format(log_path='./logs/server.log'),
    'config/repo/service-sources.txt': service_sources_contents,
    'config/repo/lua/internal/zato.rename_if_exists.lua': lua_zato_rename_if_exists,
    'config/repo/sql.conf': sql_conf_contents,
    'config/repo/static/email/sso-confirm.txt': sso_confirm_template,
    'config/repo/static/email/sso-welcome.txt': sso_welcome_template,
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

    opts.append({'name':'cluster_name', 'help':'Name of the cluster to join'})
    opts.append({'name':'server_name', 'help':"Server's name"})
    opts.append({'name':'--pub_key_path', 'help':"Path to the server's public key in PEM"})
    opts.append({'name':'--priv_key_path', 'help':"Path to the server's private key in PEM"})
    opts.append({'name':'--cert_path', 'help':"Path to the server's certificate in PEM"})
    opts.append({'name':'--ca_certs_path', 'help':"Path to list of PEM certificates the server will trust"})
    opts.append({'name':'--secret_key', 'help':"Server's secret key (must be the same for all servers)"})
    opts.append({'name':'--jwt_secret', 'help':"Server's JWT secret (must be the same for all servers)"})
    opts.append({'name':'--http_port', 'help':"Server's HTTP port"})

    def __init__(self, args):
        super(Create, self).__init__(args)
        self.target_dir = os.path.abspath(args.path)
        self.dirs_prepared = False
        self.token = uuid.uuid4().hex.encode('utf8')

    def prepare_directories(self, show_output):
        if show_output:
            self.logger.debug('Creating directories..')

        for d in sorted(directories):
            d = os.path.join(self.target_dir, d)
            if show_output:
                self.logger.debug('Creating %s', d)
            os.mkdir(d)

        self.dirs_prepared = True

    def execute(self, args, default_http_port=http_plain_server_port, show_output=True, return_server_id=False):

        engine = self._get_engine(args)
        session = self._get_session(engine)

        cluster = session.query(Cluster).\
            filter(Cluster.name == args.cluster_name).\
            first()

        if not cluster:
            self.logger.error("Cluster `%s` doesn't exist in ODB", args.cluster_name)
            return self.SYS_ERROR.NO_SUCH_CLUSTER

        server = Server(cluster=cluster)
        server.name = args.server_name
        if isinstance(self.token, (bytes, bytearray)):
            server.token = self.token.decode('utf8')
        else:
            server.token = self.token
        server.last_join_status = SERVER_JOIN_STATUS.ACCEPTED
        server.last_join_mod_by = self._get_user_host()
        server.last_join_mod_date = datetime.utcnow()
        session.add(server)

        try:
            if not self.dirs_prepared:
                self.prepare_directories(show_output)

            repo_dir = os.path.join(self.target_dir, 'config', 'repo')

            # Note that server crypto material is optional so if none was given on input
            # this command will be a no-op.
            self.copy_server_crypto(repo_dir, args)

            if show_output:
                self.logger.debug('Created a repo in {}'.format(repo_dir))
                self.logger.debug('Creating files..')

            for file_name, contents in sorted(files.items()):
                file_name = os.path.join(self.target_dir, file_name)
                if show_output:
                    self.logger.debug('Creating {}'.format(file_name))
                f = open(file_name, 'w')
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
                    port=getattr(args, 'http_port', None) or default_http_port,
                    gunicorn_workers=1,
                    odb_db_name=args.odb_db_name or args.sqlite_path,
                    odb_engine=odb_engine,
                    odb_host=args.odb_host or '',
                    odb_port=args.odb_port or '',
                    odb_pool_size=default_odb_pool_size,
                    odb_user=args.odb_user or '',
                    kvdb_host=args.kvdb_host,
                    kvdb_port=args.kvdb_port,
                    initial_cluster_name=args.cluster_name,
                    initial_server_name=args.server_name,
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

            sso_conf_loc = os.path.join(self.target_dir, 'config/repo/sso.conf')
            sso_conf = open(sso_conf_loc, 'w')
            sso_conf.write(sso_conf_contents)
            sso_conf.close()

            # There will be multiple keys in future releases to allow for key rotation
            key1 = args.secret_key or Fernet.generate_key()
            fernet1 = Fernet(key1)

            secrets_conf_loc = os.path.join(self.target_dir, 'config/repo/secrets.conf')
            secrets_conf = open(secrets_conf_loc, 'w')

            kvdb_password = args.kvdb_password or ''
            kvdb_password = kvdb_password.encode('utf8')
            kvdb_password = fernet1.encrypt(kvdb_password)
            kvdb_password = kvdb_password.decode('utf8')

            odb_password = args.odb_password or ''
            odb_password = odb_password.encode('utf8')
            odb_password = fernet1.encrypt(odb_password)
            odb_password = odb_password.decode('utf8')

            zato_well_known_data = fernet1.encrypt(well_known_data.encode('utf8'))
            zato_well_known_data = zato_well_known_data.decode('utf8')

            if isinstance(key1, (bytes, bytearray)):
                key1 = key1.decode('utf8')

            zato_main_token = fernet1.encrypt(self.token)
            zato_main_token = zato_main_token.decode('utf8')

            zato_misc_jwt_secret = getattr(args, 'jwt_secret', None)
            if not zato_misc_jwt_secret:
                zato_misc_jwt_secret = Fernet.generate_key()

            zato_misc_jwt_secret = fernet1.encrypt(zato_misc_jwt_secret)

            if isinstance(zato_misc_jwt_secret, bytes):
                zato_misc_jwt_secret = zato_misc_jwt_secret.decode('utf8')

            secrets_conf.write(secrets_conf_template.format(
                keys_key1=key1,
                zato_well_known_data=zato_well_known_data,
                zato_kvdb_password=kvdb_password,
                zato_main_token=zato_main_token,
                zato_misc_jwt_secret=zato_misc_jwt_secret,
                zato_odb_password=odb_password,
            ))
            secrets_conf.close()

            bytes_to_str_encoding = 'utf8' if PY3 else ''

            simple_io_conf_loc = os.path.join(self.target_dir, 'config/repo/simple-io.conf')
            simple_io_conf = open(simple_io_conf_loc, 'w')
            simple_io_conf.write(simple_io_conf_contents.format(
                bytes_to_str_encoding=bytes_to_str_encoding
            ))
            simple_io_conf.close()

            if show_output:
                self.logger.debug('Core configuration stored in {}'.format(server_conf_loc))

            # Sphinx APISpec files
            for file_path, contents in apispec_files.items():
                full_path = os.path.join(self.target_dir, 'config/repo/static/sphinxdoc/apispec', file_path)
                dir_name = os.path.dirname(full_path)
                try:
                    os.makedirs(dir_name, 0o770)
                except OSError:
                    # That is fine, the directory must have already created in one of previous iterations
                    pass
                finally:
                    api_file = open(full_path, 'w')
                    api_file.write(contents)
                    api_file.close()

            # Initial info
            self.store_initial_info(self.target_dir, self.COMPONENTS.SERVER.code)

            session.commit()

        except IntegrityError:
            msg = 'Server name `{}` already exists'.format(args.server_name)
            if self.verbose:
                msg += '. Caught an exception:`{}`'.format(format_exc())
            self.logger.error(msg)
            session.rollback()

            return self.SYS_ERROR.SERVER_NAME_ALREADY_EXISTS

        except Exception:
            self.logger.error('Could not create the server, e:`%s`', format_exc())
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

        # This is optional - need only by quickstart.py and needs to be requested explicitly,
        # otherwise it would be construed as a non-0 return code from this process.
        if return_server_id:
            return server.id
