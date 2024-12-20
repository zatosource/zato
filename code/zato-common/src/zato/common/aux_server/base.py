# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps
from logging import getLogger
from traceback import format_exc
from uuid import uuid4

# Bunch
from bunch import Bunch

# gevent
from gevent.pywsgi import WSGIServer

# Zato
from zato.common.api import IPC as Common_IPC, ZATO_ODB_POOL_NAME
from zato.common.broker_message import code_to_name
from zato.common.crypto.api import CryptoManager
from zato.common.odb.api import ODBManager, PoolStore
from zato.common.typing_ import cast_
from zato.common.util.api import as_bool, absjoin, get_config, is_encrypted, new_cid, set_up_logging
from zato.common.util.auth import check_basic_auth
from zato.common.util.json_ import json_loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, byteslist, callable_, callnone, intnone, strdict, strnone, type_
    callnone = callnone
    intnone = intnone
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class StatusCode:
    OK                 = '200 OK'
    InternalError      = '500 Internal Server error'
    ServiceUnavailable = '503 Service Unavailable'

headers = [('Content-Type', 'application/json')]

# ################################################################################################################################
# ################################################################################################################################

class AuxServerConfig:
    """ Encapsulates configuration of various server-related layers.
    """
    odb: 'ODBManager'
    username: 'str' = ''
    password: 'str' = ''
    env_key_username: 'str' = ''
    env_key_password: 'str' = ''
    env_key_auth_required: 'str' = ''
    server_type: 'str'
    callback_func: 'callable_'
    conf_file_name: 'str'
    crypto_manager: 'CryptoManager'
    crypto_manager_class: 'type_[CryptoManager]'
    parent_server_name: 'str'
    parent_server_pid: 'int'
    raw_config: 'Bunch'

    def __init__(self) -> 'None':
        self.main = Bunch()
        self.stats_enabled = None
        self.component_dir = 'not-set-component_dir'

# ################################################################################################################################

    @staticmethod
    def get_odb(config:'AuxServerConfig') -> 'ODBManager':

        odb = ODBManager()
        sql_pool_store = PoolStore()

        if config.main.odb.engine != 'sqlite':

            config.main.odb.host = config.main.odb.host
            config.main.odb.username = config.main.odb.username
            config.main.odb.pool_size = config.main.odb.pool_size

            odb_password:'str' = config.main.odb.password or ''

            if odb_password and odb_password.startswith('gA'):
                config.main.odb.password = config.crypto_manager.decrypt(odb_password)

        sql_pool_store[ZATO_ODB_POOL_NAME] = config.main.odb

        odb.pool = sql_pool_store[ZATO_ODB_POOL_NAME].pool
        odb.init_session(ZATO_ODB_POOL_NAME, config.main.odb, odb.pool, False)
        _ = odb.pool.ping(odb.fs_sql_config)

        return odb

# ################################################################################################################################

    def set_credentials_from_env(self) -> 'bool':

        # Return if there is no environment variable indicating what our credentials are
        if not self.env_key_auth_required:
            return False

        # Return if the variable is set but its boolean value is not True
        auth_required = os.environ.get(self.env_key_auth_required)
        auth_required = as_bool(auth_required)

        if not auth_required:
            return False

        # If we are here, we can read our credentials from environment variables
        username = os.environ.get(self.env_key_username) or 'env_key_username_missing'
        password = os.environ.get(self.env_key_password) or 'env_key_password_missing.' + uuid4().hex

        self.username = username
        self.password = password

        logger.info(f'Set username from env. variable `{self.env_key_username}`')
        logger.info(f'Set password from env. variable `{self.env_key_password}`')

        # Return True to indicate that we have set the credentials
        return True

