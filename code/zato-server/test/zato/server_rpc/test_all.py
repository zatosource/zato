# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from unittest import main, TestCase

# Zato
from zato.common.ext.dataclasses import dataclass
from zato.common.odb.model import Base, HTTPBasicAuth, Cluster, Server as ServerModel
from zato.common.odb.api import ODBManager, SQLConnectionPool
from zato.common.typing_ import anydict, cast_, dict_field
from zato.server.connection.server.rpc.api import ConfigCtx, ServerRPC
from zato.server.connection.server.rpc.config import CredentialsConfig, ODBConfigSource
from zato.server.connection.server.rpc.invoker import LocalServerInvoker, RemoteServerInvoker, ServerInvoker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class TestConfig:
    crypto_use_tls = True
    cluster_name = 'rpc_test_cluster'
    api_credentials_password = 'api_credentials_password'

    server1_name = 'server1'
    server2_name = 'server2'
    server3_name = 'server3'

    server1_preferred_address = '10.151.1.1'
    server2_preferred_address = '10.152.2.2'
    server3_preferred_address = '10.152.3.3'

    server1_port = 1111
    server2_port = 2222
    server3_port = 3333

# ################################################################################################################################
# ################################################################################################################################

class TestCluster:
    def __init__(self, name:'str') -> 'None':
        self.name = name

# ################################################################################################################################
# ################################################################################################################################

class TestParallelServer:
    def __init__(
        self,
        cluster,    # type: TestCluster
        odb,        # type: ODBManager
        server_name # type: str
    ) -> 'None':
        self.cluster = cluster
        self.cluster_name = self.cluster.name
        self.odb = odb
        self.name = server_name

    def decrypt(self, data:'str') -> 'str':
        return data

# ################################################################################################################################
# ################################################################################################################################

class BaseTestServerInvoker:

    @dataclass(init=False)
    class InvocationEntry:
        args: tuple
        kwargs: dict

# ################################################################################################################################
# ################################################################################################################################

class TestLocalServerInvoker(LocalServerInvoker, BaseTestServerInvoker):

    def __init__(self, *args:'any_', **kwargs:'any_'):

        # Initialise our base class
        super().__init__(*args, **kwargs)

        # An entry is added each time self.invoke is called
        self.invocation_history = []

    def invoke(self, *args:'any_', **kwargs:'any_') -> 'None':

        entry = self.InvocationEntry()
        entry.args = args
        entry.kwargs = kwargs

        self.invocation_history.append(entry)

# ################################################################################################################################
# ################################################################################################################################

class TestRemoteServerInvoker(RemoteServerInvoker, BaseTestServerInvoker):

    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':

        # Initialise our base class
        super().__init__(*args, **kwargs)

        # An entry is added each time self.invoke is called
        self.invocation_history = []

    def invoke(self, *args:'any_', **kwargs:'any_') -> 'None':

        entry = self.InvocationEntry()
        entry.args = args
        entry.kwargs = kwargs

        self.invocation_history.append(entry)

# ################################################################################################################################
# ################################################################################################################################

class ServerRPCTestCase(TestCase):

    def setUp(self) -> 'None':

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
            cluster.name = TestConfig.cluster_name # type: ignore
            cluster.odb_type = 'sqlite' # type: ignore
            cluster.broker_host = 'localhost-test-broker-host' # type: ignore
            cluster.broker_port = 123456 # type: ignore
            cluster.lb_host = 'localhost-test-lb-host' # type: ignore
            cluster.lb_port = 1234561 # type: ignore
            cluster.lb_agent_port = 1234562 # type: ignore

            server1 = ServerModel()
            server1.cluster = cluster
            server1.name = TestConfig.server1_name # type: ignore
            server1.token = 'abc1' # type: ignore
            server1.preferred_address = TestConfig.server1_preferred_address # type: ignore
            server1.bind_port = TestConfig.server1_port # type: ignore
            server1.crypto_use_tls = TestConfig.crypto_use_tls # type: ignore

            server2 = ServerModel()
            server2.cluster = cluster
            server2.name = TestConfig.server2_name # type: ignore
            server2.token = 'abc2' # type: ignore
            server2.preferred_address = TestConfig.server2_preferred_address # type: ignore
            server2.bind_port = TestConfig.server2_port # type: ignore
            server2.crypto_use_tls = TestConfig.crypto_use_tls # type: ignore

            server3 = ServerModel()
            server3.cluster = cluster
            server3.name = TestConfig.server3_name # type: ignore
            server3.token = 'abc3' # type: ignore
            server3.preferred_address = TestConfig.server3_preferred_address # type: ignore
            server3.bind_port = TestConfig.server3_port # type: ignore
            server3.crypto_use_tls = TestConfig.crypto_use_tls # type: ignore

            api_credentials = HTTPBasicAuth()
            api_credentials.cluster = cluster # type: ignore
            api_credentials.is_active = True # type: ignore
            api_credentials.name = CredentialsConfig.sec_def_name # type: ignore
            api_credentials.username = CredentialsConfig.api_user # type: ignore
            api_credentials.realm = CredentialsConfig.sec_def_name # type: ignore
            api_credentials.password = TestConfig.api_credentials_password # type: ignore

            session.add(cluster)
            session.add(server1)
            session.add(server2)
            session.add(server3)
            session.add(api_credentials)

            session.commit()

