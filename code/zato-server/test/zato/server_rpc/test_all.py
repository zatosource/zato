# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from unittest import main, TestCase

# Zato
from zato.common.ext.dataclasses import dataclass
from zato.common.odb.model import Base, HTTPBasicAuth, Cluster, Server as ServerModel
from zato.common.odb.api import ODBManager, SQLConnectionPool
from zato.server.connection.server.rpc.api import ConfigCtx, ServerRPC
from zato.server.connection.server.rpc.config import CredentialsConfig, ODBConfigSource, RemoteServerInvocationCtx
from zato.server.connection.server.rpc.invoker import LocalServerInvoker, RemoteServerInvoker, \
     ServerInvoker

# ################################################################################################################################
# ################################################################################################################################

class TestConfig:
    cluster_name = 'rpc_test_cluster'
    server1 = 'server1'
    server2 = 'server2'
    server3 = 'server3'

# ################################################################################################################################
# ################################################################################################################################

class TestCluster:
    def __init__(self, name):
        # type: (str) -> None
        self.name = name

# ################################################################################################################################
# ################################################################################################################################

class TestParallelServer:
    def __init__(self, cluster, odb, server_name):
        # type: (TestCluster, ODBManager, str) -> None
        self.cluster = cluster
        self.odb = odb
        self.name = server_name

# ################################################################################################################################
# ################################################################################################################################

class BaseTestServerInvoker:

    @dataclass
    class InvocationEntry:
        args: tuple
        kwargs: dict

# ################################################################################################################################
# ################################################################################################################################

class TestLocalServerInvoker(LocalServerInvoker, BaseTestServerInvoker):

    def __init__(self, *args, **kwargs):

        # Initialise our base class
        super().__init__(*args, **kwargs)

        # An entry is added each time self.invoke is called
        self.invocation_history = []

    def invoke(self, *args, **kwargs):
        self.invocation_history.append(self.InvocationEntry(args, kwargs))

# ################################################################################################################################
# ################################################################################################################################

class TestRemoteServerInvoker(RemoteServerInvoker, BaseTestServerInvoker):

    def __init__(self, *args, **kwargs):

        # Initialise our base class
        super().__init__(*args, **kwargs)

        # An entry is added each time self.invoke is called
        self.invocation_history = []

    def invoke(self, *args, **kwargs):
        self.invocation_history.append(self.InvocationEntry(args, kwargs))

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
            server1.token = 'abc1'

            server2 = ServerModel()
            server2.cluster = cluster
            server2.name = TestConfig.server2
            server2.token = 'abc2'

            server3 = ServerModel()
            server3.cluster = cluster
            server3.name = TestConfig.server3
            server3.token = 'abc3'

            api_credentials = HTTPBasicAuth()
            api_credentials.cluster = cluster
            api_credentials.is_active = True
            api_credentials.name = CredentialsConfig.sec_def_name
            api_credentials.username = CredentialsConfig.api_user
            api_credentials.realm = CredentialsConfig.sec_def_name

            session.add(cluster)
            session.add(server1)
            session.add(server2)
            session.add(server3)
            session.add(api_credentials)

            session.commit()

# ################################################################################################################################

    def get_local_server_invoker(self, local_server_invoker_class=LocalServerInvoker):

        cluster = TestCluster(TestConfig.cluster_name)
        parallel_server = TestParallelServer(cluster, None, TestConfig.server1)

        config_source = ODBConfigSource(parallel_server.odb, cluster.name, parallel_server.name)
        config_ctx = ConfigCtx(config_source, parallel_server, local_server_invoker_class=local_server_invoker_class)

        rpc = ServerRPC(config_ctx)
        invoker = rpc[TestConfig.server1]

        return invoker

# ################################################################################################################################

    def get_remote_server_invoker(self, server_name, remote_server_invoker_class=RemoteServerInvoker):

        cluster = TestCluster(TestConfig.cluster_name)
        parallel_server = TestParallelServer(cluster, self.odb, TestConfig.server1)

        config_source = ODBConfigSource(parallel_server.odb, cluster.name, parallel_server.name)
        config_ctx = ConfigCtx(config_source, parallel_server, remote_server_invoker_class=remote_server_invoker_class)

        rpc = ServerRPC(config_ctx)
        invoker = rpc[TestConfig.server2]

        return invoker

# ################################################################################################################################

    def test_get_item_local_server(self):

        invoker = self.get_local_server_invoker()

        self.assertIsInstance(invoker, ServerInvoker)
        self.assertIsInstance(invoker, LocalServerInvoker)

# ################################################################################################################################

    def test_get_item_remote_server(self):

        invoker = self.get_remote_server_invoker(TestConfig.server2)

        self.assertIsInstance(invoker, ServerInvoker)
        self.assertIsInstance(invoker, RemoteServerInvoker)

# ################################################################################################################################

    def test_invoke_local_server(self):

        invoker = self.get_local_server_invoker(
            local_server_invoker_class=TestLocalServerInvoker) # type: TestLocalServerInvoker

        args1 = (1, 2, 3, 4)
        kwargs1 = {'a1':'a2', 'b1':'b2'}

        args2 = (5, 6, 7, 8)
        kwargs2 = {'a3':'a4', 'b3':'b4'}

        invoker.invoke(*args1, **kwargs1)
        invoker.invoke(*args2, **kwargs2)

        history1 = invoker.invocation_history[0] # type: TestLocalServerInvoker.InvocationEntry
        history2 = invoker.invocation_history[1] # type: TestLocalServerInvoker.InvocationEntry

        self.assertTupleEqual(history1.args, args1)
        self.assertDictEqual(history1.kwargs, kwargs1)

        self.assertTupleEqual(history2.args, args2)
        self.assertDictEqual(history2.kwargs, kwargs2)

# ################################################################################################################################

    def test_invoke_remote_server(self):

        invoker = self.get_remote_server_invoker(
            TestConfig.server2, remote_server_invoker_class=TestRemoteServerInvoker) # type: TestRemoteServerInvoker

        args1 = (1, 2, 3, 4)
        kwargs1 = {'a1':'a2', 'b1':'b2'}

        args2 = (5, 6, 7, 8)
        kwargs2 = {'a3':'a4', 'b3':'b4'}

        invoker.invoke(*args1, **kwargs1)
        invoker.invoke(*args2, **kwargs2)

        history1 = invoker.invocation_history[0] # type: TestRemoteServerInvoker.InvocationEntry
        history2 = invoker.invocation_history[1] # type: TestRemoteServerInvoker.InvocationEntry

        self.assertTupleEqual(history1.args, args1)
        self.assertDictEqual(history1.kwargs, kwargs1)

        self.assertTupleEqual(history2.args, args2)
        self.assertDictEqual(history2.kwargs, kwargs2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
