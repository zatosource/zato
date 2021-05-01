# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.connection.server.rpc.config import RemoteServerInvocationCtx

    RemoteServerInvocationCtx = RemoteServerInvocationCtx

# ################################################################################################################################
# ################################################################################################################################

class ServerInvoker:
    """ A base class for local and remote server invocations.
    """
    def __init__(self, cluster_name, server_name):
        # type: (str, str) -> None
        self.cluster_name = cluster_name
        self.server_name = server_name

    def invoke(self, service_name, request=None, pid=None):
        # type: (str, dict, int) -> None
        pass

# ################################################################################################################################
# ################################################################################################################################

class LocalServerInvoker(ServerInvoker):
    """ Invokes services directly on the current server, without any RPC.
    """

# ################################################################################################################################
# ################################################################################################################################

class RemoteServerInvoker(ServerInvoker):
    """ Invokes services on a remote server using RPC.
    """
    def __init__(self, ctx):
        # type: (RemoteServerInvocationCtx) -> None
        super().__init__(ctx.cluster_name, ctx.server_name)
        self.remote_server_invocation_ctx = ctx

# ################################################################################################################################
# ################################################################################################################################
