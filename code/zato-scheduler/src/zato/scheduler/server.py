# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from json import dumps
from traceback import format_exc

# Bunch
from bunch import Bunch

# gevent
from gevent.pywsgi import WSGIServer

# simdjson
from simdjson import loads

# Zato
from zato.broker.client import BrokerClient
from zato.common.api import ZATO_ODB_POOL_NAME
from zato.common.broker_message import code_to_name
from zato.common.crypto.api import SchedulerCryptoManager
from zato.common.odb.api import ODBManager, PoolStore
from zato.common.util.api import as_bool, absjoin, get_config, new_cid
from zato.common.util.cli import read_stdin_data
from zato.scheduler.api import SchedulerAPI
from zato.scheduler.util import set_up_zato_client

# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, callable_

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class StatusCode:
    OK                 = '200 OK'
    InternalError      = '500 Internal Server error'
    ServiceUnavailable = '503 Service Unavailable'

headers = [('Content-Type', 'application/json')]

# ################################################################################################################################

class Config:
    """ Encapsulates configuration of various scheduler-related layers.
    """
    odb: 'ODBManager'
    crypto_manager: 'SchedulerCryptoManager'

    def __init__(self):
        self.main = Bunch()
        self.startup_jobs = []
        self.on_job_executed_cb = None
        self.stats_enabled = None
        self.job_log_level = 'info'
        self.component_dir = 'not-set-component_dir'
        self._add_startup_jobs = True
        self._add_scheduler_jobs = True

# ################################################################################################################################

    @staticmethod
    def from_repo_location(repo_location:'str') -> 'Config':

        # Response to produce
        config = Config()

        # Path to the scheduler can be built from its repository location
        component_dir = os.path.join(repo_location, '..', '..')
        component_dir = os.path.abspath(component_dir)
        config.component_dir = component_dir

        # Read config in and extend it with ODB-specific information
        config.main = get_config(repo_location, 'scheduler.conf', require_exists=True)
        config.main.odb.fs_sql_config = get_config(repo_location, 'sql.conf', needs_user_config=False)
        config.main.crypto.use_tls = as_bool(config.main.crypto.use_tls)

        # Make all paths absolute
        if config.main.crypto.use_tls:
            config.main.crypto.ca_certs_location = absjoin(repo_location, config.main.crypto.ca_certs_location)
            config.main.crypto.priv_key_location = absjoin(repo_location, config.main.crypto.priv_key_location)
            config.main.crypto.cert_location = absjoin(repo_location, config.main.crypto.cert_location)

        # Set up the crypto manager need to access credentials
        config.crypto_manager = SchedulerCryptoManager(repo_location, stdin_data=read_stdin_data())

        # ODB connection
        odb = ODBManager()
        sql_pool_store = PoolStore()

        if config.main.odb.engine != 'sqlite':

            config.main.odb.host = config.main.odb.host
            config.main.odb.username = config.main.odb.username
            config.main.odb.password = config.crypto_manager.decrypt(config.main.odb.password)
            config.main.odb.pool_size = config.main.odb.pool_size

        sql_pool_store[ZATO_ODB_POOL_NAME] = config.main.odb

        odb.pool = sql_pool_store[ZATO_ODB_POOL_NAME].pool
        odb.init_session(ZATO_ODB_POOL_NAME, config.main.odb, odb.pool, False)
        odb.pool.ping(odb.fs_sql_config)

        config.odb = odb

        return config

# ################################################################################################################################

class SchedulerServer:
    """ Main class spawning scheduler-related tasks and listening for HTTP API requests.
    """
    def __init__(self, config:'Config') -> 'None':
        self.config = config
        main = self.config.main

        if main.crypto.use_tls:
            tls_kwargs = {
                'keyfile': main.crypto.priv_key_location,
                'certfile': main.crypto.cert_location
            }
        else:
            tls_kwargs = {}

        # Configures a client to Zato servers
        self.zato_client = set_up_zato_client(main)

        # API server
        self.api_server = WSGIServer((main.bind.host, int(main.bind.port)), self, **tls_kwargs)

        # SchedulerAPI
        self.scheduler_api = SchedulerAPI(self.config)
        self.scheduler_api.broker_client = BrokerClient(zato_client=self.zato_client, server_rpc=None, scheduler_config=None)

# ################################################################################################################################

    def serve_forever(self):
        self.scheduler_api.serve_forever()
        self.api_server.serve_forever()

# ################################################################################################################################

    def handle_api_request(self, request):
        # type: (bytes) -> None

        # Log what we are about to do
        logger.info('Handling API request -> `%s`', request)

        # Convert to a Python dict ..
        request = loads(request)

        # .. callback functions expect Bunch instances on input ..
        request = Bunch(request) # type: ignore

        # .. look up the action we need to invoke ..
        action = request.get('action') # type: ignore

        # .. make sure that the basic information was given on input ..
        if not action:
            raise Exception('No action key found in API request')

        action_name = code_to_name[action] # type: ignore

        # .. convert it to an actual method to invoke ..
        func_name = 'on_broker_msg_{}'.format(action_name)
        func = getattr(self.scheduler_api, func_name)

        # .. finally, invoke the function with the input data.
        response = func(request)
        return response

# ################################################################################################################################

    def __call__(self, env:'anydict', start_response:'callable_') -> 'any_':

        cid      = '<cid-unassigned>'
        response = {}

        status_text = '<status_text-unassigned>'
        status_code = StatusCode.ServiceUnavailable

        try:

            # Assign a new cid
            cid = 'zsch{}'.format(new_cid())

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
            return_data = dumps(return_data)
            return_data = return_data.encode('utf8')

            start_response(status_code, headers)
            return [return_data]

# ################################################################################################################################
