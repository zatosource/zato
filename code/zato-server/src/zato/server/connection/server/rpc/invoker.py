# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Requests
from requests import get as requests_get

# Zato
from zato.client import AnyServiceInvoker
from zato.common.ext.dataclasses import dataclass
from zato.common.typing_ import any_, cast_, dict_field

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from typing import Callable
    from zato.client import ServiceInvokeResponse
    from zato.common.typing_ import anydict, anylist, callable_, intnone, stranydict, strordictnone
    from zato.server.base.parallel import ParallelServer
    from zato.server.connection.server.rpc.config import RPCServerInvocationCtx

    Callable = Callable
    ParallelServer = ParallelServer
    RPCServerInvocationCtx = RPCServerInvocationCtx
    Response = Response
    ServiceInvokeResponse = ServiceInvokeResponse

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ServerInvocationResult:
    is_ok: 'bool' = False
    has_data: 'bool' = False
    data: 'anydict' = dict_field()
    error_info: 'any_' = ''

@dataclass
class PerPIDResponse:
    is_ok: 'bool' = False
    pid: 'int' = 0
    pid_data: 'strordictnone' = dict_field()
    error_info: 'any_' = ''

# ################################################################################################################################
# ################################################################################################################################

class ServerInvoker:
    """ A base class for local and remote server invocations.
    """
    def __init__(self, parallel_server:'ParallelServer', cluster_name:'str', server_name:'str') -> 'None':

        # This parameter is used for local invocations only
        # to have access to self.parallel_server.invoke/.invoke_async/.invoke_all_pids
        self.parallel_server = parallel_server

        self.cluster_name = cluster_name
        self.server_name = server_name

    def invoke(self, *args:'any_', **kwargs:'any_') -> 'any_':
        raise NotImplementedError(self.__class__)

    def invoke_async(self, *args:'any_', **kwargs:'any_') -> 'any_':
        raise NotImplementedError(self.__class__)

    def invoke_all_pids(self, *args:'any_', **kwargs:'any_') -> 'anylist':
        raise NotImplementedError(self.__class__)

# ################################################################################################################################
# ################################################################################################################################

class LocalServerInvoker(ServerInvoker):
    """ Invokes services directly on the current server, without any network-based RPC.
    """
    def invoke(self, *args:'any_', **kwargs:'any_') -> 'any_':
        response = self.parallel_server.invoke(*args, **kwargs)
        return response

# ################################################################################################################################

    def invoke_async(self, *args:'any_', **kwargs:'any_') -> 'any_':
        response = self.parallel_server.invoke_async(*args, **kwargs)
        return response

# ################################################################################################################################

    def invoke_all_pids(self, *args:'any_', **kwargs:'any_') -> 'anylist':
        response = self.parallel_server.invoke_all_pids(*args, **kwargs)
        return response

# ################################################################################################################################
# ################################################################################################################################

class RemoteServerInvoker(ServerInvoker):
    """ Invokes services on a remote server using RPC.
    """
    url_path = '/zato/internal/invoke'

    def __init__(self, ctx:'RPCServerInvocationCtx') -> 'None':
        super().__init__(
            cast_('ParallelServer', None),
            cast_('str', ctx.cluster_name),
            cast_('str', ctx.server_name),
        )
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
        self.invoker = AnyServiceInvoker(self.address, self.url_path, credentials)

# ################################################################################################################################

    def ping(self, ping_timeout:'intnone'=None) -> 'None':
        ping_timeout = ping_timeout or self.ping_timeout
        _ = requests_get(self.ping_address, timeout=ping_timeout)

# ################################################################################################################################

    def close(self) -> 'None':
        self.invoker.session.close()

# ################################################################################################################################

    def _invoke(
        self,
        invoke_func,           # type: callable_
        service:'str',         # type: str
        request:'any_' = None, # type: any_
        *args:'any_',          # type: any_
        **kwargs:'any_'        # type: any_
    ) -> 'stranydict | anylist | str | None':

        if not self.invocation_ctx.address:
            logger.info('RPC address not found for %s:%s -> `%r` (%s)',
                self.invocation_ctx.cluster_name,
                self.invocation_ctx.server_name,
                self.address,
                service)
            return

        # Optionally, ping the remote server to quickly find out if it is still available ..
        if self.invocation_ctx.needs_ping:
            ping_timeout = kwargs.get('ping_timeout') or self.ping_timeout
            _ = requests_get(self.ping_address, timeout=ping_timeout)

        # .. actually invoke the server now ..
        response = invoke_func(service, request, *args, **kwargs) # type: ServiceInvokeResponse
        response = response.data

        return response

# ################################################################################################################################

    def invoke(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self._invoke(self.invoker.invoke, *args, **kwargs)

# ################################################################################################################################

    def invoke_async(self, *args:'any_', **kwargs:'any_') -> 'any_':
        return self._invoke(self.invoker.invoke_async, *args, **kwargs)

# ################################################################################################################################

    def invoke_all_pids(self, *args:'any_', **kwargs:'any_') -> 'any_':
        kwargs['all_pids'] = True
        skip_response_elem = kwargs.pop('skip_response_elem', True)
        return self._invoke(self.invoker.invoke, skip_response_elem=skip_response_elem, *args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################
