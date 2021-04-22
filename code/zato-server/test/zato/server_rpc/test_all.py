# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.server.connection.server.rpc import LocalServer, Server, ServerRPC

# ################################################################################################################################
# ################################################################################################################################

class _FakeParallelServer:
    def __init__(self, name):
        # type: (str) -> None
        self.name = name

# ################################################################################################################################
# ################################################################################################################################

class ServerRPCTestCase(TestCase):

    def xtest_get_item_local_server(self):

        server_name = 'abc'
        parallel_server = _FakeParallelServer(server_name)

        # These three will not be called because the server is local
        get_remote_server_func = object
        get_server_list_func = object
        decrypt_func = object

        rpc = ServerRPC(parallel_server, get_remote_server_func, get_server_list_func, decrypt_func)

        server = rpc[server_name]

        self.assertIsInstance(server, Server)
        self.assertIsInstance(server, LocalServer)

# ################################################################################################################################

    def test_get_item_remote_server(self):

        server_name = 'abc'
        parallel_server = _FakeParallelServer(server_name)

        get_remote_server_func = object
        decrypt_func = object

        # This one will not be called because we access a specific server by name
        get_server_list_func = object

        rpc = ServerRPC(parallel_server, get_remote_server_func, get_server_list_func, decrypt_func)

        server = rpc['not-local']

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