# ################################################################################################################################

    @classmethod
    def from_repo_location(
        class_,         # type: type_[AuxServerConfig]
        server_type,    # type: str
        repo_location,  # type: str
        conf_file_name, # type: str
        crypto_manager_class, # type: type_[CryptoManager]
        needs_odb=True, # type: bool
    ) -> 'AuxServerConfig':

        # Zato
        from zato.common.util.cli import read_stdin_data

        # Reusable
        crypto_manager = crypto_manager_class(repo_location, stdin_data=read_stdin_data())

        # Response to produce
        config = class_()
        config.server_type = server_type

        # Path to the component can be built from its repository location
        component_dir = os.path.join(repo_location, '..', '..')
        component_dir = os.path.abspath(component_dir)
        config.component_dir = component_dir

        # This is optional
        secrets_conf_location = os.path.join(repo_location, 'secrets.conf')
        if os.path.exists(secrets_conf_location):
            secrets_conf = get_config(repo_location, 'secrets.conf', needs_user_config=False)
        else:
            secrets_conf = None

        # Read configuration in
        raw_config = get_config(
            repo_location,
            conf_file_name,
            crypto_manager=crypto_manager,
            secrets_conf=secrets_conf,
            require_exists=True
        )
        config.raw_config = raw_config # type: ignore
        config.main = cast_('Bunch', raw_config)
        config.main.crypto.use_tls = as_bool(config.main.crypto.use_tls)

        # Make all paths absolute
        if config.main.crypto.use_tls:
            config.main.crypto.ca_certs_location = absjoin(repo_location, config.main.crypto.ca_certs_location)
            config.main.crypto.priv_key_location = absjoin(repo_location, config.main.crypto.priv_key_location)
            config.main.crypto.cert_location = absjoin(repo_location, config.main.crypto.cert_location)

        # Set up the crypto manager need to access credentials
        config.crypto_manager = crypto_manager

        # Optionally, establish an ODB connection
        has_odb = False

        if needs_odb:
            if 'odb' in config.main:
                config.main.odb.fs_sql_config = get_config(repo_location, 'sql.conf', needs_user_config=False)
                config.odb = class_.get_odb(config)
                has_odb = True

        # We want to have something set, even None, to make sure we do not get AttributeErrors when accessing config.odb
        if not has_odb:
            config.odb = None # type: ignore

        # Decrypt the password used to invoke servers
        if config.main.get('server'):
            server_password = config.main.server.server_password or '' # type: str
            if server_password and server_password.startswith('gA'):
                server_password = config.crypto_manager.decrypt(server_password)
                config.main.server.server_password = server_password

        # Environment variables have precedence ..
        has_credentials_from_env = config.set_credentials_from_env()

        # .. if we have not set the credentials in the environment ..
        # .. we still need to try to set them based on our configuration ..
        if not has_credentials_from_env:

            # .. otherwise, check the configuration to obtain the credentials used to invoke schedulers
            api_clients = config.main.get('api_clients') or {}

            # Proceed if any API clients are defined ..
            if api_clients:

                # .. this will give us all the keys in this part of the configuration ..
                api_clients_keys = list(api_clients.keys())

                # .. out of which we can discard some ..
                for name in ['auth_required']:
                    if name in api_clients:
                        api_clients_keys.remove(name)

                # .. if we still have any keys left, we choose the first one to be our API credentials ..
                if api_clients_keys:

                    # .. note that we currently handle only one username ..
                    username = api_clients_keys[0]

                    # .. decrypt its password ..
                    password = api_clients[username]
                    if is_encrypted(password):
                        password = config.crypto_manager.decrypt(password)

                    # .. make sure both credentials are strings ..
                    username = str(username)
                    password = str(password)

                    # .. we can set its username ..
                    config.username = username
                    config.password = password

        return config

# ################################################################################################################################
# ################################################################################################################################

class AuxServer:
    """ Main class spawning an auxilliary server and listening for API requests.
    """
    needs_logging_setup: 'bool'
    api_server: 'WSGIServer'
    cid_prefix: 'str'
    server_type: 'str'
    conf_file_name: 'str'
    config_class: 'type_[AuxServerConfig]'
    crypto_manager_class: 'type_[CryptoManager]'
    needs_odb: 'bool' = True
    has_credentials: 'bool' = True
    parent_server_name: 'str'
    parent_server_pid:  'int'

    def __init__(self, config:'AuxServerConfig') -> 'None':

        # Type hints
        tls_kwargs:'strdict'

        self.config = config
        self.parent_server_name = config.parent_server_name
        self.parent_server_pid = config.parent_server_pid

        main = self.config.main

        if main.crypto.use_tls:
            tls_kwargs = {
                'keyfile': main.crypto.priv_key_location,
                'certfile': main.crypto.cert_location
            }
        else:
            tls_kwargs = {}

        # API server
        self.api_server = WSGIServer((main.bind.host, int(main.bind.port)), self, **tls_kwargs)

# ################################################################################################################################

    @classmethod
    def before_config_hook(class_:'type_[AuxServer]') -> 'None':
        pass

# ################################################################################################################################

    @classmethod
    def after_config_hook(
        class_, # type: type_[AuxServer]
        config, # type: AuxServerConfig
        repo_location, # type: str
    ) -> 'None':

        logger = getLogger(__name__)
        logger.info('{} starting (http{}://{}:{})'.format(
            config.server_type,
            's' if config.main.crypto.use_tls else '',
            config.main.bind.host,
            config.main.bind.port)
        )

