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
from zato.server.channel.soap import SOAPMessageHandler, SOAPChannelStore
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
        store.services = {}

        return store

    # #######################################################
    # SOAP

    @Object
    def soap_config(self):
        return {
            
            # Ping
            "zato:ping": "zato.server.service.internal.Ping",

            # SQL connection pools
            "zato:pool.sql.get-list":"zato.server.service.internal.sql.GetSQLConnectionPoolList",
            "zato:pool.sql.create":"zato.server.service.internal.sql.CreateSQLConnectionPool",
            "zato:pool.sql.edit":"zato.server.service.internal.sql.EditSQLConnectionPool",
            "zato:pool.sql.delete":"zato.server.service.internal.sql.DeleteSQLConnectionPool",
            "zato:pool.sql.change-password":"zato.server.service.internal.sql.ChangePasswordSQLConnectionPool",
            "zato:pool.sql.ping":"zato.server.service.internal.sql.PingSQLConnectionPool",

            # Scheduler
            "zato:scheduler.job.get-list":"zato.server.service.internal.scheduler.GetJobList",
            "zato:scheduler.job.create":"zato.server.service.internal.scheduler.CreateJob",
            "zato:scheduler.job.edit":"zato.server.service.internal.scheduler.EditJob",
            "zato:scheduler.job.execute":"zato.server.service.internal.scheduler.ExecuteJob",
            "zato:scheduler.job.delete":"zato.server.service.internal.scheduler.DeleteJob",

            # Services
            "zato:service.get-list":"zato.server.service.internal.service.GetServiceList",
            "zato:service.get-details":"zato.server.service.internal.service.GetServiceDetails",

            # SOAP channels
            "zato:channel.soap.get-list":"zato.server.service.internal.soap.GetChannelList",
            
            # Technical accounts
            "zato:security.tech-account.get-list":"zato.server.service.internal.security.tech_account.GetList",
            "zato:security.tech-account.get-by-id":"zato.server.service.internal.security.tech_account.GetByID",
            "zato:security.tech-account.create":"zato.server.service.internal.security.tech_account.Create",
            "zato:security.tech-account.edit":"zato.server.service.internal.security.tech_account.Edit",
            "zato:security.tech-account.change-password":"zato.server.service.internal.security.tech_account.ChangePassword",
            "zato:security.tech-account.delete":"zato.server.service.internal.security.tech_account.Delete",

            # WS-Security
            "zato:security.wss.get-list":"zato.server.service.internal.security.wss.GetList",
            "zato:security.wss.get-details":"zato.server.service.internal.security.wss.GetDetails",
            "zato:security.wss.create":"zato.server.service.internal.security.wss.Create",
            "zato:security.wss.edit":"zato.server.service.internal.security.wss.Edit",
        }

    @Object
    def soap_message_handler(self):
        handler = SOAPMessageHandler()
        handler.soap_config = self.soap_config()
        handler.service_store = self.service_store()
        handler.crypto_manager = self.crypto_manager()
        handler.wss_store = self.wss_username_password_store()

        return handler

    # #######################################################
    # WS-Security

    @Object
    def wss_nonce_cache(self):
        return {}

    #@Object
    #def wss_username_password_definition_list(self):
    #    definition_list = {u"Adapter AZR": {"username":"user1", "password":"zzz",
    #                     "reject_empty_nonce_creation_timestamp":True,
    #                     "expiry_limit":3000, "reject_stale_username_token":True,
    #                     "nonce_freshness_time":30900}} # TODO: Make sure it can't be set to 0
    #    return definition_list

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
    def parallel_server(self):

        server = ParallelServer()
        server.odb = self.odb_manager()
        server.soap_handler = self.soap_message_handler()

        # Regular objects.
        #server.sql_pool = self.sql_pool()
        #server.odb_pool_config = self.odb_pool_config()
        #server.service_store = self.service_store()
        #server.wss_nonce_cache = self.wss_nonce_cache()
        #server.wss_store = self.wss_username_password_store()

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
        scheduler = Scheduler()
        scheduler.config_repo_manager = self.config_repo_manager()

        return scheduler

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

    # #######################################################
    # AMQP

    #@Object
    def amqp_config_connection_parameters(self):
        host = "127.0.0.1"
        port = 5672
        virtual_host = "/"
        user = "guest"
        password = "guest"

        creds = PlainCredentials(user, password)
        conn_params = ConnectionParameters(host, port, virtual_host, creds)

        return conn_params

    #@Object(scope.PROTOTYPE)
    #def amqp_config_para_client(self):
    #    return Client(self.amqp_config_connection_parameters(), "para")

    #@Object
    #def amqp_config_single_client(self):
    #    return Client(self.amqp_config_connection_parameters(), "single")
