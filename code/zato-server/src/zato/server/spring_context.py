# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from zato.bunch import Bunch

# Spring Python
from springpython.config import Object, PythonConfig

# Zato
from zato.common import ZATO_CRYPTO_WELL_KNOWN_DATA
from zato.common.kvdb import KVDB
from zato.common.odb.api import ODBManager, PoolStore
from zato.server.base.parallel import ParallelServer
from zato.server.service.store import ServiceStore

class ZatoContext(PythonConfig):

    # #######################################################
    # Services

    @Object
    def service_store(self):
        store = ServiceStore()
        store.odb = self.odb_manager()
        store.services = {}

        return store

    @Object
    def service_modules(self):
        return []

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
        server.service_modules = self.service_modules()
        server.kvdb = self.kvdb()
        server.user_config = Bunch()

        return server
