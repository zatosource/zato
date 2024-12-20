# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from contextlib import closing
from dataclasses import dataclass
from unittest import main, TestCase
from uuid import uuid4

# Zato
from zato.common.api import INFO_FORMAT
from zato.common.component_info import get_info
from zato.common.odb.model import Base, HTTPBasicAuth, Cluster, Server as ServerModel
from zato.common.odb.api import ODBManager, SQLConnectionPool
from zato.common.test import TestCluster, TestParallelServer
from zato.common.typing_ import cast_
from zato.common.util.api import get_client_from_server_conf, get_new_tmp_full_path
from zato.common.util.open_ import open_w
from zato.server.connection.server.rpc.api import ConfigCtx, ServerRPC
from zato.server.connection.server.rpc.config import CredentialsConfig, ODBConfigSource, RPCServerInvocationCtx
from zato.server.connection.server.rpc.invoker import LocalServerInvoker, RemoteServerInvoker, ServerInvoker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anytuple, intstrdict
    from zato.server.base.parallel import ParallelServer
    ParallelServer = ParallelServer
    anylist = anylist
    intstrdict = intstrdict

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

class BaseTestServerInvoker:

    @dataclass(init=False)
    class InvocationEntry:
        args: 'anytuple'
        kwargs: 'anydict'

# ################################################################################################################################
# ################################################################################################################################

class TestLocalServerInvoker(LocalServerInvoker, BaseTestServerInvoker):

    def __init__(self, *args:'any_', **kwargs:'any_'):

        # Initialise our base class
        super().__init__(*args, **kwargs)

        # An entry is added each time self.invoke is called
        self.invocation_history = [] # type: anylist

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
        self.invocation_history = [] # type: anylist

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
        } # type: anydict

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
        return rpc.get_invoker_by_server_name(TestConfig.server1_name)

# ################################################################################################################################

    def get_remote_server_invoker(
        self,
        server_name, # type: str
        remote_server_invoker_class=RemoteServerInvoker # type: type[RemoteServerInvoker]
    ) -> 'ServerInvoker':
        rpc = self.get_server_rpc(self.odb, remote_server_invoker_class=remote_server_invoker_class)
        return rpc.get_invoker_by_server_name(TestConfig.server2_name)

# ################################################################################################################################

    def xtest_get_item_local_server(self):

        invoker = self.get_local_server_invoker()

        self.assertIsInstance(invoker, ServerInvoker)
        self.assertIsInstance(invoker, LocalServerInvoker)

# ################################################################################################################################

    def xtest_get_item_remote_server(self):

        invoker = self.get_remote_server_invoker(TestConfig.server2_name)

        self.assertIsInstance(invoker, ServerInvoker)
        self.assertIsInstance(invoker, RemoteServerInvoker)

# ################################################################################################################################

    def xtest_invoke_local_server(self):

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

    def xtest_invoke_remote_server(self):

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

    def xtest_remote_server_invocation_ctx_is_populated(self):
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

    def xtest_populate_servers(self):

        # Get our RPC client ..
        server_rpc = self.get_server_rpc(
            self.odb,
            local_server_invoker_class=LocalServerInvoker,
            remote_server_invoker_class=RemoteServerInvoker
        )

        # .. this reads all the servers from the database ..
        server_rpc.populate_invokers()

        # .. so we can start our tests now.
        invoker_list = server_rpc._invokers

        # The first invoker is a local one. The other ones are remote.
        invoker1 = invoker_list['server1']
        invoker2 = invoker_list['server2']
        invoker3 = invoker_list['server3']

        self.assertIsInstance(invoker1, LocalServerInvoker)
        self.assertIsInstance(invoker2, RemoteServerInvoker)
        self.assertIsInstance(invoker3, RemoteServerInvoker)

        # Note that the invocation context is populated only for remote invokers
        # which is why we check ctx2 and ctx3 here but not ctx1.
        ctx2 = invoker2.invocation_ctx
        ctx3 = invoker3.invocation_ctx

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

    def test_invoke_all_pids_using_a_remote_invoker(self):

        if not(server_root_dir := os.environ.get('Zato_Test_Server_Root_Dir')):
            return

        # We are going to write random data to a file for each worker PID
        # and then all the PIDs will be invoked. It is expected that each
        # PID will read its data from that file and create a new file
        # with its response which we will read to confirm that the PID
        # indeed has been invoked.

        # Local aliases
        service_name = 'zato.ping'

        # Note that this test requires that at least two workers be present
        # because it tests multi-CPU configuration.
        min_workers = 2

        # Configuration read from the environment
        server_host = os.environ.get('Zato_Test_Server_Host')
        server_port = cast_('str', os.environ.get('Zato_Test_Server_Port'))
        server_port = int(server_port)

        # An invocation client that we can extract the underlying configuration from
        client = get_client_from_server_conf(server_root_dir, url_path=RemoteServerInvoker.url_path)

        # Build the overall configuration context object
        ctx = RPCServerInvocationCtx()
        ctx.cluster_name = 'ServerRPCTestCase-Cluster-Name'
        ctx.server_name  = 'ServerRPCTestCase-Server-Name'
        ctx.address = server_host
        ctx.port = server_port
        ctx.username = client.username
        ctx.password = client.password

        # Create the invoker ..
        invoker = RemoteServerInvoker(ctx)

        # .. and ping it immediately to make sure the configuration is correct.
        invoker.ping()

        # Now, obtain all the PIDs of the workers in the current server.
        server_info = get_info(server_root_dir, INFO_FORMAT.DICT)

        # Make sure we have enough worker processes to continue
        master_proc_workers_no = server_info['master_proc_workers_no']
        master_proc_workers_no = cast_('int', master_proc_workers_no)
        if master_proc_workers_no < min_workers:
            msg = f'Server from {server_root_dir} should have at least {min_workers} workers instead of {master_proc_workers_no}'
            raise Exception(msg)

        # The request will be populated with data for each PID in the loop below
        request = {} # type: intstrdict

        # Go through all the PIDs found ..
        for pid in server_info['master_proc_workers_pids']:

            # This is reusable
            random_pid_data = uuid4().hex

            # Random data for that pid
            pid_data = f'pid:{pid}:' + random_pid_data + '\n'

            # A random file for that PID
            prefix = f'pid-request-{pid}'
            tmp_file_path = get_new_tmp_full_path(prefix=prefix, random_suffix=random_pid_data)

            # Write the data for this PID
            with open_w(tmp_file_path) as f:
                _ = f.write(pid_data)

            # Populate the request
            request[pid] = random_pid_data

        # .. now, we can invoke all the PIDs with our request on input ..
        _ = invoker.invoke_all_pids(service_name, request)

        # .. close the underlying socket ..
        invoker.close()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
