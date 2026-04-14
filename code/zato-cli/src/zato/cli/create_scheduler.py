# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""


# stdlib
import os
from copy import deepcopy
from dataclasses import dataclass

# Bunch
from bunch import Bunch

# Zato
from zato.cli import common_scheduler_server_address_opts, common_scheduler_server_api_client_opts, ZatoCommand
from zato.common.api import SCHEDULER
from zato.common.const import ServiceConst
from zato.common.crypto.api import SchedulerCryptoManager
from zato.common.crypto.const import well_known_data
from zato.common.scheduler import startup_jobs
from zato.common.util.config import get_scheduler_api_client_for_server_auth_required, \
    get_scheduler_api_client_for_server_password, get_scheduler_api_client_for_server_username
from zato.common.util.open_ import open_w
from zato.common.util.platform_ import is_linux

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from argparse import Namespace
    from zato.common.typing_ import any_, strdict
    Namespace = Namespace

# ################################################################################################################################
# ################################################################################################################################

config_template = """[bind]
host={scheduler_bind_host}
port={scheduler_bind_port}

[cluster]
id=1

[server]
server_path={server_path}
server_host={server_host}
server_port={server_port}
server_username={server_username}
server_password={server_password}
server_use_tls={server_use_tls}
server_tls_verify=False

[misc]
initial_sleep_time={initial_sleep_time}

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
    server_host: 'str'
    server_port: 'int'
    server_path: 'str'
    server_use_tls: 'bool'
    is_auth_from_server_required: 'bool'

    class api_client:

        class from_server_to_scheduler:
            username: 'str'
            password: 'str'

        class from_scheduler_to_server:
            username: 'str' = ServiceConst.API_Admin_Invoke_Username
            password: 'str'

# ################################################################################################################################
# ################################################################################################################################

class Create(ZatoCommand):
    """ Creates a new scheduler instance.
    """
    needs_empty_dir = True

    opts:'any_' = []

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

    opts.append({'name':'--server-username', 'help':'Deprecated. Use --server-api-client-for-scheduler-username'})
    opts.append({'name':'--server-password', 'help':'Deprecated. Use --server-api-client-for-scheduler-password'})

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

    opts += deepcopy(common_scheduler_server_address_opts)
    opts += deepcopy(common_scheduler_server_api_client_opts)

# ################################################################################################################################

    def __init__(self, args:'any_') -> 'None':
        self.target_dir = os.path.abspath(args.path)
        super(Create, self).__init__(args)

# ################################################################################################################################

    def allow_empty_secrets(self):
        return True

# ################################################################################################################################

    def _get_server_config(self, args:'any_', cm:'SchedulerCryptoManager') -> 'ServerConfigForScheduler':

        out = ServerConfigForScheduler()

        server_path = self.get_arg('server_path') or ''
        server_host = self.get_arg('server_host', '127.0.0.1')
        server_port = self.get_arg('server_port', 17010)

        scheduler_api_client_for_server_auth_required = get_scheduler_api_client_for_server_auth_required(args)
        scheduler_api_client_for_server_username = get_scheduler_api_client_for_server_username(args)
        scheduler_api_client_for_server_password = get_scheduler_api_client_for_server_password(args, cm)

        out.server_path = server_path
        out.server_host = server_host
        out.server_port = server_port

        out.is_auth_from_server_required = scheduler_api_client_for_server_auth_required # type: ignore
        out.api_client.from_server_to_scheduler.username = scheduler_api_client_for_server_username
        out.api_client.from_server_to_scheduler.password = scheduler_api_client_for_server_password

        # Handle both ..
        server_password = self.get_arg('server_password')
        server_api_client_for_scheduler_password = self.get_arg('server_api_client_for_scheduler_password')

        # .. but prefer the latter ..
        server_api_client_for_scheduler_password = server_password or server_api_client_for_scheduler_password

        # .. it still may be empty ..
        if not server_api_client_for_scheduler_password:
            server_api_client_for_scheduler_password = ''

        out.api_client.from_scheduler_to_server.password = server_api_client_for_scheduler_password

        # Extract basic information about the scheduler the server will be invoking ..
        server_use_tls, server_host, server_port = self._extract_address_data(
            args,
            'server_address_for_scheduler',
            'server_host',
            'server_port',
            '127.0.0.1',
            17010,
        )

        out.server_use_tls = server_use_tls
        out.server_host = server_host
        out.server_port = server_port

        return out

# ################################################################################################################################

    def execute(self, args:'Namespace', show_output:'bool'=True, needs_created_flag:'bool'=False):

        # Zato
        from zato.common.util.logging_ import get_logging_conf_contents

        os.chdir(self.target_dir)

        repo_dir = os.path.join(self.target_dir, 'config', 'repo')
        conf_path = os.path.join(repo_dir, 'scheduler.conf')
        startup_jobs_conf_path = os.path.join(repo_dir, 'startup_jobs.conf')

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

        server_config = self._get_server_config(args, cm)

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
            'scheduler_api_client_for_server_username':  server_config.api_client.from_server_to_scheduler.username,
            'scheduler_api_client_for_server_password': server_config.api_client.from_server_to_scheduler.password,
            'secret_key1': secret_key,
            'well_known_data': zato_well_known_data,
            'server_path': server_config.server_path,
            'server_host': server_config.server_host,
            'server_port': server_config.server_port,
            'server_use_tls': server_config.server_use_tls,
            'server_username': server_config.api_client.from_scheduler_to_server.username,
            'server_password': server_config.api_client.from_scheduler_to_server.password,
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

        logging_conf_contents = get_logging_conf_contents()

        _ = open_w(os.path.join(repo_dir, 'logging.conf')).write(logging_conf_contents)
        _ = open_w(conf_path).write(config_template.format(**config))
        _ = open_w(startup_jobs_conf_path).write(startup_jobs)

        self.store_initial_info(self.target_dir, self.COMPONENTS.SCHEDULER.code)

        if show_output:
            if self.verbose:
                msg = """Successfully created a scheduler instance.
    You can start it with the 'zato start {path}' command.""".format(path=os.path.abspath(os.path.join(os.getcwd(), self.target_dir)))
                self.logger.debug(msg)
            else:
                self.logger.info('OK')

        if needs_created_flag:
            return True

# ################################################################################################################################
# ################################################################################################################################
