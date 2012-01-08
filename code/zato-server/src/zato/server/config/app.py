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

# stdlib
import multiprocessing, os

# PyYAML
from yaml import load, Loader

# Spring Python
from springpython.config import Object, PythonConfig
from springpython.context import scope

# Zato
from zato.common import ZATO_CRYPTO_WELL_KNOWN_DATA
from zato.server.base.parallel import ParallelServer
from zato.server.base.singleton import SingletonServer
from zato.server.connection.http_soap import PlainHTTPHandler, RequestHandler, SOAPHandler
from zato.server.connection.http_soap import Security as ConnectionHTTPSOAPSecurity
from zato.server.crypto import CryptoManager
from zato.server.odb import ODBManager
from zato.server.pickup import Pickup, PickupEventProcessor
from zato.server.pool.sql import SQLConnectionPool, SQLConnectionPool
from zato.server.repo import RepoManager
from zato.server.scheduler import Scheduler
from zato.server.security.wss import WSSUsernameTokenProfileStore
from zato.server.service.store import EggServiceImporter, ServiceStore

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
        pickup_event_processor.importer = self.egg_importer()

        return pickup_event_processor

    @Object
    def egg_importer(self):
        importer = EggServiceImporter()
        importer.config_repo_manager = self.config_repo_manager()

        return importer

    # #######################################################
    # Repository management

    @Object
    def config_repo_manager(self):
        repo_manager = RepoManager()
        repo_manager.sql_pool_list_location = self.sql_pool_list_location()

        return repo_manager

    # #######################################################
    # Services

    @Object
    def service_store(self):
        store = ServiceStore()
        store.odb = self.odb_manager()
        store.services = {}

        return store

    # #######################################################
    # HTTP/SOAP handlers

    @Object
    def soap_config(self):
        return {}

    @Object
    def soap_handler(self):
        handler = SOAPHandler()
        handler.soap_config = self.soap_config()
        handler.service_store = self.service_store()
        handler.crypto_manager = self.crypto_manager()
        handler.wss_store = self.wss_username_password_store()

        return handler
    
    @Object
    def plain_http_handler(self):
        return PlainHTTPHandler()

    # #######################################################
    # Security

    @Object
    def wss_nonce_cache(self):
        return {}
    
    @Object
    def connection_http_soap_security(self):
        return ConnectionHTTPSOAPSecurity()

    @Object
    def wss_username_password_store(self):
        store = WSSUsernameTokenProfileStore()
        store.config = {"foo": "sample1"}

        # TODO: Fetch definitions from ODB
        #store.definitions = self.wss_username_password_definition_list()

        return store

    # #######################################################
    # ODB (Operational Database)

    @Object
    def odb_manager(self):
        return ODBManager(well_known_data=ZATO_CRYPTO_WELL_KNOWN_DATA)

    # #######################################################
    # Servers
    
    @Object
    def request_handler(self):
        rh = RequestHandler()
        rh.security = self.connection_http_soap_security()
        rh.soap_handler = self.soap_handler()
        rh.plain_http_handler = self.plain_http_handler()
        
        return rh

    @Object
    def parallel_server(self):

        server = ParallelServer()
        server.odb = self.odb_manager()
        server.service_store = self.service_store()
        server.request_handler = self.request_handler()
        server.request_handler.soap_handler.server = server
        server.request_handler.plain_http_handler.server = server

        return server

    @Object
    def singleton_server(self):
        server = SingletonServer()
        server.pickup = self.pickup()
        server.config_repo_manager = self.config_repo_manager()
        server.scheduler = self.scheduler()
        server.config_queue = multiprocessing.Queue()

        return server

    # #######################################################
    # Scheduler management

    @Object
    def scheduler(self):
        return Scheduler()

    # #######################################################
    # SQL connection pools management

    @Object
    def odb_pool_location(self):
        pass
        #return os.path.join(self.config_repo_location(), "odb.yml")

    @Object
    def odb_pool_config(self):
        #data = load(open(self.odb_pool_location()), Loader=Loader)
        #return data["zato_odb"]
        pass

    @Object
    def sql_pool_list_location(self):
        #return os.path.join(self.config_repo_location(), "sql-pool-list.yml")
        pass

    @Object
    def sql_pool_list(self):
        # TODO: Make sure the list is empty (sql_pool_list: {}) when Zato is
        # installed.

        #data = load(open(self.sql_pool_list_location()), Loader=Loader)
        return {} #data["sql_pool_list"]


    @Object
    def sql_pool(self):
        pool_list = self.sql_pool_list()
        config_repo_manager = self.config_repo_manager()
        crypto_manager = self.crypto_manager()
        create_sa_engines = True
        pool = SQLConnectionPool(pool_list, config_repo_manager, crypto_manager,
                                 create_sa_engines)

        return pool
