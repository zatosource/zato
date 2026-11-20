# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from importlib import import_module

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    from zato.server.base.config_manager import ConfigManager
    from zato.server.connection.grpc_ import GRPCInvoker

# ################################################################################################################################
# ################################################################################################################################

# The module of the invokers, which imports grpc and protobuf, and which the wrapper of each connection has imported already
_grpc_module = 'zato.server.connection.grpc_'

# ################################################################################################################################
# ################################################################################################################################

class GRPCFacade:
    """ Provides dict-like access to gRPC outgoing connections from services via self.grpc.
    """
    cid: 'str'
    _outconn_grpc: 'anydict'

    def init(self, cid:'str', config_manager:'ConfigManager') -> 'None':
        self.cid = cid
        self._outconn_grpc = config_manager.outconn_grpc

# ################################################################################################################################

    def __getitem__(self, name:'str') -> 'GRPCInvoker':

        # This will raise a KeyError if there is no such connection
        item = self._outconn_grpc[name]

        # The wrapper holds the underlying channel and stub
        wrapper = item['conn']

        grpc_module = import_module(_grpc_module)

        out = grpc_module.GRPCInvoker(wrapper, self.cid)
        return out

# ################################################################################################################################
# ################################################################################################################################
