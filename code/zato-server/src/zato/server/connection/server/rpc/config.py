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
from zato.common.odb.model import SecurityBase as SecurityBaseModel, Server as ServerModel
from zato.common.odb.query import server_by_name, server_list

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.odb.api import SessionWrapper
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
    username: str = None
    password: str = None

# ################################################################################################################################
# ################################################################################################################################

class ConfigSource:
    """ A base class for returning server configuration.
    """
    def __init__(self, cluster_name, server_name):
        # type: (str, str) -> None
        self.current_cluster_name = cluster_name
        self.current_server_name = server_name

    def get_remote_server_invocation_ctx(self, cluster_name, server_name):
        # type: (str, str) -> RemoteServerInvocationCtx
        raise NotImplementedError('Should be overridden by subclasses')

# ################################################################################################################################
# ################################################################################################################################

class ODBConfigSource(ConfigSource):
    """ Returns server configuration based on information in the cluster's ODB.
    """
    def __init__(self, odb, cluster_name, server_name):
        # type: (SessionWrapper, str, str) -> None
        super().__init__(cluster_name, server_name)
        self.odb = odb

# ################################################################################################################################

    def _get_invoke_sec_def(self, session, cluster_name):
        for sec_item in self.odb.get_basic_auth_list(None, cluster_name):
            if sec_item.name == CredentialsConfig.sec_def_name:
                return sec_item
        else:
            raise ValueError('No such security definition `{}` in cluster `{}`'.format(
                CredentialsConfig.sec_def_name, cluster_name))

# ################################################################################################################################

    def get_remote_server_invocation_ctx(self, cluster_name, server_name):
        """ Returns a specific server defined in ODB.
        """
        # type: (str, str) -> RemoteServerInvocationCtx

        out = RemoteServerInvocationCtx()
        out.cluster_name = cluster_name
        out.server_name = server_name

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
            invoke_sec_def = self._get_invoke_sec_def(session, cluster_name) # type: SecurityBaseModel

            out.address = server_model.preferred_address
            out.username = invoke_sec_def.username
            out.password = invoke_sec_def.password

        return out

# ################################################################################################################################
# ################################################################################################################################

