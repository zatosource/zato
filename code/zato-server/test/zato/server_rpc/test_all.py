# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from unittest import main, TestCase

# SQLAlchemy
from sqlalchemy import create_engine

# Zato
from zato.common.odb.model import Base, HTTPBasicAuth, Cluster, Server as ServerModel
from zato.common.odb.api import ODBManager, SQLConnectionPool
from zato.common.util.api import get_session
from zato.server.connection.server.rpc.api import ConfigCtx, ServerRPC
from zato.server.connection.server.rpc.config import CredentialsConfig, ODBConfigSource
from zato.server.connection.server.rpc.invoker import LocalServerInvoker, RemoteServerInvoker, ServerInvoker

# ################################################################################################################################
# ################################################################################################################################

class TestConfig:
    cluster_name = 'rpc_test_cluster'
    server1 = 'server1'
    server2 = 'server2'

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
        # type: (_TestCluster, ODBManager, str) -> None
        self.cluster = cluster
        self.odb = odb
        self.name = server_name

# ################################################################################################################################
# ################################################################################################################################

class ServerRPCTestCase(TestCase):

    def setUp(self):

        # Prepare in-memory ODB configuration ..
        odb_name = 'ServerRPCTestCase'
        odb_config = {
            'engine': 'sqlite',
            'is_active': True,
            'fs_sql_config': {},
            'echo': True,
        }

        pool_config = {
            'engine': 'sqlite',
            'path': ':memory:',
            'echo': True,
        }

        # .. set up ODB ..
        odb_pool = SQLConnectionPool(odb_name, odb_config, odb_config)
        self.odb = ODBManager()
        self.odb.init_session(odb_name, odb_config, odb_pool)

        # .. create SQL schema ..
        Base.metadata.create_all(self.odb.pool.engine)

        with closing(self.odb.session()) as session:

            cluster = Cluster()
            cluster.name = TestConfig.cluster_name
            cluster.odb_type = 'sqlite'
            cluster.broker_host = 'localhost-test-broker-host'
            cluster.broker_port = 123456
            cluster.lb_host = 'localhost-test-lb-host'
            cluster.lb_port = 1234561
            cluster.lb_agent_port = 1234562

            server1 = ServerModel()
            server1.cluster = cluster
            server1.name = TestConfig.server1
            server1.token = 'abc'

            server2 = ServerModel()
            server2.cluster = cluster
            server2.name = TestConfig.server2
            server2.token = 'abc'

            api_credentials = HTTPBasicAuth()
            api_credentials.cluster = cluster
            api_credentials.is_active = True
            api_credentials.name = CredentialsConfig.sec_def_name
            api_credentials.username = CredentialsConfig.api_user
            api_credentials.realm = CredentialsConfig.sec_def_name

            session.add(cluster)
            session.add(server1)
            session.add(server2)
            session.add(api_credentials)

            session.commit()

# ################################################################################################################################

    def test_get_item_local_server(self):

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

        cluster = _TestCluster(TestConfig.cluster_name)
        parallel_server = _TestParallelServer(cluster, self.odb, TestConfig.server1)

        get_remote_server_func = object
        decrypt_func = object

        # This one will not be called because we access a specific server by name
        get_server_list_func = object

        config_source = ODBConfigSource(parallel_server.odb, cluster.name, parallel_server.name)
        config_ctx = ConfigCtx(config_source, parallel_server)

        rpc = ServerRPC(config_ctx)

        server = rpc[TestConfig.server2]

        self.assertIsInstance(server, ServerInvoker)
        self.assertIsInstance(server, RemoteServerInvoker)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
