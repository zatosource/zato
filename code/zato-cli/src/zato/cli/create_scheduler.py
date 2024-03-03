# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""


# stdlib
import os
import sys
from copy import deepcopy
from dataclasses import dataclass

# Bunch
from bunch import Bunch

# Zato
from zato.cli import common_odb_opts, common_scheduler_server_api_client_opts, sql_conf_contents, ZatoCommand
from zato.common.api import SCHEDULER
from zato.common.crypto.api import SchedulerCryptoManager
from zato.common.crypto.const import well_known_data
from zato.common.odb.model import Cluster
from zato.common.scheduler import startup_jobs
from zato.common.util.config import get_scheduler_api_client_for_server_auth_required, \
    get_scheduler_api_client_for_server_password, get_scheduler_api_client_for_server_username
from zato.common.util.open_ import open_w
from zato.common.util.platform_ import is_linux

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from argparse import Namespace
    from zato.common.typing_ import any_, anydict, strdict
    Namespace = Namespace

# ################################################################################################################################
# ################################################################################################################################

config_template = """[bind]
host={scheduler_bind_host}
port={scheduler_bind_port}

[cluster]
id=1
stats_enabled=False

[server]
server_path={server_path}
server_host={server_host}
server_port={server_port}
server_username={server_username}
server_password={server_password}
server_use_tls=False
server_tls_verify=True

[misc]
initial_sleep_time={initial_sleep_time}

[odb]
engine={odb_engine}
db_name={odb_db_name}
host={odb_host}
port={odb_port}
username={odb_username}
password={odb_password}
pool_size=1
extra=
use_async_driver=True
is_active=True

[secret_keys]
key1={secret_key1}

[crypto]
well_known_data={well_known_data}
use_tls={tls_use}
tls_version={tls_version}
tls_ciphers={tls_ciphers}
tls_client_certs={tls_client_certs}
priv_key_location={tls_priv_key_location}
pub_key_location={tls_pub_key_location}
cert_location={tls_cert_location}
ca_certs_location={tls_ca_certs_location}

[api_clients]
auth_required={scheduler_api_client_for_server_auth_required}
{scheduler_api_client_for_server_username}={scheduler_api_client_for_server_password}

[command_pause]

[command_resume]

[command_set_server]
"""

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ServerConfigForScheduler:
    host: 'str'
    port: 'int'
    use_tls: 'bool'
    is_auth_from_server_required: 'bool'

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
    """ Creates a new scheduler instance.
    """
    needs_empty_dir = True

    # Redis options are no longer used by they are kept here for pre-3.2 backward compatibility
    opts:'any_' = deepcopy(common_odb_opts)

    opts.append({'name':'--pub-key-path', 'help':'Path to scheduler\'s public key in PEM'})
    opts.append({'name':'--priv-key-path', 'help':'Path to scheduler\'s private key in PEM'})
    opts.append({'name':'--cert-path', 'help':'Path to the admin\'s certificate in PEM'})
    opts.append({'name':'--ca-certs-path', 'help':'Path to a bundle of CA certificates to be trusted'})
    opts.append({'name':'--cluster-name', 'help':'Name of the cluster this scheduler will belong to'})
    opts.append({'name':'--cluster-id', 'help':'ID of the cluster this scheduler will belong to'})
    opts.append({'name':'--secret-key', 'help':'Scheduler\'s secret crypto key'})

    opts.append({'name':'--server-path', 'help':'Local path to a Zato server'})

    opts.append({'name':'--server-host', 'help':'Deprecated. Use --server-address-for-scheduler instead.'})
    opts.append({'name':'--server-port', 'help':'Deprecated. Use --server-address-for-scheduler instead.'})

    opts.append({'name':'--server-username', 'help':'An alias to --server-api-client-for-scheduler-username'})
    opts.append({'name':'--server-password', 'help':'An alias to --server-api-client-for-scheduler-password'})

    opts.append({'name':'--bind-host', 'help':'Local address to start the scheduler on'})
    opts.append({'name':'--bind-port', 'help':'Local TCP port to start the scheduler on'})

    opts.append({'name':'--tls-enabled', 'help':'Whether the scheduler should use TLS'})
    opts.append({'name':'--tls-version', 'help':'What TLS version to use'})

    opts.append({'name':'--tls-ciphers', 'help':'What TLS ciphers to use'})
    opts.append({'name':'--tls-client-certs', 'help':'Whether TLS client certificates are required or optional'})

    opts.append({'name':'--tls-priv-key-location', 'help':'Scheduler\'s private key location'})
    opts.append({'name':'--tls-pub-key-location', 'help':'Scheduler\'s public key location'})
    opts.append({'name':'--tls-cert', 'help':'Scheduler\'s certificate location'})
    opts.append({'name':'--tls-ca-certs', 'help':'Scheduler\'s CA certificates location'})

    opts.append({'name':'--initial-sleep-time', 'help':'How many seconds to sleep initially when the scheduler starts'})

    opts += deepcopy(common_scheduler_server_api_client_opts)

