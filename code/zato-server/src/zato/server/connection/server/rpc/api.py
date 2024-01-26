# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.ext.dataclasses import dataclass
from zato.common.typing_ import cast_, list_field
from zato.server.connection.server.rpc.invoker import LocalServerInvoker, RemoteServerInvoker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, generator_, stranydict
    from zato.server.base.parallel import ParallelServer
    from zato.server.connection.server.rpc.config import ConfigSource, RPCServerInvocationCtx
    from zato.server.connection.server.rpc.invoker import PerPIDResponse, ServerInvoker

    ConfigSource = ConfigSource
    ParallelServer = ParallelServer
    PerPIDResponse = PerPIDResponse
    RPCServerInvocationCtx = RPCServerInvocationCtx

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class InvokeAllResult:

    # By default, we assume that the invocation succeeded,
    # unless it is overwritten by one of the per-PID responses
    is_ok: 'bool' = True

    # This is a list of responses from each PID of each server
    data: 'anylist' = list_field()

# ################################################################################################################################
# ################################################################################################################################

class ConfigCtx:
    """ A config-like class that knows how to return details needed to invoke local or remote servers.
    """
    def __init__(self,
        config_source,   # type: ConfigSource
        parallel_server, # type: ParallelServer
        local_server_invoker_class = LocalServerInvoker,  # type: type[LocalServerInvoker]
        remote_server_invoker_class = RemoteServerInvoker # type: type[RemoteServerInvoker]
    ):
        self.config_source = config_source
        self.parallel_server = parallel_server
        self.local_server_invoker_class = local_server_invoker_class
        self.remote_server_invoker_class = remote_server_invoker_class

    def get_remote_server_invoker(self, server_name:'str') -> 'RemoteServerInvoker':
        ctx = self.config_source.get_server_ctx(self.parallel_server, self.config_source.current_cluster_name, server_name)
        return self.remote_server_invoker_class(ctx)

    def get_remote_server_invoker_list(self) -> 'generator_[ServerInvoker, None, None]':
        ctx_list = self.config_source.get_server_ctx_list(self.config_source.current_cluster_name)
        for ctx in ctx_list:
            if ctx.server_name == self.config_source.current_server_name:
                cluster_name = cast_('str', ctx.cluster_name)
                server_name  = cast_('str', ctx.server_name)
                invoker = self.local_server_invoker_class(self.parallel_server, cluster_name, server_name)
            else:
                invoker = self.remote_server_invoker_class(ctx)
            yield invoker

# ################################################################################################################################
# ################################################################################################################################

class ServerRPC:
    """ A facade through which Zato servers can be invoked.
    """
    def __init__(self, config_ctx:'ConfigCtx') -> 'None':
        self.config_ctx = config_ctx
        self.current_cluster_name = self.config_ctx.config_source.current_cluster_name
        self._invokers = {} # type: stranydict
        self.logger = getLogger('zato')

# ################################################################################################################################

    def _get_invoker_by_server_name(self, server_name:'str') -> 'ServerInvoker':
        if server_name == self.config_ctx.parallel_server.name:
            invoker = self.config_ctx.local_server_invoker_class(
                self.config_ctx.parallel_server,
                self.config_ctx.parallel_server.cluster_name,
                self.config_ctx.parallel_server.name,
            )
        else:
            invoker = self.config_ctx.get_remote_server_invoker(server_name)

        return invoker

# ################################################################################################################################

    def get_invoker_by_server_name(self, server_name:'str') -> 'ServerInvoker':

        has_invoker_by_server_name = server_name in self._invokers

        if not has_invoker_by_server_name:
            invoker = self._get_invoker_by_server_name(server_name)
            self._invokers[server_name] = invoker

        invoker = self._invokers[server_name]
        return invoker

# ################################################################################################################################

    def populate_invokers(self) -> 'None':
        for invoker in self.config_ctx.get_remote_server_invoker_list():
            self._invokers[invoker.server_name] = invoker

# ################################################################################################################################

    def invoke_all(
        self,
        service,        # type: str
        request = None, # type: any_
        *args,          # type: any_
        **kwargs        # type: any_
    ) -> 'InvokeAllResult':

        # First, make sure that we are aware of all the servers currently available
        self.populate_invokers()

        # Response to produce
        out = InvokeAllResult()

        # Now, invoke all the servers ..
        for invoker in self._invokers.values():
            invoker = cast_('ServerInvoker', invoker)

            # .. each response object received is a list of sub-responses,
            # .. with each sub-response representing a specific PID ..
            response = invoker.invoke_all_pids(service, request, *args, **kwargs)
            out.data.extend(response)

        # .. now we can return the result.
        return out

# ################################################################################################################################
# ################################################################################################################################
