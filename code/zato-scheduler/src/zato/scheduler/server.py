# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
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
from zato.common.util.cli import read_stdin_data
from zato.scheduler.api import SchedulerAPI

# ################################################################################################################################

if 0:
    from zato.client import AnyServiceInvoker
    AnyServiceInvoker = AnyServiceInvoker

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

ok = '200 OK'
headers = [('Content-Type', 'application/json')]

# ################################################################################################################################

class Config(object):
    """ Encapsulates configuration of various scheduler-related layers.
    """
    def __init__(self):
        self.main = Bunch()
        self.startup_jobs = []
        self.odb = None
        self.on_job_executed_cb = None
        self.stats_enabled = None
        self.job_log_level = 'info'
        self.broker_client = None
        self._add_startup_jobs = True
        self._add_scheduler_jobs = True

# ################################################################################################################################

class SchedulerServer(object):
    """ Main class spawning scheduler-related tasks and listening for HTTP API requests.
    """
    def __init__(self, config, repo_location):
        self.odb = config.odb
        self.config = config
        self.repo_location = repo_location
        self.sql_pool_store = PoolStore()

        # Set up the crypto manager that will be used by both ODB and, possibly, KVDB
        self.config.crypto_manager = SchedulerCryptoManager(self.repo_location, stdin_data=read_stdin_data())

        # ODB connection
        self.odb = ODBManager()

        if self.config.main.odb.engine != 'sqlite':
            self.config.main.odb.password = self.config.crypto_manager.decrypt(config.main.odb.password)
            self.config.main.odb.host = config.main.odb.host
            self.config.main.odb.pool_size = config.main.odb.pool_size
            self.config.main.odb.username = config.main.odb.username

        self.sql_pool_store[ZATO_ODB_POOL_NAME] = self.config.main.odb

        main = self.config.main

        if main.crypto.use_tls:
            tls_kwargs = {
                'keyfile': main.crypto.priv_key_location,
                'certfile': main.crypto.cert_location
            }
        else:
            tls_kwargs = {}

        # Configures a client to Zato servers
        self.zato_client = self.set_up_zato_client(self.config.main)

        # API server
        self.api_server = WSGIServer((main.bind.host, int(main.bind.port)), self, **tls_kwargs)

        self.odb.pool = self.sql_pool_store[ZATO_ODB_POOL_NAME].pool
        self.odb.init_session(ZATO_ODB_POOL_NAME, self.config.main.odb, self.odb.pool, False)
        self.config.odb = self.odb

        # SchedulerAPI
        self.scheduler_api = SchedulerAPI(self.config)
        self.scheduler_api.broker_client = BrokerClient(zato_client=self.zato_client)

# ################################################################################################################################

    def _set_up_zato_client_by_server_path(self, server_path):
        # type: (str) -> AnyServiceInvoker

        # Zato
        from zato.common.util.api import get_client_from_server_conf

        return get_client_from_server_conf(server_path, require_server=False)

# ################################################################################################################################

    def _set_up_zato_client_by_remote_details(self, server_host, server_port, server_username, server_password):
        # type: (str, int, str, str) -> AnyServiceInvoker
        pass

# ################################################################################################################################

    def set_up_zato_client(self, config):
        # type: (Bunch) -> AnyServiceInvoker

        # New in 3.2, hence optional
        server_config = config.get('server') # type: Bunch

        # We do have server configuration available ..
        if server_config:

            if server_config.get('server_path'):
                return self._set_up_zato_client_by_server_path(server_config.server_path)
            else:
                server_host = server_config.server_host
                server_port = server_config.server_port
                server_username = server_config.server_username
                server_password = server_config.server_password

                return self._set_up_zato_client_by_remote_details(
                    server_host,
                    server_port,
                    server_username,
                    server_password
                )

        # .. no configuration, assume this is a default quickstart cluster.
        else:
            # This is what quickstart environments use by default
            server_path = '/opt/zato/env/qs-1'
            return self._set_up_zato_client_by_server_path(server_path)

# ################################################################################################################################

    def serve_forever(self):
        self.scheduler_api.serve_forever()
        self.api_server.serve_forever()

# ################################################################################################################################

    def handle_api_request(self, data):
        # type: (bytes) -> None

        # Convert to a Python dict ..
        data = loads(data)

        # .. callback functions expect Bunch instances on input ..
        data = Bunch(data)

        # .. look up the action we need to invoke ..
        action_name = code_to_name[data['action']]

        # .. convert it to an actual method to invoke ..
        func_name = 'on_broker_msg_{}'.format(action_name)
        func = getattr(self.scheduler_api, func_name)

        # .. finally, invoke the function with the input data.
        func(data)

# ################################################################################################################################

    def __call__(self, env, start_response):
        try:
            request = env['wsgi.input'].read()
            self.handle_api_request(request)
            start_response(ok, headers)
            return [b'{}\n']
        except Exception:
            logger.warning(format_exc())

# ################################################################################################################################