# ################################################################################################################################

    def __init__(self, args:'any_') -> 'None':
        self.target_dir = os.path.abspath(args.path)
        super(Create, self).__init__(args)

# ################################################################################################################################

    def allow_empty_secrets(self):
        return True

# ################################################################################################################################

    def _get_cluster_id(self, args:'any_') -> 'any_':
        engine = self._get_engine(args)
        session = self._get_session(engine) # type: ignore

        cluster_id_list = session.query(Cluster.id).all() # type: ignore

        if not cluster_id_list:
            raise Exception('No cluster found in `{}`'.format(args))
        else:

            cluster_id_list.sort()
            return cluster_id_list[0][0] # type: ignore

# ################################################################################################################################

    def _get_server_admin_invoke_credentials(self, cm:'SchedulerCryptoManager', odb_config:'anydict') -> 'any_':

        # Zato
        from zato.common.util.api import get_server_client_auth

        _config = Bunch()

        _config_odb = Bunch()
        _config.odb = _config_odb

        _config_odb.engine = odb_config['odb_engine']
        _config_odb.username = odb_config['odb_username']
        _config_odb.password = odb_config['odb_password']
        _config_odb.host = odb_config['odb_host']
        _config_odb.port = odb_config['odb_port']
        _config_odb.db_name = odb_config['odb_db_name']

        server_username, server_password = get_server_client_auth(_config, None, cm, True)

        return server_username, server_password

