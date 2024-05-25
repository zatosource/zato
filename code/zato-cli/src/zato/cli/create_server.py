# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from dataclasses import dataclass

# Zato
from zato.cli import common_odb_opts, common_scheduler_server_api_client_opts, common_scheduler_server_address_opts, \
    sql_conf_contents, ZatoCommand
from zato.common.api import CONTENT_TYPE, default_internal_modules, Default_Service_File_Data, NotGiven, SCHEDULER, \
     SSO as CommonSSO
from zato.common.crypto.api import ServerCryptoManager
from zato.common.simpleio_ import simple_io_conf_contents
from zato.common.util.api import as_bool, get_demo_py_fs_locations
from zato.common.util.config import get_scheduler_api_client_for_server_password, get_scheduler_api_client_for_server_username
from zato.common.util.open_ import open_r, open_w
from zato.common.events.common import Default as EventsDefault

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# For pyflakes
simple_io_conf_contents = simple_io_conf_contents

# ################################################################################################################################
# ################################################################################################################################

server_conf_dict = deepcopy(CONTENT_TYPE)
server_conf_dict.deploy_internal = {}

deploy_internal = []

for key, value in default_internal_modules.items():
    deploy_internal.append('{}={}'.format(key, value))

server_conf_dict.deploy_internal = '\n'.join(deploy_internal)

# ################################################################################################################################
# ################################################################################################################################

server_conf_template = """[main]
gunicorn_bind=0.0.0.0:{{port}}
gunicorn_worker_class=gevent
gunicorn_workers={{gunicorn_workers}}
gunicorn_timeout=1234567890
gunicorn_user=
gunicorn_group=
gunicorn_proc_name=
gunicorn_logger_class=
gunicorn_graceful_timeout=1
debugger_enabled=False
debugger_host=0.0.0.0
debugger_port=5678
ipc_host=127.0.0.1
ipc_port_start=17050

work_dir=../../work

deployment_lock_expires=1073741824 # 2 ** 30 seconds = +/- 34 years
deployment_lock_timeout=180

token=zato+secret://zato.server_conf.main.token
service_sources=./service-sources.txt

[http_response]
server_header=Zato
return_x_zato_cid=True
code_400_message=400 Bad Request
code_400_content_type=text/plain
code_401_message=401 Unauthorized
code_401_content_type=text/plain
code_403_message=403 Forbidden
code_403_content_type=text/plain
code_404_message=404 Not Found
code_404_content_type=text/plain
code_405_message=405 Not Allowed
code_405_content_type=text/plain
code_500_message=500 Internal Server Error
code_500_content_type=text/plain

[crypto]
use_tls=False
tls_version=TLSv1
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

[scheduler]
scheduler_host={{scheduler_host}}
scheduler_port={{scheduler_port}}
scheduler_use_tls={{scheduler_use_tls}}
scheduler_api_username={{scheduler_api_client_for_server_username}}
scheduler_api_password={{scheduler_api_client_for_server_password}}

[hot_deploy]
pickup_dir=../../pickup/incoming/services
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
queue_build_cap=30000000 # All queue-based connections need to initialize in that many seconds
http_proxy=
locale=
ensure_sql_connections_exist=True
http_server_header=Apache
needs_x_zato_cid=False
zeromq_connect_sleep=0.1
aws_host=
fifo_response_buffer_size=0.2 # In MB
jwt_secret=zato+secret://zato.server_conf.misc.jwt_secret
enforce_service_invokes=False
return_tracebacks=True
default_error_message="An error has occurred"
startup_callable=
return_json_schema_errors=False
sftp_genkey_command=dropbearkey
posix_ipc_skip_platform=darwin
service_invoker_allow_internal="pub.zato.ping", "/zato/api/invoke/service_name"

[events]
fs_data_path = {{events_fs_data_path}}
sync_threshold = {{events_sync_threshold}}
sync_interval = {{events_sync_interval}}

[http]
methods_allowed=GET, POST, DELETE, PUT, PATCH, HEAD, OPTIONS

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
stats=False
slow_response=True
cassandra=True
email=True
hl7=True
search=True
msg_path=True
ibm_mq=False
odoo=True
zeromq=True
patterns=True
target_matcher=False
invoke_matcher=False
sms=True
sso=True

[pubsub]
wsx_gateway_service_allowed=
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
json_library=stdlib
pings_missed_threshold=2
ping_interval=30

[content_type]
json = {JSON}

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
rest_log_ignore=/zato/admin/invoke,

[greenify]
#/path/to/oracle/instantclient_19_3/libclntsh.so.19.1=True

[os_environ]
sample_key=sample_value

[command_set_scheduler]

[deploy_internal]
{deploy_internal}

""".format(**server_conf_dict)