# ################################################################################################################################

    @classmethod
    def start_from_repo_location(
        class_,                # type: type_[AuxServer]
        *,
        base_dir=None,         # type: strnone
        bind_host='127.0.0.1', # type: str
        bind_port=None,        # type: intnone
        username='',           # type: str
        password='',           # type: str
        callback_func=None,    # type: callnone
        server_type_suffix='', # type: str
        parent_server_name='', # type: str
        parent_server_pid=-1,  # type: int
    ) -> 'None':

        # Functionality that needs to run before configuration is created
        class_.before_config_hook()

        # Where we keep our configuration
        base_dir = base_dir or '.'
        repo_location = os.path.join(base_dir, 'config', 'repo')

        # Optionally, configure logging
        if class_.needs_logging_setup:
            set_up_logging(repo_location)

        # The main configuration object
        config = class_.config_class.from_repo_location(
            class_.server_type,
            repo_location,
            class_.conf_file_name,
            class_.crypto_manager_class,
            class_.needs_odb,
        )

        config.parent_server_name = parent_server_name
        config.parent_server_pid  = parent_server_pid

        if not config.username:
            username = username or 'ipc.username.not.set.' + CryptoManager.generate_secret().decode('utf8') # type: ignore
            config.username = username

        if not config.password:
            password = password or 'ipc.password.not.set.' + CryptoManager.generate_secret().decode('utf8') # type: ignore
            config.password = password

        if callback_func:
            config.callback_func = callback_func
        config.server_type = config.server_type + server_type_suffix

        # This is optional
        if bind_port:
            config.main.bind = Bunch()
            config.main.bind.host = bind_host
            config.main.bind.port = bind_port

        # Functionality that needs to run before configuration is created
        class_.after_config_hook(config, repo_location)

        # Run the server now
        class_._start(config)

# ################################################################################################################################

    @classmethod
    def start_from_config(class_:'type_[AuxServer]', config:'AuxServerConfig') -> 'None':
        class_._start(config)

# ################################################################################################################################

    @classmethod
    def _start(class_:'type_[AuxServer]', config:'AuxServerConfig') -> 'None':
        try:
            class_(config).serve_forever()
        except Exception:
            logger.warning(format_exc())

# ################################################################################################################################

    def serve_forever(self) -> 'None':
        self.api_server.serve_forever()

# ################################################################################################################################

    def get_action_func_impl(self, action_name:'str') -> 'callable_':
        raise NotImplementedError()

# ################################################################################################################################

    def _check_credentials(self, credentials:'str') -> 'None':

        result = check_basic_auth('', credentials, self.config.username, self.config.password)
        if result is not True:
            logger.info('Credentials error -> %s', result)
            raise Exception('Invalid credentials')

# ################################################################################################################################

    def should_check_credentials(self) -> 'bool':
        return True

# ################################################################################################################################

    def handle_api_request(self, data:'bytes', credentials:'str') -> 'any_':

        # Convert to a Python dict ..
        request = json_loads(data)

        # .. callback functions expect Bunch instances on input ..
        request = Bunch(request) # type: ignore

        # .. first, check credentials ..
        if self.has_credentials:
            if self.should_check_credentials():
                self._check_credentials(credentials)

        # .. look up the action we need to invoke ..
        action = request.get('action') # type: ignore

        # .. make sure that the basic information was given on input ..
        if not action:
            raise Exception('No action key found in API request')

        action_name = code_to_name[action] # type: ignore

        # .. convert it to an actual method to invoke ..
        func = self.get_action_func_impl(action_name)

        # .. finally, invoke the function with the input data.
        response = func(request)
        return response

# ################################################################################################################################

    def __call__(self, env:'anydict', start_response:'callable_') -> 'byteslist':

        cid      = '<cid-unassigned>'
        response = {}

        status_text = '<status_text-unassigned>'
        status_code = StatusCode.ServiceUnavailable

        try:

            # Assign a new cid
            cid = '{}{}'.format(self.cid_prefix, new_cid())

            # Get the contents of our request ..
            request = env['wsgi.input'].read()

            # .. this is where we expect to find Basic Auth credentials ..
            credentials = env.get('HTTP_AUTHORIZATION') or ''

            # .. if there was any, invoke the business function ..
            if request:
                response = self.handle_api_request(request, credentials)

            # If we are here, it means that there was no exception
            status_text = Common_IPC.Status_OK
            status_code = StatusCode.OK

        except Exception:

            # We are here because there was an exception
            logger.warning(format_exc())

            status_text = 'error'
            status_code = StatusCode.InternalError

        finally:

            # Build our response ..
            return_data:'any_' = {
                'cid': cid,
                'status': status_text,
                'response': response
            }

            # .. make sure that we return bytes representing a JSON object ..
            return_data = dumps(return_data)
            return_data = return_data.encode('utf8')

            start_response(status_code, headers)

            return [return_data]

# ################################################################################################################################
# ################################################################################################################################