# ################################################################################################################################

    def _get_server_config(self, args:'any_', secret_key:'bytes', odb_config:'strdict') -> 'ServerConfigForScheduler':

        # stdlib
        import os
        from urllib.parse import urlparse

        # Our response to produce
        out = ServerConfigForScheduler()

        '''
        scheduler_api_client_for_server_auth_required = get_scheduler_api_client_for_server_auth_required(args)
        scheduler_api_client_for_server_username = get_scheduler_api_client_for_server_username(args)
        scheduler_api_client_for_server_password = get_scheduler_api_client_for_server_password(args, cm)

        server_path = self.get_arg('server_path') or ''
        server_host = self.get_arg('server_host', '127.0.0.1')
        server_port = self.get_arg('server_port', 17010)

        server_username = self.get_arg('server_username', '')
        server_password = self.get_arg('server_password', '')

        # We enter this branch if we have credentials given on input ..
        if server_username or server_password:
            if server_username:
                if not server_password:
                    self.logger.warn('Server password is required if server username is provided')
                    sys.exit(self.SYS_ERROR.INVALID_INPUT)

            if server_password:
                if not server_username:
                    self.logger.warn('Server username is required if server password is provided')
                    sys.exit(self.SYS_ERROR.INVALID_INPUT)

        # .. we enter this branch if server credentials needed to be looked up in the ODB.
        else:
            server_username, server_password = self._get_server_admin_invoke_credentials(cm, odb_config)

        # .. encrypt the password before making use of it ..
        server_password = cm.encrypt(server_password, needs_str=True)
        '''

        '''
        # Try to Extract the scheduler's address from a single option
        if scheduler_address := args.scheduler_address_for_server:

            # Make sure we have a scheme ..
            if not '://' in scheduler_address:
                scheduler_address = 'https://' + scheduler_address

            # .. parse out the individual components ..
            scheduler_address = urlparse(scheduler_address)

            # .. now we know if TLS should be used ..
            use_tls = scheduler_address.scheme == 'https'

            # .. extract the host and port ..
            address = scheduler_address.netloc.split(':')
            host = address[0]

            if len(address) == 2:
                port = address[1]
            else:
                port = SCHEDULER.DefaultPort

        else:
            # Extract the scheduler's address from individual pieces
            host = self.get_arg('scheduler_host', SCHEDULER.DefaultHost)
            port = self.get_arg('scheduler_port', SCHEDULER.DefaultPort)

        # .. now, we can assign host and port to the response ..
        out.host = host
        out.port = port

        # Extract API credentials
        cm = ServerCryptoManager.from_secret_key(secret_key)
        scheduler_api_client_for_server_username = get_scheduler_api_client_for_server_username(args)
        scheduler_api_client_for_server_password = get_scheduler_api_client_for_server_password(args, cm)

        out.api_username = scheduler_api_client_for_server_username
        out.api_password = scheduler_api_client_for_server_password

        # This can be overridden through environment variables
        env_keys = ['Zato_Server_To_Scheduler_Use_TLS', 'ZATO_SERVER_SCHEDULER_USE_TLS']
        for key in env_keys:
            if value := os.environ.get(key):
                use_tls = as_bool(value)
                break
        else:
            use_tls = True

        out.use_tls = use_tls
        '''

        # .. finally, return the response to our caller.
        return out

