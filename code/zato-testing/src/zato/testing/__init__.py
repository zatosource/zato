# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
from unittest import TestCase

# Bunch
from bunch import bunchify

# Cryptography
from cryptography.fernet import Fernet

# Zato
from zato.common.api import CHANNEL, DATA_FORMAT, UNITTEST
from zato.common.crypto.api import CryptoManager
from zato.common.json_internal import loads
from zato.common.kvdb.api import KVDB
from zato.common.odb.api import PoolStore
from zato.common.util.api import new_cid
from zato.server.base.worker import WorkerStore
from zato.server.connection.cache import CacheAPI
from zato.server.connection.http_soap.channel import RequestHandler
from zato.server.connection.vault import VaultConnAPI
from zato.server.base.parallel import ParallelServer
from zato.server.config import ConfigStore
from zato.server.service.store import ServiceStore
from zato.testing.requests_ import RequestsAdapter

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import basestring

# ################################################################################################################################

if 0:
    from zato.common.odb.unittest_ import QueryCtx
    from zato.server.service import Service

    QueryCtx = QueryCtx
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

class _FSConfig:
    def get(self, key):
        return getattr(self, key, None)

# ################################################################################################################################
# ################################################################################################################################

class FSPubSub(_FSConfig):
    __slots__ = 'data_prefix_len', 'data_prefix_short_len', 'log_if_deliv_server_not_found', 'log_if_wsx_deliv_server_not_found'

    def __init__(self):
        self.data_prefix_len = 100
        self.data_prefix_short_len = 100
        self.log_if_deliv_server_not_found = False
        self.log_if_wsx_deliv_server_not_found = False

# ################################################################################################################################
# ################################################################################################################################

class FSPubSubMetaTopic(_FSConfig):
    __slots__ = 'enabled', 'store_frequency'

    def __init__(self):
        self.enabled = False
        self.store_frequency = None

# ################################################################################################################################
# ################################################################################################################################

class FSPubSubMetaEndpointPub(_FSConfig):
    __slots__ = 'enabled', 'store_frequency', 'data_len', 'max_history'

    def __init__(self):
        self.enabled = False
        self.store_frequency = 1000
        self.data_len = 50
        self.max_history = 200

# ################################################################################################################################
# ################################################################################################################################

class FSServerConfig(_FSConfig):
    __slots__ = 'pubsub', 'pubsub_meta_topic', 'pubsub_meta_endpoint_pub', 'misc'

    def __init__(self):
        self.pubsub = FSPubSub()
        self.pubsub_meta_topic = FSPubSubMetaTopic()
        self.pubsub_meta_endpoint_pub = FSPubSubMetaEndpointPub()

# ################################################################################################################################
# ################################################################################################################################

class ServiceTestCaseConfig:
    pass

# ################################################################################################################################

class Cache:
    def __init__(self):
        pass

    def get(self, *args, **kwargs):
        return True

# ################################################################################################################################
# ################################################################################################################################

class ServiceTestCase(TestCase):
    def setUp(self):

        # For mocking out Vault responses
        self.vault_adapter = RequestsAdapter()

        # We are always the first process in a server
        os.environ['ZATO_SERVER_WORKER_IDX'] = '1'

        # Represents the server.conf file
        self.fs_server_config = FSServerConfig()

        self.worker_config = ConfigStore()
        self.fernet_key = Fernet.generate_key() # type: str
        self.crypto_manager = CryptoManager(secret_key=self.fernet_key)
        self.vault_conn_api = VaultConnAPI(requests_adapter=self.vault_adapter)

        self.server = ParallelServer()
        self.server.fs_server_config = self.fs_server_config
        self.server.kvdb = KVDB()
        self.server.component_enabled.stats = False
        self.server.component_enabled.slow_response = False
        self.server.crypto_manager = self.crypto_manager

        self.service_store = ServiceStore(is_testing=True)
        self.service_store.server = self.server
        self.service_store.services = {}

        self.server.service_store = self.service_store

        self.fs_sql_config = {
            UNITTEST.SQL_ENGINE: {
                'ping_query': 'SELECT 1+1'
            }
        }

        self.cache = Cache()
        self.sql_pool_store = PoolStore()

        self.worker_store = WorkerStore(self.worker_config, self.server)
        self.worker_store.sql_pool_store = self.sql_pool_store
        self.worker_store.outconn_wsx = None
        self.worker_store.vault_conn_api = self.vault_conn_api
        self.worker_store.sms_twilio_api = None
        self.worker_store.out_sap = None
        self.worker_store.out_sftp = None
        self.worker_store.outconn_ldap = {}
        self.worker_store.outconn_mongodb = {}
        self.worker_store.def_kafka = {}

        self.worker_store.cache_api = CacheAPI(self.server)
        self.worker_store.cache_api.default = self.cache

        self.request_handler = RequestHandler(self.server)

        self.wsgi_environ = {
            'HTTP_HOST': 'api.localhost'
        }

        # Callback methods for particular SQL queries
        self.sql_callback_by_idx = {}

# ################################################################################################################################

    def add_outconn_sql(self, name):
        # type: (str)
        self.sql_pool_store.add_unittest_item(name)

# ################################################################################################################################

    def import_services(self, item):
        # type: (object)
        self.service_store.import_services_from_anywhere(item, None, None, False)

# ################################################################################################################################

    def invoke_service(self, class_, request=None, **kwargs):
        # type: (Service, object, object)

        class_.name = class_.get_name()
        class_.impl_name = class_.get_impl_name()
        class_.component_enabled_ibm_mq = True
        class_.component_enabled_zeromq = False
        class_.component_enabled_sms = True
        class_.component_enabled_email = False
        class_.component_enabled_search = False
        class_.component_enabled_msg_path = False
        class_.component_enabled_patterns = False
        class_.has_sio = True
        class_._worker_config = self.worker_config
        class_._worker_store = self.worker_store
        class_.crypto = self.server.crypto_manager

        service = class_() # type: Service
        service.out.vault = self.vault_conn_api

        self.service_store.services[service.impl_name] = {
            'slow_threshold': 100,
        }

        channel = kwargs.get('channel') or CHANNEL.INVOKE
        data_format = kwargs.get('data_format') or DATA_FORMAT.DICT
        transport = ''
        broker_client = None
        cid = kwargs.get('cid') or new_cid()
        simple_io_config = {
            'bytes_to_str': {'encoding': 'utf8'}
        }

        response = service.update_handle(
            self.request_handler._set_response_data, service, request, channel, data_format, transport,
            self.server, broker_client, self.worker_store, cid, simple_io_config, environ=kwargs.get('environ'))

        if kwargs.get('as_bunch'):
            if isinstance(response.payload, basestring):
                payload = loads(response.payload)
                payload = bunchify(payload)
                response._payload = payload

        return response

# ################################################################################################################################
# ################################################################################################################################
