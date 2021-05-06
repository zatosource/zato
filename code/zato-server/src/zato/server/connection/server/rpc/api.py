# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.ext.dataclasses import dataclass, field
from zato.server.connection.server.rpc.invoker import LocalServerInvoker, RemoteServerInvoker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.base.parallel import ParallelServer
    from zato.server.connection.server.rpc.config import ConfigSource, RemoteServerInvocationCtx
    from zato.server.connection.server.rpc.invoker import PerPIDResponse, ServerInvoker

    ConfigSource = ConfigSource
    ParallelServer = ParallelServer
    RemoteServerInvocationCtx = RemoteServerInvocationCtx

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class InvokeAllResult:

    # By default, we assume that the invocation succeeded,
    # unless it is overwritten by one of the per-PID responses
    is_ok: bool = True

    # This is a list of responses from each PID of each server
    data: list = field(default_factory=list)

# ################################################################################################################################
# ################################################################################################################################

class ConfigCtx:
    """ A config-like class that knows how to return details needed to invoke local or remote servers.
    """
    def __init__(self,
            config_source,
            parallel_server,
            local_server_invoker_class=LocalServerInvoker,
            remote_server_invoker_class=RemoteServerInvoker
        ):
        # type: (ConfigSource, ParallelServer) -> None
        self.config_source = config_source
        self.parallel_server = parallel_server
        self.local_server_invoker_class = local_server_invoker_class
        self.remote_server_invoker_class = remote_server_invoker_class

    def get_remote_server_invoker(self, server_name):
        # type: (str) -> RemoteServerInvoker
        ctx = self.config_source.get_server_ctx(self.config_source.current_cluster_name, server_name)
        return self.remote_server_invoker_class(ctx)

    def get_remote_server_invoker_list(self):
        # type: (str) -> list[RemoteServerInvoker]
        ctx_list = self.config_source.get_server_ctx_list(self.config_source.current_cluster_name)
        for ctx in ctx_list: # type: RemoteServerInvocationCtx
            yield self.remote_server_invoker_class(ctx)

# ################################################################################################################################
# ################################################################################################################################

class ServerRPC:
    """ A facade through which Zato servers can be invoked.
    """
    def __init__(self, config_ctx):
        # type: (ConfigCtx) -> None
        self.config_ctx = config_ctx
        self.current_cluster_name = self.config_ctx.config_source.current_cluster_name
        self._invokers = {}

# ################################################################################################################################

    def _get_invoker_by_server_name(self, server_name):
        # type: (str) -> ServerInvoker
        if server_name == self.config_ctx.parallel_server.name:
            return self.config_ctx.local_server_invoker_class(self.current_cluster_name, server_name)
        else:
            return self.config_ctx.get_remote_server_invoker(server_name)

# ################################################################################################################################

    def __getitem__(self, server_name):
        # type: (str) -> ServerInvoker
        if server_name not in self._invokers:
            server = self._get_invoker_by_server_name(server_name)
            self._invokers[server_name] = server

        return self._invokers[server_name]

# ################################################################################################################################

    def populate_invokers(self):
        for invoker in self.config_ctx.get_remote_server_invoker_list(): # type: RemoteServerInvoker
            self._invokers[invoker.server_name] = invoker

# ################################################################################################################################

    def invoke_all(self, service, request=None, *args, **kwargs):

        # First, make sure that we are aware of all the servers currently available
        self.populate_invokers()

        # Response to produce
        out = InvokeAllResult()

        # Now, invoke all the servers ..
        for invoker in self._invokers.values(): # type: ServerInvoker

            # .. this includes responses for all the PIDs ..
            response = invoker.invoke_all_pids(service, request, *args, **kwargs)

            # .. continue if we know we can find something ..
            if response.has_data:

                # .. check all per-PID responses ..
                for pid, per_pid_response in response.data.items(): # type: (int, PerPIDResponse)

                    # .. append the response if everything went fine ..
                    if per_pid_response.is_ok:
                        out.data.append(per_pid_response.pid_data)

                    # .. otherwise, just set the overall response's success flag to false ..
                    else:
                        out.is_ok = False

        # .. now we can return the result.
        return out

# ################################################################################################################################
# ################################################################################################################################
