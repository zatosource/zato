# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Spring Python
from springpython.config import Object, PythonConfig

# Zato
from zato.common import ZATO_CRYPTO_WELL_KNOWN_DATA
from zato.server.base.parallel import ParallelServer
from zato.server.base.singleton import SingletonServer
from zato.server.connection.http_soap import Security as ConnectionHTTPSOAPSecurity
from zato.server.crypto import CryptoManager
from zato.server.odb import ODBManager
from zato.server.pickup import Pickup, PickupEventProcessor
from zato.server.repo import RepoManager
from zato.server.scheduler import Scheduler
from zato.server.service.store import ServiceStore
from zato.server.connection.sql import PoolStore

class ZatoContext(PythonConfig):

    # #######################################################
    # Crypto keys

    @Object
    def crypto_manager(self):
        return CryptoManager()

    # #######################################################
    # Hot-deployment

    @Object
    def pickup(self):
        pickup = Pickup()
        pickup.pickup_event_processor = self.pickup_event_processor()

        return pickup

    @Object
    def pickup_event_processor(self):
        pickup_event_processor = PickupEventProcessor()

        return pickup_event_processor

    # #######################################################
    # Repository management

    @Object
    def config_repo_manager(self):
        repo_manager = RepoManager()

        return repo_manager

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
            'zato.server.service.internal.http_soap',
            'zato.server.service.internal.scheduler',
            'zato.server.service.internal.service',
            'zato.server.service.internal.channel.amqp',
            'zato.server.service.internal.channel.jms_wmq',
            'zato.server.service.internal.channel.zmq',
            'zato.server.service.internal.definition.amqp',
            'zato.server.service.internal.definition.jms_wmq',
            'zato.server.service.internal.outgoing.amqp',
            'zato.server.service.internal.outgoing.ftp',
            'zato.server.service.internal.outgoing.jms_wmq',
            'zato.server.service.internal.outgoing.sql',
            'zato.server.service.internal.outgoing.zmq',
            'zato.server.service.internal.security',
            'zato.server.service.internal.security.basic_auth',
            'zato.server.service.internal.security.tech_account',
            'zato.server.service.internal.security.wss',
        ]
    
    @Object
    def service_modules(self):
        return []
    
    @Object
    def int_parameters(self):
        return ['id']
    
    @Object
    def int_parameter_suffixes(self):
        return ['_id', '_size', '_timeout']
    
    @Object
    def bool_parameter_prefixes(self):
        return ['is_', 'needs_', 'should_']

    # #######################################################
    # Security
    
    @Object
    def connection_http_soap_security(self):
        return ConnectionHTTPSOAPSecurity()

    # #######################################################
    # SQL

    @Object
    def odb_manager(self):
        return ODBManager(well_known_data=ZATO_CRYPTO_WELL_KNOWN_DATA)
    
    @Object
    def sql_pool_store(self):
        return PoolStore()
    
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

        return server

    @Object
    def singleton_server(self):
        server = SingletonServer()
        server.pickup = self.pickup()
        server.config_repo_manager = self.config_repo_manager()
        server.scheduler = self.scheduler()

        return server

    # #######################################################
    # Scheduler management

    @Object
    def scheduler(self):
        return Scheduler()
