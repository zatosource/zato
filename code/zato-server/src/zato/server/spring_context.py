# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Spring Python
from springpython.config import Object, PythonConfig

# Zato
from zato.common import DEFAULT_STATS_SETTINGS, SIMPLE_IO, ZATO_CRYPTO_WELL_KNOWN_DATA
from zato.common.crypto import CryptoManager
from zato.common.delivery import DeliveryStore
from zato.common.kvdb import KVDB
from zato.server.base.parallel import ParallelServer
from zato.server.base.singleton import SingletonServer
from zato.server.connection.sql import PoolStore
from zato.server.odb import ODBManager
#from zato.server.pickup import Pickup, PickupEventProcessor
from zato.server.scheduler import Scheduler
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
            'zato.server.service.internal.channel.amqp',
            'zato.server.service.internal.channel.jms_wmq',
            'zato.server.service.internal.channel.zmq',
            'zato.server.service.internal.helpers',
            'zato.server.service.internal.http_soap',
            'zato.server.service.internal.hot_deploy',
            'zato.server.service.internal.kvdb',
            'zato.server.service.internal.kvdb.data_dict.dictionary',
            'zato.server.service.internal.kvdb.data_dict.impexp',
            'zato.server.service.internal.kvdb.data_dict.translation',
            'zato.server.service.internal.definition.amqp',
            'zato.server.service.internal.definition.jms_wmq',
            'zato.server.service.internal.outgoing.amqp',
            'zato.server.service.internal.outgoing.ftp',
            'zato.server.service.internal.outgoing.jms_wmq',
            'zato.server.service.internal.outgoing.sql',
            'zato.server.service.internal.outgoing.zmq',
            'zato.server.service.internal.pattern.delivery',
            'zato.server.service.internal.pattern.delivery.definition',
            'zato.server.service.internal.scheduler',
            'zato.server.service.internal.security',
            'zato.server.service.internal.security.basic_auth',
            'zato.server.service.internal.security.tech_account',
            'zato.server.service.internal.security.wss',
            'zato.server.service.internal.server',
            'zato.server.service.internal.service',
            'zato.server.service.internal.stats',
            'zato.server.service.internal.stats.summary',
            'zato.server.service.internal.stats.trends',
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
        return SIMPLE_IO.BOOL_PARAMETERS.SUFFIXES
    
    # #######################################################
    # Delivery store
    
    @Object
    def delivery_store(self):
        return DeliveryStore(self.kvdb())

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
    # Channels

    @Object
    def soap11_content_type(self):
        return 'application/xml'

    @Object
    def soap12_content_type(self):
        return 'application/soap+xml; charset=utf-8' # We always require UTF-8
    
    @Object
    def plain_xml_content_type(self):
        return 'application/xml'

    @Object
    def json_content_type(self):
        return 'application/json'

    # #######################################################
    # Servers
    
    @Object
    def parallel_server(self):

        server = ParallelServer()
        server.odb = self.odb_manager()
        server.service_store = self.service_store()
        server.sql_pool_store = self.sql_pool_store()
        server.int_parameters = self.int_parameters()
        server.int_parameter_suffixes = self.int_parameter_suffixes()
        server.bool_parameter_prefixes = self.bool_parameter_prefixes()
        server.soap11_content_type = self.soap11_content_type()
        server.soap12_content_type = self.soap12_content_type()
        server.plain_xml_content_type = self.plain_xml_content_type()
        server.json_content_type = self.json_content_type()
        server.internal_service_modules = self.internal_service_modules()
        server.service_modules = self.service_modules()
        server.kvdb = self.kvdb()

        return server

    @Object
    def singleton_server(self):
        server = SingletonServer()
        server.scheduler = self.scheduler()

        return server

    # #######################################################
    # Scheduler management

    @Object
    def scheduler(self):
        return Scheduler()

    @Object
    def startup_jobs(self):
        return [
            {'name': 'zato.stats.process-raw-times', 'seconds':90, 
             'service':'zato.stats.process-raw-times', 
             'extra':'max_batch_size={}'.format(DEFAULT_STATS_SETTINGS['scheduler_raw_times_batch'])},
            
            {'name': 'zato.stats.aggregate-by-minute', 'seconds':60, 
             'service':'zato.stats.aggregate-by-minute'},
            
            {'name': 'zato.stats.aggregate-by-hour', 'minutes':10,
             'service':'zato.stats.aggregate-by-hour'},
            
            {'name': 'zato.stats.aggregate-by-day', 'minutes':60,
             'service':'zato.stats.aggregate-by-day'},
            
            {'name': 'zato.stats.aggregate-by-month', 'minutes':60,
             'service':'zato.stats.aggregate-by-month'},
            
            {'name': 'zato.stats.summary.create-summary-by-day', 'minutes':10,
             'service':'zato.stats.summary.create-summary-by-day'},
            
            {'name': 'zato.stats.summary.create-summary-by-week', 'minutes':10,
             'service':'zato.stats.summary.create-summary-by-week'},
            
            {'name': 'zato.stats.summary.create-summary-by-month', 'minutes':60,
             'service':'zato.stats.summary.create-summary-by-month'},
            
            {'name': 'zato.stats.summary.create-summary-by-year', 'minutes':60,
             'service':'zato.stats.summary.create-summary-by-year'},
            
            {'name': 'zato.pattern.delivery.update-counters', 'seconds':30,
             'service':'zato.pattern.delivery.update-counters'},
            
            {'name': 'zato.pattern.delivery.dispatch-auto-resubmit', 'seconds':300,
             'service':'zato.pattern.delivery.dispatch-auto-resubmit'},
        ]
