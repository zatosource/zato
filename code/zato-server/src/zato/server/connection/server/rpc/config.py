# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from logging import getLogger

# Zato
from zato.common.ext.dataclasses import dataclass
from zato.common.odb.model import SecurityBase as SecurityBaseModel
from zato.common.odb.query import server_by_name, server_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Callable
    from zato.common.odb.api import SessionWrapper
    from zato.common.odb.model import Server as ServerModel
    from zato.server.base.parallel import ParallelServer

    ParallelServer = ParallelServer
    SessionWrapper = SessionWrapper

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class CredentialsConfig:
    sec_def_name = 'zato.internal.invoke'
    api_user = 'zato.internal.invoke.user'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RemoteServerInvocationCtx:
    cluster_name: str = None
    server_name:  str = None
    address:  str = None
    port: int = None
    crypto_use_tls: bool
    username: str = None
    password: str = None
    needs_ping: bool = True

@dataclass(init=False)
class InvocationCredentials:
    username: str = None
    password: str = None

# ################################################################################################################################
# ################################################################################################################################

class ConfigSource:
    """ A base class for returning server configuration.
    """
    def __init__(self, cluster_name, server_name, decrypt_func):
        # type: (str, str, Callable) -> None
        self.current_cluster_name = cluster_name
        self.current_server_name = server_name
        self.decrypt_func = decrypt_func

    def get_server_ctx(self, parallel_server, cluster_name, server_name):
        # type: (ParallelServer, str, str) -> RemoteServerInvocationCtx
        raise NotImplementedError('Should be overridden by subclasses')

    def get_server_ctx_list(self, cluster_name):
        # type: (str) -> list[RemoteServerInvocationCtx]
        raise NotImplementedError('Should be overridden by subclasses')

    def get_invocation_credentials(self, cluster_name):
        # type: (str) -> InvocationCredentials
        raise NotImplementedError('Should be overridden by subclasses')

# ################################################################################################################################
# ################################################################################################################################

class ODBConfigSource(ConfigSource):
    """ Returns server configuration based on information in the cluster's ODB.
    """
    def __init__(self, odb, cluster_name, server_name, decrypt_func):
        # type: (SessionWrapper, str, str, Callable) -> None
        super().__init__(cluster_name, server_name, decrypt_func)
        self.odb = odb

# ################################################################################################################################

    def get_invocation_credentials(self, session, cluster_name):
        for sec_item in self.odb.get_basic_auth_list(None, cluster_name): # type: SecurityBaseModel
            if sec_item.name == CredentialsConfig.sec_def_name:
                out = InvocationCredentials()
                out.username = sec_item.username
                out.password = self.decrypt_func(sec_item.password)
                return out
        else:
            raise ValueError('No such security definition `{}` in cluster `{}`'.format(
                CredentialsConfig.sec_def_name, cluster_name))

# ################################################################################################################################

    def build_server_ctx(self, server_model, credentials):
        # type: (ServerModel, InvocationCredentials) -> RemoteServerInvocationCtx

        out = RemoteServerInvocationCtx()
        out.cluster_name = server_model.cluster_name
        out.server_name = server_model.name
        out.address = server_model.preferred_address
        out.crypto_use_tls = server_model.crypto_use_tls
        out.port = server_model.bind_port

        out.username = credentials.username
        out.password = credentials.password

        return out

# ################################################################################################################################

    def get_server_ctx(self, _ignored_parallel_server, cluster_name, server_name):
        """ Returns a specific server defined in ODB.
        """
        # type: (ParallelServer, str, str) -> RemoteServerInvocationCtx

        with closing(self.odb.session()) as session:
            result = server_by_name(session, None, cluster_name, server_name)

        if not result:
            msg = 'No such server or cluster {}@{}'.format(server_name, cluster_name)
            logger.warn(msg)
            raise ValueError(msg)

        # Multiple matches - naturally, should not happen
        elif len(result) > 1:
            msg = 'Unexpected output for {}@{} len:`{}`, result:`{}`'.format(
                server_name, cluster_name, len(result), '\n' + '\n'.join(str(elem) for elem in result))
            logger.warn(msg)
            raise ValueError(msg)

        else:
            server_model = result[0] # type: ServerModel
            credentials = self.get_invocation_credentials(session, cluster_name) # type: SecurityBaseModel

            return self.build_server_ctx(server_model, credentials)

# ################################################################################################################################

    def get_server_ctx_list(self, cluster_name):
        # type: (str) -> list[RemoteServerInvocationCtx]

        # Response to return
        out = []

        with closing(self.odb.session()) as session:

            # First, get API credentials that will be the same for all servers ..
            credentials = self.get_invocation_credentials(session, cluster_name)

            # .. now, get servers from the database ..
            result = server_list(session, None, cluster_name)
            result = result[0]
            result = result.result

        # .. combine the two ..

        for item in result:
            server_ctx = self.build_server_ctx(item, credentials)
            out.append(server_ctx)

        # .. and return everything to our caller.
        return out

# ################################################################################################################################
# ################################################################################################################################
