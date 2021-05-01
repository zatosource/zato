# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# SQLAlchemy
from sqlalchemy import create_engine

# Zato
from zato.common.odb.model import Base
from zato.common.odb.api import SessionWrapper
from zato.server.connection.server.rpc.api import ConfigCtx, ServerRPC
from zato.server.connection.server.rpc.config import ODBConfigSource
from zato.server.connection.server.rpc.invoker import LocalServerInvoker, RemoteServerInvoker, ServerInvoker

# ################################################################################################################################
# ################################################################################################################################

class _TestCluster:
    def __init__(self, name):
        # type: (str) -> None
        self.name = name

# ################################################################################################################################
# ################################################################################################################################

class _TestParallelServer:
    def __init__(self, cluster, odb, server_name):
        # type: (_TestCluster, SessionWrapper, str) -> None
        self.cluster = cluster
        self.odb = odb
        self.name = server_name

# ################################################################################################################################
# ################################################################################################################################

class ServerRPCTestCase(TestCase):

    def setUp(self):
        engine =  create_engine('sqlite://')

        Base.metadata.create_all(engine)

        print(111, dir(engine))
        print(222, engine.table_names())

# ################################################################################################################################

    def xtest_get_item_local_server(self):

        cluster_name = 'cluster.1'
        server_name = 'abc'

        cluster = _TestCluster(cluster_name)
        parallel_server = _TestParallelServer(cluster, None, server_name)

        # These three will not be called because the server is local
        get_remote_server_func = object
        get_server_list_func = object
        decrypt_func = object

        config_source = ODBConfigSource(parallel_server.odb, cluster.name, parallel_server.name)
        config_ctx = ConfigCtx(config_source, parallel_server)

        rpc = ServerRPC(config_ctx)

        server = rpc[server_name]

        self.assertIsInstance(server, ServerInvoker)
        self.assertIsInstance(server, LocalServerInvoker)

# ################################################################################################################################

    def test_get_item_remote_server(self):

        cluster_name = 'cluster.1'
        server_name = 'abc'

        odb = SessionWrapper()
        #odb.init_session()

        return

        cluster = _TestCluster(cluster_name)
        parallel_server = _TestParallelServer(cluster, odb, server_name)

        get_remote_server_func = object
        decrypt_func = object

        # This one will not be called because we access a specific server by name
        get_server_list_func = object

        config_source = ODBConfigSource(parallel_server.odb, cluster.name, parallel_server.name)
        config_ctx = ConfigCtx(config_source, parallel_server)

        rpc = ServerRPC(config_ctx)

        server = rpc['not-local']

        self.assertIsInstance(server, ServerInvoker)
        self.assertIsInstance(server, RemoteServerInvoker)

        print(111, server.invoke('zzz'))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
