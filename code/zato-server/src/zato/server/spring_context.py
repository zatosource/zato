# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from zato.bunch import Bunch

# Spring Python
from springpython.config import Object, PythonConfig

# Zato
from zato.common import SIMPLE_IO, ZATO_CRYPTO_WELL_KNOWN_DATA
from zato.common.crypto import CryptoManager
from zato.common.kvdb import KVDB
from zato.common.odb.api import ODBManager, PoolStore
from zato.server.base.parallel import ParallelServer
from zato.server.service.store import ServiceStore

class ZatoContext(PythonConfig):

    # #######################################################
    # Crypto keys

    @Object
    def crypto_manager(self):
        return CryptoManager()

    # #######################################################
    # Services

    @Object
    def service_store(self):
        store = ServiceStore()
        store.odb = self.odb_manager()
        store.services = {}

        return store

    @Object
    def internal_service_modules(self):
        return [
            'zato.server.service.internal',
            'zato.server.service.internal.apispec',
            'zato.server.service.internal.apispec.pub',
            'zato.server.service.internal.cache.builtin',
            'zato.server.service.internal.cache.builtin.entry',
            'zato.server.service.internal.cache.builtin.pubapi',
            'zato.server.service.internal.cache.memcached',
            'zato.server.service.internal.channel.amqp_',
            'zato.server.service.internal.channel.jms_wmq',
            'zato.server.service.internal.channel.stomp',
            'zato.server.service.internal.channel.web_socket',
            'zato.server.service.internal.channel.web_socket.client',
            'zato.server.service.internal.channel.web_socket.subscription',
            'zato.server.service.internal.channel.zmq',
            'zato.server.service.internal.cloud.aws.s3',
            'zato.server.service.internal.cloud.openstack.swift',
            'zato.server.service.internal.connector.amqp_',
            'zato.server.service.internal.definition.amqp_',
            'zato.server.service.internal.definition.cassandra',
            'zato.server.service.internal.definition.jms_wmq',
            'zato.server.service.internal.email.imap',
            'zato.server.service.internal.email.smtp',
            'zato.server.service.internal.helpers',
            'zato.server.service.internal.hot_deploy',
            'zato.server.service.internal.info',
            'zato.server.service.internal.http_soap',
            'zato.server.service.internal.kv_data',
            'zato.server.service.internal.kvdb',
            'zato.server.service.internal.kvdb.data_dict.dictionary',
            'zato.server.service.internal.kvdb.data_dict.impexp',
            'zato.server.service.internal.kvdb.data_dict.translation',
            'zato.server.service.internal.message.namespace',
            'zato.server.service.internal.message.xpath',
            'zato.server.service.internal.message.json_pointer',
            'zato.server.service.internal.message.live_browser',
            'zato.server.service.internal.notif',
            'zato.server.service.internal.notif.cloud.openstack.swift',
            'zato.server.service.internal.notif.sql',
            'zato.server.service.internal.outgoing.amqp_',
            'zato.server.service.internal.outgoing.ftp',
            'zato.server.service.internal.outgoing.jms_wmq',
            'zato.server.service.internal.outgoing.odoo',
            'zato.server.service.internal.outgoing.sql',
            'zato.server.service.internal.outgoing.stomp',
            'zato.server.service.internal.outgoing.zmq',
            'zato.server.service.internal.pattern',
            'zato.server.service.internal.pickup',
            'zato.server.service.internal.pattern.invoke_retry',
            'zato.server.service.internal.pubsub',
            'zato.server.service.internal.pubsub.cleanup',
            'zato.server.service.internal.pubsub.delivery',
            'zato.server.service.internal.pubsub.endpoint',
            'zato.server.service.internal.pubsub.hook',
            'zato.server.service.internal.pubsub.message',
            'zato.server.service.internal.pubsub.pubapi',
            'zato.server.service.internal.pubsub.publish',
            'zato.server.service.internal.pubsub.subscription',
            'zato.server.service.internal.pubsub.queue',
            'zato.server.service.internal.pubsub.topic',
            'zato.server.service.internal.query.cassandra',
            'zato.server.service.internal.scheduler',
            'zato.server.service.internal.search.es',
            'zato.server.service.internal.search.solr',
            'zato.server.service.internal.security',
            'zato.server.service.internal.security.apikey',
            'zato.server.service.internal.security.aws',
            'zato.server.service.internal.security.basic_auth',
            'zato.server.service.internal.security.jwt',
            'zato.server.service.internal.security.ntlm',
            'zato.server.service.internal.security.oauth',
            'zato.server.service.internal.security.rbac',
            'zato.server.service.internal.security.rbac.client_role',
            'zato.server.service.internal.security.rbac.permission',
            'zato.server.service.internal.security.rbac.role',
            'zato.server.service.internal.security.rbac.role_permission',
            'zato.server.service.internal.security.tech_account',
            'zato.server.service.internal.security.tls.ca_cert',
            'zato.server.service.internal.security.tls.channel',
            'zato.server.service.internal.security.tls.key_cert',
            'zato.server.service.internal.security.wss',
            'zato.server.service.internal.security.vault.connection',
            'zato.server.service.internal.security.vault.policy',
            'zato.server.service.internal.security.xpath',
            'zato.server.service.internal.server',
            'zato.server.service.internal.service',
            'zato.server.service.internal.sms',
            'zato.server.service.internal.sms.twilio',
            'zato.server.service.internal.stats',
            'zato.server.service.internal.stats.summary',
            'zato.server.service.internal.stats.trends',
            'zato.server.service.internal.updates',
        ]

    @Object
    def service_modules(self):
        return []

    @Object
    def int_parameters(self):
        return SIMPLE_IO.INT_PARAMETERS.VALUES

    @Object
    def int_parameter_suffixes(self):
        return SIMPLE_IO.INT_PARAMETERS.SUFFIXES

    @Object
    def bool_parameter_prefixes(self):
        return SIMPLE_IO.BOOL_PARAMETERS.PREFIXES

    # #######################################################
    # SQL

    @Object
    def odb_manager(self):
        return ODBManager(well_known_data=ZATO_CRYPTO_WELL_KNOWN_DATA)

    @Object
    def sql_pool_store(self):
        return PoolStore()

    # #######################################################
    # Key-value DB

    @Object
    def kvdb(self):
        return KVDB()

    # #######################################################
    # Servers

    @Object
    def server(self):

        server = ParallelServer()
        server.odb = self.odb_manager()
        server.service_store = self.service_store()
        server.service_store.server = server
        server.sql_pool_store = self.sql_pool_store()
        server.int_parameters = self.int_parameters()
        server.int_parameter_suffixes = self.int_parameter_suffixes()
        server.bool_parameter_prefixes = self.bool_parameter_prefixes()
        server.internal_service_modules = self.internal_service_modules()
        server.service_modules = self.service_modules()
        server.kvdb = self.kvdb()
        server.user_config = Bunch()

        return server
