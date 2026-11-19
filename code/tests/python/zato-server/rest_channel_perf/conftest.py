# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import os
import secrets
import sys
import tempfile

# The services and the identity provider of the suite of channel invocations, which this suite shares
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'rest_channel_invocation'))

# psutil
import psutil

# pytest
import pytest

# Zato
from channel_tokens import IdentityProvider
from request_driver import build_go_program, ModuleCtx as DriverCtx
from zato.common.test.client import AdminClient
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture, get_server_pids, import_into_running_server, \
    render_template

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import anydict, strdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Logger_Name = 'zato.test.rest_channel_perf.conftest'

    Current_Dir = os.path.dirname(__file__)

    # The services that the channels invoke, deployed from the pickup directory when the server starts
    Services_Path = os.path.join(Current_Dir, '..', 'rest_channel_invocation', 'channel_services.py')

    # The security definitions and channels, imported once the services are deployed
    Template_Path = os.path.join(Current_Dir, '_enmasse_template.yaml')

    # The length of each generated secret, in bytes
    Secret_Bytes = 16

# ################################################################################################################################
# ################################################################################################################################

# The files of the session, which the session removes when it ends
_data_dir = tempfile.mkdtemp(prefix='zato_rest_channel_perf_')

# The provider that signs the tokens of the channel secured with JWTs
_provider = IdentityProvider()

# The credentials that the security definitions of the channels expect
_credentials:'strdict' = {
    'basic_username': 'test.perf.channel.basic',
    'basic_password': secrets.token_hex(ModuleCtx.Secret_Bytes),
    'api_key': secrets.token_hex(ModuleCtx.Secret_Bytes),
    'static_token': secrets.token_hex(ModuleCtx.Secret_Bytes),
    'jwt_client_password': secrets.token_hex(ModuleCtx.Secret_Bytes),
}

# What the tests know of the server once it runs
_server_info:'anydict' = {}

# ################################################################################################################################
# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
    ) -> 'anydict':
    """ Starts the identity provider, and returns the services to deploy and what imports the channels
    once the server runs.
    """
    state.test_data_directory = _data_dir

    _provider.start()
    _ = atexit.register(_provider.stop)

    placeholders = dict(_credentials)
    placeholders['issuer'] = _provider.issuer
    placeholders['audience'] = _provider.audience
    placeholders['jwks_url'] = _provider.jwks_url

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
        ) -> 'None':

        yaml_text = render_template(ModuleCtx.Template_Path, placeholders)
        import_into_running_server(zato_bin, server_directory, yaml_text, _data_dir)

        processes:'list[psutil.Process]' = []

        for pid in get_server_pids(state):
            processes.append(psutil.Process(pid))

        _server_info['host'] = host
        _server_info['port'] = server_port
        _server_info['password'] = invoke_password
        _server_info['database'] = state.pubsub_database
        _server_info['processes'] = processes

    out:'anydict' = {
        'placeholders': {},
        'populate_callback': _populate,
        'hot_deploy_sources': [ModuleCtx.Services_Path],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server_process = create_zato_server_fixture(
    logger_name=ModuleCtx.Logger_Name,
    server_log_copy_name='server-logs-rest-channel-perf.txt',
    template_path='',
    quickstart_prefix='zato_rest_channel_perf_qs_',
    extra_server_env={},
    patch_server_conf_bind=True,
    build_config_callback=_build_config,
    log_to_files=False,
)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server(zato_server_process:'None') -> 'anydict':
    """ Returns the address, the password, the database and the processes of the server of the session.
    """
    out = dict(_server_info)
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_client(zato_server:'anydict') -> 'AdminClient':
    """ Returns the client of the services of the server of the session.
    """
    base_url = f'http://{zato_server["host"]}:{zato_server["port"]}'

    out = AdminClient(base_url, zato_server['password'])
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def load_client() -> 'str':
    """ Returns the path of the load client, compiled for the session.
    """
    out = build_go_program(DriverCtx.Load_Client, _data_dir)
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def identity_provider() -> 'IdentityProvider':
    """ Returns the provider that signs the tokens of the channel secured with JWTs.
    """
    out = _provider
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def credentials() -> 'strdict':
    """ Returns the credentials that the security definitions of the channels expect.
    """
    out = _credentials
    return out

# ################################################################################################################################

@pytest.fixture(scope='session')
def data_dir() -> 'str':
    """ Returns the directory of the files of the session.
    """
    out = _data_dir
    return out

# ################################################################################################################################
# ################################################################################################################################
