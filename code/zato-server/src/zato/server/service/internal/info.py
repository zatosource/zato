# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode
from contextlib import closing

# Zato
from zato.client import AnyServiceInvoker
from zato.common.api import INFO_FORMAT, MISC, SERVER_JOIN_STATUS, SERVER_UP_STATUS
from zato.common.component_info import format_info, get_info, get_worker_pids
from zato.common.const import ServiceConst
from zato.common.json_internal import dumps, loads
from zato.common.odb.query import server_list
from zato.common.util.config import get_url_protocol_from_config_item
from zato.server.service import List, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class GetInfo(Service):
    """ Like 'zato info' on command line but works across the whole cluster rather than with a single server.
    """
    def handle(self):

        # Let's prepare as much as we can upfront.
        sec_def:'any_' = self.server.worker_store.basic_auth_get(ServiceConst.API_Admin_Invoke_Username).config
        channel:'any_' = self.server.worker_store.get_channel_rest(MISC.DefaultAdminInvokeChannel)
        out = {}

        # We assume that if the current server uses TLS or not,
        # the same will go for all the other servers in the cluster.
        api_protocol = get_url_protocol_from_config_item(self.server.fs_server_config.crypto.use_tls)

        with closing(self.odb.session()) as session:
            _server_list = server_list(session, self.server.cluster_id, None, None, False) # type: ignore

            for item in _server_list:
                server_info:'any_' = out.setdefault(item.name, {})
                server_info['cluster_name'] = item.cluster_name

                server_info['up_mod_date'] = item.up_mod_date.isoformat() if item.up_status == SERVER_UP_STATUS.RUNNING else None
                server_info['last_join_mod_date'] = item.last_join_mod_date.isoformat() if \
                    item.last_join_status == SERVER_JOIN_STATUS.ACCEPTED else None

                for name in 'id', 'name', 'bind_host', 'bind_port', 'last_join_status', 'last_join_mod_by', 'up_status':
                    server_info[name] = getattr(item, name)

                if item.up_status == SERVER_UP_STATUS.RUNNING:

                    address = f'{api_protocol}://{item.bind_host}:{item.bind_port}'
                    auth = (sec_def.username, sec_def.password) # type: ignore

                    client = AnyServiceInvoker(address, channel.url_path, auth=auth)

                    response = client.invoke('zato.info.get-server-info')
                    if response.ok:
                        response = loads(response.inner.text)['zato_service_invoke_response']['response']
                        response = b64decode(response)
                        response = loads(response)['response']
                        server_info['info'] = loads(response['info'])
                    else:
                        self.logger.warning(response)

        self.response.content_type = 'application/json'
        self.response.payload = dumps(out)

# ################################################################################################################################

class GetServerInfo(Service):
    """ Collects information about a server it's invoked on.
    """
    class SimpleIO:
        output_required = ('info',)

    def handle(self):
        self.response.content_type = 'application/json'
        self.response.payload.info = format_info(get_info(self.server.base_dir, INFO_FORMAT.JSON), INFO_FORMAT.JSON)

# ################################################################################################################################

class GetWorkerPids(Service):
    """ Returns PIDs of all processes of current server.
    """
    output:'any_' = List('pids')

    def handle(self):
        self.response.payload.pids = get_worker_pids(self.server.base_dir)

# ################################################################################################################################
