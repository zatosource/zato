# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps
from logging import getLogger
from traceback import format_exc

# Bunch
from bunch import Bunch

# gevent
from gevent.pywsgi import WSGIServer

# Zato
from zato.common.api import ZATO_ODB_POOL_NAME
from zato.common.broker_message import code_to_name
from zato.common.crypto.api import CryptoManager, is_string_equal
from zato.common.odb.api import ODBManager, PoolStore
from zato.common.util.api import as_bool, absjoin, get_config, new_cid, set_up_logging
from zato.common.util.json_ import json_loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, byteslist, callable_, callnone, intnone, strnone, type_

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
    username: 'str'
    password: 'str'
    server_type: 'str'
    callback_func: 'callable_'
    conf_file_name: 'str'
    crypto_manager: 'CryptoManager'
    crypto_manager_class: 'type_[CryptoManager]'

    def __init__(self) -> 'None':
        self.main = Bunch()
        self.stats_enabled = None
        self.component_dir = 'not-set-component_dir'

# ################################################################################################################################

    @classmethod
    def from_repo_location(
        class_,         # type: type_[AuxServerConfig]
        server_type,    # type: str
        repo_location,  # type: str
        conf_file_name, # type: str
        crypto_manager_class, # type: type_[CryptoManager]
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

        # Read config in and extend it with ODB-specific information
        config.main = get_config(
            repo_location,
            conf_file_name,
            crypto_manager=crypto_manager,
            secrets_conf=secrets_conf,
            require_exists=True
        )
        config.main.odb.fs_sql_config = get_config(repo_location, 'sql.conf', needs_user_config=False)
        config.main.crypto.use_tls = as_bool(config.main.crypto.use_tls)

        # Make all paths absolute
        if config.main.crypto.use_tls:
            config.main.crypto.ca_certs_location = absjoin(repo_location, config.main.crypto.ca_certs_location)
            config.main.crypto.priv_key_location = absjoin(repo_location, config.main.crypto.priv_key_location)
            config.main.crypto.cert_location = absjoin(repo_location, config.main.crypto.cert_location)

        # Set up the crypto manager need to access credentials
        config.crypto_manager = crypto_manager

        # ODB connection
        odb = ODBManager()
        sql_pool_store = PoolStore()

        if config.main.odb.engine != 'sqlite':

            config.main.odb.host = config.main.odb.host
            config.main.odb.username = config.main.odb.username
            config.main.odb.pool_size = config.main.odb.pool_size

            odb_password = config.main.odb.password or '' # type: str

            if odb_password and odb_password.startswith('gA'):
                config.main.odb.password = config.crypto_manager.decrypt(odb_password)

        # Decrypt the password used to invoke servers
        if config.main.get('server'):
            server_password = config.main.server.server_password or '' # type: str
            if server_password and server_password.startswith('gA'):
                server_password = config.crypto_manager.decrypt(server_password)
                config.main.server.server_password = server_password

        sql_pool_store[ZATO_ODB_POOL_NAME] = config.main.odb

        odb.pool = sql_pool_store[ZATO_ODB_POOL_NAME].pool
        odb.init_session(ZATO_ODB_POOL_NAME, config.main.odb, odb.pool, False)
        odb.pool.ping(odb.fs_sql_config)

        config.odb = odb

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
    has_credentials: 'bool' = True

    def __init__(self, config:'AuxServerConfig') -> 'None':
        self.config = config
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
    def start(
        class_,            # type 'type_[AuxServer]
        *,
        base_dir=None,         # type: strnone
        bind_host='127.0.0.1', # type: str
        bind_port=None,        # type: intnone
        username='',           # type: str
        password='',           # type: str
        callback_func=None,    # type: callnone
        server_type_suffix=''  # type: str
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
        )

        username = username or 'ipc.username.not.set.' + CryptoManager.generate_secret().decode('utf8')
        password = password or 'ipc.password.not.set.' + CryptoManager.generate_secret().decode('utf8')

        config.username = username
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

    def _check_credentials(self, request:'Bunch') -> 'None':

        username = request.get('username') or ''
        password = request.get('password') or ''

        if not is_string_equal(self.config.username, username):
            logger.info('Invalid IPC username')
            raise Exception('Invalid IPC username or password')

        if not is_string_equal(self.config.password, password):
            logger.info('Invalid IPC password')
            raise Exception('Invalid IPC username or password')

# ################################################################################################################################

    def handle_api_request(self, data:'bytes') -> 'any_':

        # Convert to a Python dict ..
        request = json_loads(data)

        # .. callback functions expect Bunch instances on input ..
        request = Bunch(request) # type: ignore

        # .. first, check credentials ..
        if self.has_credentials:
            self._check_credentials(request)

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

            # .. if there was any, invoke the business function ..
            if request:
                response = self.handle_api_request(request)

            # If we are here, it means that there was no exception
            status_text = 'ok'
            status_code = StatusCode.OK

        except Exception:

            # We are here because there was an exception
            logger.warning(format_exc())

            status_text = 'error'
            status_code = StatusCode.InternalError

        finally:

            # Build our response ..
            return_data = {
                'cid': cid,
                'status': status_text,
                'response': response
            }

            # .. make sure that we return bytes representing a JSON object ..
            try:
                return_data = dumps(return_data)
            except TypeError as e:
                e
                e
                return_data = '{}'
            return_data = return_data.encode('utf8')

            start_response(status_code, headers)
            return [return_data]

# ################################################################################################################################
# ################################################################################################################################