# ################################################################################################################################

pickup_conf = """#[hot-deploy.user.local-dev]
#pickup_from=/uncomment/this/stanza/to/enable/a/custom/location

[json]
pickup_from=./pickup/incoming/json
move_processed_to=./pickup/processed/json
patterns=*.json
parse_with=py:json.loads
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
patterns=*.ini, *.conf
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

# ################################################################################################################################

service_sources_contents = """
#
# This file is kept for backward compatibility with previous versions of Zato.
# Do not modify it and do not use it in new deployments.
#

./work/hot-deploy/current
""".strip()

# ################################################################################################################################

user_conf_contents = """[sample_section]
string_key=sample_string
list_key=sample,list
"""

# ################################################################################################################################

sso_conf_contents = '''[main]
encrypt_email=True
encrypt_password=True
email_service=
smtp_conn=
site_name=

[backend]
default=sql

[sql]
name=

[hash_secret]
rounds=120000
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
inform_if_totp_missing=True

[password_reset]
valid_for=1440 # In minutes = 1 day
password_change_session_duration=1800 # In seconds = 30 minutes
user_search_by=username
email_title_en_GB=Password reset
email_title_en_US=Password reset
email_from=hello@example.com

[user_address_list]

[session]
expiry=60 # In minutes
expiry_hook= # Name of a service that will return expiry value each time it is needed

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
min_complexity=0
min_complexity_algorithm=zxcvbn
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

# ################################################################################################################################

sso_confirm_template = """
Hello {username},

your account is almost ready - all we need to do is make sure that this is your email.

Use this link to confirm your address:

https://example.com/signup-confirm/{token}

If you did not want to create the account, just delete this email and everything will go back to the way it was.

ZATO_FOOTER_MARKER
Your Zato SSO team.
""".strip()

# ################################################################################################################################

sso_welcome_template = """
Hello {username},

thanks for joining us. Here are a couple great ways to get started:

* https://example.com/link/1
* https://example.com/link/2
* https://example.com/link/3

ZATO_FOOTER_MARKER
Your Zato SSO team.
""".strip()

sso_password_reset_template = """
Hello {username},

a password reset was recently requested on your {site_name} account. If this was you, please click the link below to update your password.

https://example.com/reset-password/{token}

This link will expire in {expiration_time_hours} hours.

If you do not want to reset your password, please ignore this message and the password will not be changed.