# ################################################################################################################################

    def execute(self, args:'Namespace', show_output:'bool'=True, needs_created_flag:'bool'=False):

        print()
        print(222, args)
        print()

        qqq

        # Zato
        from zato.common.util.logging_ import get_logging_conf_contents

        # Navigate to the directory that the component will be created in.
        os.chdir(self.target_dir)

        repo_dir = os.path.join(self.target_dir, 'config', 'repo')
        conf_path = os.path.join(repo_dir, 'scheduler.conf')
        startup_jobs_conf_path = os.path.join(repo_dir, 'startup_jobs.conf')
        sql_conf_path = os.path.join(repo_dir, 'sql.conf')

        os.mkdir(os.path.join(self.target_dir, 'logs'))
        os.mkdir(os.path.join(self.target_dir, 'config'))
        os.mkdir(repo_dir)

        self.copy_scheduler_crypto(repo_dir, args)

        if hasattr(args, 'get'):
            secret_key = args.get('secret_key')
        else:
            secret_key = args.secret_key

        secret_key = secret_key or SchedulerCryptoManager.generate_key()
        cm = SchedulerCryptoManager.from_secret_key(secret_key)

        odb_engine=args.odb_type
        if odb_engine.startswith('postgresql'):
            odb_engine = 'postgresql+pg8000'

        # There will be always one cluster in the database.
        cluster_id = self._get_cluster_id(args)

        # We need to have a reference to it before we encrypt it later on.
        odb_password = args.odb_password or ''
        odb_password = odb_password.encode('utf8')
        odb_password = cm.encrypt(odb_password, needs_str=True)

        # Collect ODB configuration in one place as it will be reusable further below.
        odb_config:'strdict' = {
            'odb_engine': odb_engine,
            'odb_password': odb_password,
            'odb_db_name': args.odb_db_name or args.sqlite_path,
            'odb_host': args.odb_host or '',
            'odb_port': args.odb_port or '',
            'odb_username': args.odb_user or '',
        }

        server_config = self._get_server_config(args, cm, odb_config)

        initial_sleep_time = self.get_arg('initial_sleep_time', SCHEDULER.InitialSleepTime)

        scheduler_bind_host = self.get_arg('bind_host', SCHEDULER.DefaultBindHost)
        scheduler_bind_port = self.get_arg('bind_port', SCHEDULER.DefaultBindPort)

        zato_well_known_data = well_known_data.encode('utf8')
        zato_well_known_data = cm.encrypt(zato_well_known_data, needs_str=True)

        if is_linux:
            tls_version = SCHEDULER.TLS_Version_Default_Linux
            tls_ciphers = SCHEDULER.TLS_Ciphers_13
        else:
            tls_version = SCHEDULER.TLS_Version_Default_Windows
            tls_ciphers = SCHEDULER.TLS_Ciphers_12

        tls_use = self.get_arg('tls_enabled', SCHEDULER.TLS_Enabled)
        tls_client_certs = self.get_arg('tls_client_certs', SCHEDULER.TLS_Client_Certs)
        priv_key_location = self.get_arg('priv_key_location', SCHEDULER.TLS_Private_Key_Location)
        pub_key_location = self.get_arg('pub_key_location', SCHEDULER.TLS_Public_Key_Location)
        cert_location = self.get_arg('cert_location', SCHEDULER.TLS_Cert_Location)
        ca_certs_location = self.get_arg('ca_certs_location', SCHEDULER.TLS_CA_Certs_Key_Location)

        tls_version = self.get_arg('tls_version', tls_version)
        tls_ciphers = self.get_arg('tls_ciphers', tls_ciphers)

        if isinstance(secret_key, (bytes, bytearray)):
            secret_key = secret_key.decode('utf8')

        config:'strdict' = {
            'scheduler_api_client_for_server_auth_required': server_config.is_auth_from_server_required,
            'scheduler_api_client_for_server_username':  scheduler_api_client_for_server_username,
            'scheduler_api_client_for_server_password': scheduler_api_client_for_server_password,
            'cluster_id': cluster_id,
            'secret_key1': secret_key,
            'well_known_data': zato_well_known_data,
            'server_path': server_path,
            'server_host': server_host,
            'server_port': server_port,
            'server_username': server_username,
            'server_password': server_password,
            'initial_sleep_time': initial_sleep_time,
            'scheduler_bind_host': scheduler_bind_host,
            'scheduler_bind_port': scheduler_bind_port,
            'tls_use': tls_use,
            'tls_version': tls_version,
            'tls_ciphers': tls_ciphers,
            'tls_client_certs': tls_client_certs,
            'tls_priv_key_location': priv_key_location,
            'tls_pub_key_location': pub_key_location,
            'tls_cert_location': cert_location,
            'tls_ca_certs_location': ca_certs_location,
        }

        config.update(odb_config)

        logging_conf_contents = get_logging_conf_contents()

        _ = open_w(os.path.join(repo_dir, 'logging.conf')).write(logging_conf_contents)
        _ = open_w(conf_path).write(config_template.format(**config))
        _ = open_w(startup_jobs_conf_path).write(startup_jobs)
        _ = open_w(sql_conf_path).write(sql_conf_contents)

        # Initial info
        self.store_initial_info(self.target_dir, self.COMPONENTS.SCHEDULER.code)

        if show_output:
            if self.verbose:
                msg = """Successfully created a scheduler instance.
    You can start it with the 'zato start {path}' command.""".format(path=os.path.abspath(os.path.join(os.getcwd(), self.target_dir)))
                self.logger.debug(msg)
            else:
                self.logger.info('OK')

        # We return it only when told to explicitly so when the command runs from CLI
        # it doesn't return a non-zero exit code.
        if needs_created_flag:
            return True

# ################################################################################################################################
# ################################################################################################################################