# ################################################################################################################################

    def get_server_rpc(
        self,
        odb, # type: ODBManager
        local_server_invoker_class=None, # type: type[LocalServerInvoker]  | None
        remote_server_invoker_class=None # type: type[RemoteServerInvoker] | None
    ) -> 'ServerRPC':

        cluster = TestCluster(TestConfig.cluster_name)
        parallel_server = TestParallelServer(cluster, odb, TestConfig.server1_name)

        config_source = ODBConfigSource(parallel_server.odb, cluster.name, parallel_server.name, parallel_server.decrypt)
        config_ctx = ConfigCtx(
            config_source,
            cast_('ParallelServer', parallel_server),
            local_server_invoker_class = cast_('type[LocalServerInvoker]', local_server_invoker_class),
            remote_server_invoker_class = cast_('type[RemoteServerInvoker]', remote_server_invoker_class),
        )

        return ServerRPC(config_ctx)

# ################################################################################################################################

    def get_local_server_invoker(
        self,
        local_server_invoker_class=LocalServerInvoker # type: type[LocalServerInvoker]
    ) -> 'ServerInvoker':
        rpc = self.get_server_rpc(
            cast_('ODBManager', None),
            local_server_invoker_class = local_server_invoker_class
        )
        return rpc[TestConfig.server1_name]

# ################################################################################################################################

    def get_remote_server_invoker(
        self,
        server_name, # type: str
        remote_server_invoker_class=RemoteServerInvoker # type: type[RemoteServerInvoker]
    ) -> 'ServerInvoker':
        rpc = self.get_server_rpc(self.odb, remote_server_invoker_class=remote_server_invoker_class)
        return rpc[TestConfig.server2_name]

# ################################################################################################################################

    def test_get_item_local_server(self):

        invoker = self.get_local_server_invoker()

        self.assertIsInstance(invoker, ServerInvoker)
        self.assertIsInstance(invoker, LocalServerInvoker)

# ################################################################################################################################

    def test_get_item_remote_server(self):

        invoker = self.get_remote_server_invoker(TestConfig.server2_name)

        self.assertIsInstance(invoker, ServerInvoker)
        self.assertIsInstance(invoker, RemoteServerInvoker)

# ################################################################################################################################

    def test_invoke_local_server(self):

        local_server_invoker_class = cast_('type[LocalServerInvoker]', TestLocalServerInvoker)
        invoker = self.get_local_server_invoker(
            local_server_invoker_class = local_server_invoker_class
        )
        invoker = cast_('TestLocalServerInvoker', invoker)

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

        remote_server_invoker_class = cast_('type[RemoteServerInvoker]', TestRemoteServerInvoker)
        invoker = self.get_remote_server_invoker(
            TestConfig.server2_name,
            remote_server_invoker_class = remote_server_invoker_class
        )
        invoker = cast_('TestRemoteServerInvoker', invoker)

        args1 = (1, 2, 3, 4)
        kwargs1 = {'a1':'a2', 'b1':'b2'}

        args2 = (5, 6, 7, 8)
        kwargs2 = {'a3':'a4', 'b3':'b4'}

        invoker.invoke(*args1, **kwargs1)
        invoker.invoke(*args2, **kwargs2)

        history1 = invoker.invocation_history[0]
        history2 = invoker.invocation_history[1]

        self.assertTupleEqual(history1.args, args1)
        self.assertDictEqual(history1.kwargs, kwargs1)

        self.assertTupleEqual(history2.args, args2)
        self.assertDictEqual(history2.kwargs, kwargs2)

# ################################################################################################################################

    def test_remote_server_invocation_ctx_is_populated(self):
        """ Confirms that remote server's invocation_ctx contains remote address and API credentials.
        """
        remote_server_invoker_class = cast_('type[RemoteServerInvoker]', TestRemoteServerInvoker)
        invoker = self.get_remote_server_invoker(
            TestConfig.server2_name,
            remote_server_invoker_class = remote_server_invoker_class
        )
        invoker = cast_('TestRemoteServerInvoker', invoker)

        ctx = invoker.invocation_ctx

        self.assertEqual(ctx.address, TestConfig.server2_preferred_address)
        self.assertEqual(ctx.cluster_name, TestConfig.cluster_name)
        self.assertEqual(ctx.server_name, TestConfig.server2_name)
        self.assertEqual(ctx.username, CredentialsConfig.api_user)
        self.assertEqual(ctx.password, TestConfig.api_credentials_password)
        self.assertIs(ctx.crypto_use_tls, TestConfig.crypto_use_tls)