ZATO_FOOTER_MARKER
Your Zato SSO team.
""".strip()

# ################################################################################################################################

# We need to do it because otherwise IDEs may replace '-- ' with '--' (stripping the whitespace)
sso_confirm_template = sso_confirm_template.replace('ZATO_FOOTER_MARKER', '-- ')
sso_welcome_template = sso_welcome_template.replace('ZATO_FOOTER_MARKER', '-- ')
sso_password_reset_template = sso_password_reset_template.replace('ZATO_FOOTER_MARKER', '-- ')

# ################################################################################################################################

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

# ################################################################################################################################

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

# ################################################################################################################################

default_odb_pool_size = 60

# ################################################################################################################################

directories = (
    'config',
    'config/repo',
    'config/repo/lua',
    'config/repo/lua/internal',
    'config/repo/lua/user',
    'config/repo/schema',
    'config/repo/schema/json',
    'config/repo/sftp',
    'config/repo/sftp/channel',
    'config/repo/static',
    'config/repo/static/sso',
    'config/repo/static/sso/email',
    'config/repo/static/sso/email/en_GB',
    'config/repo/static/sso/email/en_US',
    'config/repo/tls',
    'config/repo/tls/keys-certs',
    'config/repo/tls/ca-certs',
    'logs',
    'pickup',
    'pickup/incoming',
    'pickup/processed',
    'pickup/incoming/services',
    'pickup/incoming/static',
    'pickup/incoming/user-conf',
    'pickup/incoming/json',
    'pickup/incoming/xml',
    'pickup/incoming/csv',
    'pickup/processed/static',
    'pickup/processed/user-conf',
    'pickup/processed/json',
    'pickup/processed/xml',
    'pickup/processed/csv',
    'profiler',
    'work',
    'work/events',
    'work/events/v1',
    'work/events/v2',
    'work/hot-deploy',
    'work/hot-deploy/current',
    'work/hot-deploy/backup',
    'work/hot-deploy/backup/last',
)

# ################################################################################################################################

priv_key_location = './config/repo/config-priv.pem'
priv_key_location = './config/repo/config-pub.pem'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SchedulerConfigForServer:
    scheduler_host: 'str'
    scheduler_port: 'int'
    scheduler_use_tls: 'bool'

    class api_client:

        class from_server_to_scheduler:
            username: 'str'
            password: 'str'

        class from_scheduler_to_server:
            username: 'str'
            password: 'str'

# ################################################################################################################################
# ################################################################################################################################

class Create(ZatoCommand):
    """ Creates a new Zato server
    """
    needs_empty_dir = True

    opts:'any_' = deepcopy(common_odb_opts)

    opts.append({'name':'cluster_name', 'help':'Name of the cluster to join'})
    opts.append({'name':'server_name', 'help':'Server\'s name'})
    opts.append({'name':'--pub-key-path', 'help':'Path to the server\'s public key in PEM'})
    opts.append({'name':'--priv-key-path', 'help':'Path to the server\'s private key in PEM'})
    opts.append({'name':'--cert-path', 'help':'Path to the server\'s certificate in PEM'})
    opts.append({'name':'--ca-certs-path', 'help':'Path to list of PEM certificates the server will trust'})
    opts.append({'name':'--secret-key', 'help':'Server\'s secret key (must be the same for all servers)'})
    opts.append({'name':'--jwt-secret', 'help':'Server\'s JWT secret (must be the same for all servers)'})
    opts.append({'name':'--http-port', 'help':'Server\'s HTTP port'})
    opts.append({'name':'--scheduler-host', 'help':'Deprecated. Use --scheduler-address-for-server instead.'})
    opts.append({'name':'--scheduler-port', 'help':'Deprecated. Use --scheduler-address-for-server instead.'})
    opts.append({'name':'--threads', 'help':'How many main threads the server should use', 'default':1}) # type: ignore

    opts += deepcopy(common_scheduler_server_address_opts)
    opts += deepcopy(common_scheduler_server_api_client_opts)

# ################################################################################################################################

    def __init__(self, args:'any_') -> 'None':

        # stdlib
        import os
        import uuid

        super(Create, self).__init__(args)
        self.target_dir = os.path.abspath(args.path)
        self.dirs_prepared = False
        self.token = uuid.uuid4().hex.encode('utf8')

# ################################################################################################################################

    def allow_empty_secrets(self):
        return True

# ################################################################################################################################

    def prepare_directories(self, show_output:'bool') -> 'None':

        # stdlib
        import os

        if show_output:
            self.logger.debug('Creating directories..')

        for d in sorted(directories):
            d = os.path.join(self.target_dir, d)
            if show_output:
                self.logger.debug('Creating %s', d)
            os.mkdir(d)

        self.dirs_prepared = True

# ################################################################################################################################

    def _get_scheduler_config(self, args:'any_', secret_key:'bytes') -> 'SchedulerConfigForServer':

        # stdlib
        import os

        # Local variables
        use_tls = NotGiven

        # Our response to produce
        out = SchedulerConfigForServer()

        # Extract basic information about the scheduler the server will be invoking ..
        use_tls, host, port = self._extract_address_data(
            args,
            'scheduler_address_for_server',
            'scheduler_host',
            'scheduler_port',
            SCHEDULER.DefaultHost,
            SCHEDULER.DefaultPort,
        )

        # .. now, we can assign host and port to the response ..
        out.scheduler_host = host
        out.scheduler_port = port

        # Extract API credentials
        cm = ServerCryptoManager.from_secret_key(secret_key)
        scheduler_api_client_for_server_username = get_scheduler_api_client_for_server_username(args)
        scheduler_api_client_for_server_password = get_scheduler_api_client_for_server_password(args, cm)

        out.api_client.from_server_to_scheduler.username = scheduler_api_client_for_server_username
        out.api_client.from_server_to_scheduler.password = scheduler_api_client_for_server_password

        # This can be overridden through environment variables
        env_keys = ['Zato_Server_To_Scheduler_Use_TLS', 'ZATO_SERVER_SCHEDULER_USE_TLS']
        for key in env_keys:
            if value := os.environ.get(key):
                use_tls = as_bool(value)
                break
        else:
            if use_tls is NotGiven:
                use_tls = False

        out.scheduler_use_tls = use_tls # type: ignore

        # .. finally, return the response to our caller.
        return out

# ################################################################################################################################

    def _add_demo_service(self, fs_location:'str', full_path:'str') -> 'None':

        with open_w(fs_location) as f:
            data = Default_Service_File_Data.format(**{
                'full_path': full_path,
            })
            _ = f.write(data)

# ################################################################################################################################

    def execute(
        self,
        args:'any_',
        default_http_port:'any_'=None,
        show_output:'bool'=True,
        return_server_id:'bool'=False
    ) -> 'int | None':

        # stdlib
        import os
        import platform
        from datetime import datetime
        from traceback import format_exc

        # Cryptography
        from cryptography.fernet import Fernet

        # SQLAlchemy
        from sqlalchemy.exc import IntegrityError

        # Python 2/3 compatibility
        from six import PY3

        # Zato
        from zato.cli._apispec_default import apispec_files
        from zato.common.api import SERVER_JOIN_STATUS
        from zato.common.crypto.const import well_known_data
        from zato.common.defaults import http_plain_server_port
        from zato.common.odb.model import Cluster, Server
        from zato.common.util.logging_ import get_logging_conf_contents

        logging_conf_contents = get_logging_conf_contents()

        files = {
            'config/repo/logging.conf': logging_conf_contents,
            'config/repo/service-sources.txt': service_sources_contents,
            'config/repo/lua/internal/zato.rename_if_exists.lua': lua_zato_rename_if_exists,
            'config/repo/sql.conf': sql_conf_contents,

            'config/repo/static/sso/email/en_GB/signup-confirm.txt': CommonSSO.EmailTemplate.SignupConfirm,
            'config/repo/static/sso/email/en_GB/signup-welcome.txt': CommonSSO.EmailTemplate.SignupWelcome,
            'config/repo/static/sso/email/en_GB/password-reset-link.txt': CommonSSO.EmailTemplate.PasswordResetLink,

            'config/repo/static/sso/email/en_US/signup-confirm.txt': CommonSSO.EmailTemplate.SignupConfirm,
            'config/repo/static/sso/email/en_US/signup-welcome.txt': CommonSSO.EmailTemplate.SignupWelcome,
            'config/repo/static/sso/email/en_US/password-reset-link.txt': CommonSSO.EmailTemplate.PasswordResetLink,
        }

        default_http_port = default_http_port or http_plain_server_port

        engine = self._get_engine(args)
        session = self._get_session(engine) # type: ignore

        cluster = session.query(Cluster).filter(Cluster.name == args.cluster_name).first() # type: ignore

        if not cluster:
            self.logger.error("Cluster `%s` doesn't exist in ODB", args.cluster_name)
            return self.SYS_ERROR.NO_SUCH_CLUSTER

        server = Server(cluster=cluster)
        server.name = args.server_name
        if isinstance(self.token, (bytes, bytearray)): # type: ignore
            server.token = self.token.decode('utf8') # type: ignore
        else:
            server.token = self.token
        server.last_join_status = SERVER_JOIN_STATUS.ACCEPTED # type: ignore
        server.last_join_mod_by = self._get_user_host() # type: ignore
        server.last_join_mod_date = datetime.utcnow() # type: ignore
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
                f = open_w(file_name)
                _ = f.write(contents)
                f.close()

            logging_conf_loc = os.path.join(self.target_dir, 'config/repo/logging.conf')

            logging_conf = open_r(logging_conf_loc).read()
            _ = open_w(logging_conf_loc).write(logging_conf.format(log_path=os.path.join(self.target_dir, 'logs', 'zato.log')))

            if show_output:
                self.logger.debug('Logging configuration stored in {}'.format(logging_conf_loc))

            odb_engine=args.odb_type
            if odb_engine.startswith('postgresql'):
                odb_engine = 'postgresql+pg8000'

            server_conf_loc = os.path.join(self.target_dir, 'config/repo/server.conf')
            server_conf = open_w(server_conf_loc)

            # There will be multiple keys in future releases to allow for key rotation
            secret_key = args.secret_key or Fernet.generate_key()

            try:
                threads = int(args.threads)
            except Exception:
                threads = 1

            # Build the scheduler's configuration
            scheduler_config = self._get_scheduler_config(args, secret_key)

            # Substitue the variables ..
            server_conf_data = server_conf_template.format(
                    port=getattr(args, 'http_port', None) or default_http_port,
                    gunicorn_workers=threads,
                    odb_db_name=args.odb_db_name or args.sqlite_path,
                    odb_engine=odb_engine,
                    odb_host=args.odb_host or '',
                    odb_port=args.odb_port or '',
                    odb_pool_size=default_odb_pool_size,
                    odb_user=args.odb_user or '',
                    kvdb_host=self.get_arg('kvdb_host'),
                    kvdb_port=self.get_arg('kvdb_port'),
                    initial_cluster_name=args.cluster_name,
                    initial_server_name=args.server_name,
                    events_fs_data_path=EventsDefault.fs_data_path,
                    events_sync_threshold=EventsDefault.sync_threshold,
                    events_sync_interval=EventsDefault.sync_interval,
                    scheduler_host=scheduler_config.scheduler_host,
                    scheduler_port=scheduler_config.scheduler_port,
                    scheduler_use_tls=scheduler_config.scheduler_use_tls,
                    scheduler_api_client_for_server_username=scheduler_config.api_client.from_server_to_scheduler.username,
                    scheduler_api_client_for_server_password=scheduler_config.api_client.from_server_to_scheduler.password,
                )

            # .. and special-case this one as it contains the {} characters
            # .. which makes it more complex to substitute them.
            server_conf_data = server_conf_data.replace('/zato/api/invoke/service_name', '/zato/api/invoke/{service_name}')

            _ = server_conf.write(server_conf_data)
            server_conf.close()

            pickup_conf_loc = os.path.join(self.target_dir, 'config/repo/pickup.conf')
            pickup_conf_file = open_w(pickup_conf_loc)
            _ = pickup_conf_file.write(pickup_conf)
            pickup_conf_file.close()

            user_conf_loc = os.path.join(self.target_dir, 'config/repo/user.conf')
            user_conf = open_w(user_conf_loc)
            _ = user_conf.write(user_conf_contents)
            user_conf.close()

            sso_conf_loc = os.path.join(self.target_dir, 'config/repo/sso.conf')
            sso_conf = open_w(sso_conf_loc)
            _ = sso_conf.write(sso_conf_contents)
            sso_conf.close()

            # On systems other than Windows, where symlinks are not fully supported,
            # for convenience and backward compatibility,
            # create a shortcut symlink from incoming/user-conf to config/repo/user-conf.

            system = platform.system()
            is_windows = 'windows' in system.lower()

            if not is_windows:
                user_conf_src = os.path.join(self.target_dir, 'pickup', 'incoming', 'user-conf')
                user_conf_dest = os.path.join(self.target_dir, 'config', 'repo', 'user-conf')
                os.symlink(user_conf_src, user_conf_dest)

            fernet1 = Fernet(secret_key)

            secrets_conf_loc = os.path.join(self.target_dir, 'config/repo/secrets.conf')
            secrets_conf = open_w(secrets_conf_loc)

            kvdb_password = self.get_arg('kvdb_password') or ''
            kvdb_password = kvdb_password.encode('utf8')
            kvdb_password = fernet1.encrypt(kvdb_password)
            kvdb_password = kvdb_password.decode('utf8')

            odb_password = self.get_arg('odb_password') or ''
            odb_password = odb_password.encode('utf8')
            odb_password = fernet1.encrypt(odb_password)
            odb_password = odb_password.decode('utf8')

            zato_well_known_data = fernet1.encrypt(well_known_data.encode('utf8'))
            zato_well_known_data = zato_well_known_data.decode('utf8')

            if isinstance(secret_key, (bytes, bytearray)):
                secret_key = secret_key.decode('utf8')

            zato_main_token = fernet1.encrypt(self.token)
            zato_main_token = zato_main_token.decode('utf8')

            zato_misc_jwt_secret = getattr(args, 'jwt_secret', None)
            if not zato_misc_jwt_secret:
                zato_misc_jwt_secret = Fernet.generate_key()

            if not isinstance(zato_misc_jwt_secret, bytes):
                zato_misc_jwt_secret = zato_misc_jwt_secret.encode('utf8')

            zato_misc_jwt_secret = fernet1.encrypt(zato_misc_jwt_secret)

            if isinstance(zato_misc_jwt_secret, bytes): # type: ignore
                zato_misc_jwt_secret = zato_misc_jwt_secret.decode('utf8')

            _ = secrets_conf.write(secrets_conf_template.format(
                keys_key1=secret_key,
                zato_well_known_data=zato_well_known_data,
                zato_kvdb_password=kvdb_password,
                zato_main_token=zato_main_token,
                zato_misc_jwt_secret=zato_misc_jwt_secret,
                zato_odb_password=odb_password,
            ))
            secrets_conf.close()

            bytes_to_str_encoding = 'utf8' if PY3 else ''

            simple_io_conf_loc = os.path.join(self.target_dir, 'config/repo/simple-io.conf')
            simple_io_conf = open_w(simple_io_conf_loc)
            _ = simple_io_conf.write(simple_io_conf_contents.format(
                bytes_to_str_encoding=bytes_to_str_encoding
            ))
            simple_io_conf.close()

            if show_output:
                self.logger.debug('Core configuration stored in {}'.format(server_conf_loc))

            # Prepare paths for the demo service ..
            demo_py_fs = get_demo_py_fs_locations(self.target_dir)

            # .. and create it now.
            self._add_demo_service(demo_py_fs.pickup_incoming_full_path, demo_py_fs.pickup_incoming_full_path)
            self._add_demo_service(demo_py_fs.work_dir_full_path, demo_py_fs.pickup_incoming_full_path)

            # Sphinx APISpec files
            for file_path, contents in apispec_files.items(): # type: ignore
                full_path = os.path.join(self.target_dir, 'config/repo/static/sphinxdoc/apispec', file_path)
                dir_name = os.path.dirname(full_path)
                try:
                    os.makedirs(dir_name, 0o770)
                except OSError:
                    # That is fine, the directory must have already created in one of previous iterations
                    pass
                finally:
                    api_file = open_w(full_path)
                    _ = api_file.write(contents)
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
            return server.id # type: ignore

# ################################################################################################################################
# ################################################################################################################################
