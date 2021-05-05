# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Requests
from requests import get as requests_get

# Zato
from zato.client import AnyServiceInvoker
from zato.common.ext.dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from typing import Callable
    from zato.client import ServiceInvokeResponse
    from zato.server.connection.server.rpc.config import RemoteServerInvocationCtx

    Callable = Callable
    RemoteServerInvocationCtx = RemoteServerInvocationCtx
    Response = Response
    ServiceInvokeResponse = ServiceInvokeResponse

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class InvocationResult:
    is_ok: bool
    has_data: bool
    data: object
    error: object

# ################################################################################################################################
# ################################################################################################################################

class ServerInvoker:
    """ A base class for local and remote server invocations.
    """
    def __init__(self, cluster_name, server_name):
        # type: (str, str) -> None
        self.cluster_name = cluster_name
        self.server_name = server_name

    def invoke(self, *args, **kwargs):
        raise NotImplementedError()

    def invoke_async(self, *args, **kwargs):
        raise NotImplementedError()

    def invoke_all_pids(self, *args, **kwargs):
        raise NotImplementedError()

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
        self.invocation_ctx = ctx

        # We need to cover both HTTP and HTTPS connections to other servers
        protocol = 'https' if self.invocation_ctx.crypto_use_tls else 'http'

        # These two are used to ping each server right before an actual request is sent - with a short timeout,
        # this lets out quickly discover whether the server is up and running.
        self.ping_address = '{}://{}:{}/zato/ping'.format(protocol, self.invocation_ctx.address, self.invocation_ctx.port)
        self.ping_timeout = 1

        # Build the full address to the remote server
        self.address = '{}://{}:{}'.format(protocol, self.invocation_ctx.address, self.invocation_ctx.port)

        # Credentials to connect to the remote server with
        credentials = (self.invocation_ctx.username, self.invocation_ctx.password)

        # Now, we can build a client to the remote server
        self.invoker = AnyServiceInvoker(self.address, '/zato/internal/invoke', credentials)

# ################################################################################################################################

    def _invoke(self, invoke_func, service, request=None, *args, **kwargs):
        # type: (Callable, str, object) -> InvocationResult

        # Ping the remote server to quickly find out if it is still available ..
        requests_get(self.ping_address, timeout=self.ping_timeout)

        # .. actually invoke the server now ..
        response = invoke_func(service, request, skip_response_elem=True, *args, **kwargs) # type: ServiceInvokeResponse

        # .. build the results object ..
        out = InvocationResult()
        out.is_ok = response.ok
        out.has_data = response.has_data
        out.data = response.data
        out.error = response.details

        # .. and return the result to our caller.
        return out

# ################################################################################################################################

    def invoke(self, *args, **kwargs):
        return self._invoke(self.invoker.invoke, *args, **kwargs)

# ################################################################################################################################

    def invoke_async(self, *args, **kwargs):
        return self._invoke(self.invoker.invoke_async, *args, **kwargs)

# ################################################################################################################################

    def invoke_all_pids(self, *args, **kwargs):
        kwargs['all_pids'] = True
        return self._invoke(self.invoker.invoke, *args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################