# ################################################################################################################################

    def test_populate_servers(self):

        # Get our RPC client ..
        server_rpc = self.get_server_rpc(self.odb, remote_server_invoker_class=RemoteServerInvoker)

        # .. this reads all the servers from the database ..
        server_rpc.populate_invokers()

        # .. so we can start our tests now.
        invoker_list = server_rpc._invokers

        self.assertEqual(len(invoker_list), 3)

        ctx1 = invoker_list['server1'].invocation_ctx
        ctx2 = invoker_list['server2'].invocation_ctx
        ctx3 = invoker_list['server3'].invocation_ctx

        self.assertEqual(ctx1.address, TestConfig.server1_preferred_address)
        self.assertEqual(ctx1.cluster_name, TestConfig.cluster_name)
        self.assertEqual(ctx1.server_name, TestConfig.server1_name)
        self.assertEqual(ctx1.username, CredentialsConfig.api_user)
        self.assertEqual(ctx1.password, TestConfig.api_credentials_password)
        self.assertIs(ctx1.crypto_use_tls, TestConfig.crypto_use_tls)

        self.assertEqual(ctx2.address, TestConfig.server2_preferred_address)
        self.assertEqual(ctx2.cluster_name, TestConfig.cluster_name)
        self.assertEqual(ctx2.server_name, TestConfig.server2_name)
        self.assertEqual(ctx2.username, CredentialsConfig.api_user)
        self.assertEqual(ctx2.password, TestConfig.api_credentials_password)
        self.assertIs(ctx2.crypto_use_tls, TestConfig.crypto_use_tls)

        self.assertEqual(ctx3.address, TestConfig.server3_preferred_address)
        self.assertEqual(ctx3.cluster_name, TestConfig.cluster_name)
        self.assertEqual(ctx3.server_name, TestConfig.server3_name)
        self.assertEqual(ctx3.username, CredentialsConfig.api_user)
        self.assertEqual(ctx3.password, TestConfig.api_credentials_password)
        self.assertIs(ctx3.crypto_use_tls, TestConfig.crypto_use_tls)

    def test_invoke_all(self):

        @dataclass(init=False)
        class TestServiceInvokeResponse:
            ok: bool = True
            has_data: bool = True
            details: str = ''
            data: anydict = dict_field()

        def invoke_func(server_name:'any_') -> 'any_':

            def _inner(service:'any_', request:'any_', skip_response_elem:'any_'=True, *args:'any_', **kwargs:'any_') -> 'any_':

                # This simulates a response from the Zato client ..
                response = TestServiceInvokeResponse()

                # .. keyed by PID ..
                data = {}

                pid_prefix = server_name[-1]
                pid_responses_len = 4

                # .. generate responses for several PIDs ..
                for idx in range(pid_responses_len):
                    pid_suffix = pid_prefix * 2 + str(idx)
                    pid = int(pid_prefix + pid_suffix)

                    # .. a per-PID response ..
                    pid_response = {
                        'is_ok': True,
                        'pid_data': {'pong':'zato-{}'.format(pid)},
                        'error_info': None,
                    }

                    # .. assign to output ..
                    data[pid] = pid_response

                # .. the overall reply ..
                response.data = data

                # .. now, we can return everything to the caller.
                return response

            return _inner

        class StaticRemoteServerInvoker(RemoteServerInvoker):
            def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
                super().__init__(*args, **kwargs)
                self.invocation_ctx.needs_ping = False
                self.invoker.invoke = invoke_func(self.server_name)

        service_name = 'zato.ping'
        request = {'abc':123}

        # Get our RPC client ..
        server_rpc = self.get_server_rpc(self.odb, remote_server_invoker_class=StaticRemoteServerInvoker)

        # .. invoke all the servers and PIDs ..
        response = server_rpc.invoke_all(service_name, request)

        # .. we have three servers with four PIDs each and we need to check each ..

        server1_pid_0_data = response.data[0]
        server1_pid_1_data = response.data[1]
        server1_pid_2_data = response.data[2]
        server1_pid_3_data = response.data[3]

        server2_pid_0_data = response.data[4]
        server2_pid_1_data = response.data[5]
        server2_pid_2_data = response.data[6]
        server2_pid_3_data = response.data[7]

        server3_pid_0_data = response.data[8]
        server3_pid_1_data = response.data[9]
        server3_pid_2_data = response.data[10]
        server3_pid_3_data = response.data[11]

        self.assertDictEqual(server1_pid_0_data, {'pong': 'zato-1110'})
        self.assertDictEqual(server1_pid_1_data, {'pong': 'zato-1111'})
        self.assertDictEqual(server1_pid_2_data, {'pong': 'zato-1112'})
        self.assertDictEqual(server1_pid_3_data, {'pong': 'zato-1113'})

        self.assertDictEqual(server2_pid_0_data, {'pong': 'zato-2220'})
        self.assertDictEqual(server2_pid_1_data, {'pong': 'zato-2221'})
        self.assertDictEqual(server2_pid_2_data, {'pong': 'zato-2222'})
        self.assertDictEqual(server2_pid_3_data, {'pong': 'zato-2223'})

        self.assertDictEqual(server3_pid_0_data, {'pong': 'zato-3330'})
        self.assertDictEqual(server3_pid_1_data, {'pong': 'zato-3331'})
        self.assertDictEqual(server3_pid_2_data, {'pong': 'zato-3332'})
        self.assertDictEqual(server3_pid_3_data, {'pong': 'zato-3333'})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
