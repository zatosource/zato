# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from json import dumps, loads

# Zato
from zato.client import AnyServiceInvoker
from zato.common import INFO_FORMAT, SERVER_JOIN_STATUS, SERVER_UP_STATUS
from zato.common.broker_message import SERVER_STATUS
from zato.common.odb.query import server_list
from zato.common.component_info import format_info, get_info, get_worker_pids
from zato.server.service import List, Service

# ################################################################################################################################

class GetInfo(Service):
    """ Like 'zato info' on command line but works across the whole cluster rather than with a single server.
    """
    def handle(self):

        # Let's prepare as much as we can upfront.
        sec_def = self.worker_store.basic_auth_get('admin.invoke').config
        channel = self.worker_store.get_channel_plain_http('admin.invoke.json')
        out = {}

        with closing(self.odb.session()) as session:
            for item in server_list(session, self.server.cluster_id, None, None, False):
                server_info = out.setdefault(item.name, {})
                server_info['cluster_name'] = item.cluster_name

                server_info['up_mod_date'] = item.up_mod_date.isoformat() if item.up_status == SERVER_UP_STATUS.RUNNING else None
                server_info['last_join_mod_date'] = item.last_join_mod_date.isoformat() if \
                    item.last_join_status == SERVER_JOIN_STATUS.ACCEPTED else None

                for name in 'id', 'name', 'bind_host', 'bind_port', 'last_join_status', 'last_join_mod_by', 'up_status':
                    server_info[name] = getattr(item, name)

                if item.up_status == SERVER_UP_STATUS.RUNNING:

                    client = AnyServiceInvoker(
                        'http://{}:{}'.format(item.bind_host, item.bind_port),
                        channel.url_path, (sec_def.username, sec_def.password))
                    response = client.invoke('zato.info.get-server-info')
                    if response.ok:
                        response = loads(response.inner.text)['zato_service_invoke_response']['response'].decode('base64')
                        response = loads(response)['response']
                        server_info['info'] = loads(response['info'])
                    else:
                        self.logger.warn(response)

        self.response.content_type = 'application/json'
        self.response.payload = dumps(out)

# ################################################################################################################################

class GetServerInfo(Service):
    """ Collects information about a server it's invoked on.
    """
    class SimpleIO(object):
        output_required = ('info',)

    def handle(self):
        self.response.content_type = 'application/json'
        self.response.payload.info = format_info(get_info(self.server.base_dir, INFO_FORMAT.JSON), INFO_FORMAT.JSON)

# ################################################################################################################################

class GetWorkerPids(Service):
    """ Returns PIDs of all workers of current server.
    """
    class SimpleIO(object):
        output_required = (List('pids'),)

    def handle(self):
        self.response.payload.pids = get_worker_pids(self.server.base_dir)

# ################################################################################################################################

class SetServerUpStatus(Service):
    """ Notifies all worker processes that current one has just started.
    """
    def handle(self):
        self.broker_client.publish({
            'action': SERVER_STATUS.STATUS_CHANGED.value,
            'status': SERVER_UP_STATUS.RUNNING,
        })

# ################################################################################################################################
