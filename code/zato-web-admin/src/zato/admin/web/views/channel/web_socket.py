# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.channel.web_socket import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common import ZATO_NONE
from zato.common.odb.model import ChannelWebSocket
from zato.common.util.json_ import dumps

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class WSXConnection(object):
    def __init__(self):
        self.id = None
        self.local_address = None
        self.peer_address = None
        self.peer_fqdn = None
        self.pub_client_id = None
        self.ext_client_id = None
        self.connection_time = None
        self.connection_time_utc = None
        self.server_name = None
        self.server_proc_pid = None
        self.ext_client_name = None
        self.sub_count = 0

# ################################################################################################################################

class WSXSubKeyData(object):
    def __init__(self):
        self.sub_key = None
        self.creation_time = None
        self.topic_id = None
        self.topic_name = None

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-web-socket'
    template = 'zato/channel/web-socket.html'
    service_name = 'zato.channel.web-socket.get-list'
    output_class = ChannelWebSocket
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'address', 'service_name', 'token_format', 'data_format',
            'security_id', 'sec_type', 'new_token_wait_time', 'token_ttl')
        output_repeated = True

    def on_before_append_item(self, item):
        if item.security_id:
            item.security_id = '{}/{}'.format(item.sec_type, item.security_id)
        else:
            item.security_id = ZATO_NONE
        return item

    def handle(self):
        if self.req.zato.cluster_id:
            sec_list = self.get_sec_def_list('basic_auth').def_items
            sec_list.extend(self.get_sec_def_list('jwt'))
            sec_list.extend(self.get_sec_def_list('vault_conn_sec'))
        else:
            sec_list = []

        return {
            'create_form': CreateForm(sec_list, req=self.req),
            'edit_form': EditForm(sec_list, prefix='edit', req=self.req),
        }

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'address', 'service_name', 'token_format', 'data_format', 'is_internal',
            'security_id', 'new_token_wait_time', 'token_ttl')
        output_required = ('id', 'name')

    def on_after_set_input(self):
        if self.input.security_id != ZATO_NONE:
            self.input.security_id = int(self.input.security_id.split('/')[1])
        else:
            self.input.security_id = None

    def success_message(self, item):
        return 'WebSocket channel `{}` successfully {}'.format(item.name, self.verb)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-web-socket-create'
    service_name = 'zato.channel.web-socket.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-web-socket-edit'
    form_prefix = 'edit-'
    service_name = 'zato.channel.web-socket.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-web-socket-delete'
    error_message = 'Could not delete WebSocket channel'
    service_name = 'zato.channel.web-socket.delete'

# ################################################################################################################################

class ConnectionList(_Index):
    method_allowed = 'GET'
    url_name = 'channel-web-socket-connection-list'
    template = 'zato/channel/web-socket-connection-list.html'
    service_name = 'zato.channel.web-socket.get-connection-list'
    output_class = WSXConnection
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'id', 'channel_name')
        output_required = ('local_address', 'peer_address', 'peer_fqdn', 'pub_client_id', 'ext_client_id', 'connection_time',
            'server_name', 'server_proc_pid', 'peer_forwarded_for', 'peer_forwarded_for_fqdn')
        output_optional = 'ext_client_name', 'sub_count'
        output_repeated = True

    def handle(self):
        return {
            'conn_id': self.input.id,
            'channel_id': self.input.id,
            'channel_name': self.input.channel_name
        }

    def on_before_append_item(self, item):
        item.id = item.pub_client_id.replace('.', '-')
        item.connection_time_utc = item.connection_time
        item.connection_time = from_utc_to_user(item.connection_time_utc + '+00:00', self.req.zato.user_profile)

        if item.ext_client_name:
            item.ext_client_name = [elem.strip() for elem in item.ext_client_name.split(';')]
            item.ext_client_name = '\n'.join(item.ext_client_name)

        return item

# ################################################################################################################################

class DisconnectionConnection(_Delete):
    url_name = 'channel-web-socket-connection-disconnect'
    error_message = 'Could not disconnect WebSocket connection'
    service_name = 'zato.channel.web-socket.disconnect-connection'

    def get_input_dict(self):
        out = super(DisconnectionConnection, self).get_input_dict()
        out['pub_client_id'] = self.req.zato.args.pub_client_id.replace('-', '.')
        return out

# ################################################################################################################################

class SubKeyDataList(_Index):
    method_allowed = 'GET'
    url_name = 'channel-web-socket-connection-sub-key-data-list'
    template = 'zato/channel/web-socket-connection-sub-key-data-list.html'
    service_name = 'zato.channel.web-socket.get-sub-key-data-list'
    output_class = WSXSubKeyData
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'pub_client_id', 'channel_name')
        input_optional = ('conn_id',)
        output_required = ('sub_id', 'sub_key', 'creation_time', 'topic_id', 'topic_name', 'sub_pattern_matched',
            'ext_client_id', 'endpoint_id', 'endpoint_name')
        output_repeated = True

    def on_after_set_input(self):
        self.input['pub_client_id'] = self.input['pub_client_id'].replace('-', '.')

    def handle(self):
        return {
            'conn_id': self.input.conn_id,
            'pub_client_id': self.input.pub_client_id,
            'pub_client_id_html': self.input.pub_client_id.replace('.', '-'),
            'channel_name': self.input.channel_name,
        }

    def on_before_append_item(self, item):
        item.id = item.sub_key.replace('.', '_')
        item.creation_time_utc = item.creation_time
        item.creation_time = from_utc_to_user(item.creation_time_utc + '+00:00', self.req.zato.user_profile)
        return item

# ################################################################################################################################

@method_allowed('GET')
def invoke(req, conn_id, pub_client_id, ext_client_id, ext_client_name, channel_id, channel_name):

    return_data = {
        'conn_id': conn_id,
        'pub_client_id': pub_client_id,
        'pub_client_id_html': pub_client_id.replace('.', '-'),
        'ext_client_id': ext_client_id,
        'ext_client_name': ext_client_name,
        'channel_id': channel_id,
        'channel_name': channel_name,
        'cluster_id': req.zato.cluster_id,
    }

    return TemplateResponse(req, 'zato/channel/web-socket-invoke.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def invoke_action(req, pub_client_id, send_attrs=('id', 'pub_client_id', 'request_data', 'timeout')):

    try:
        request = {
            'cluster_id': req.zato.cluster_id
        }

        for name in send_attrs:
            request[name] = req.POST.get(name, '')

        response = req.zato.client.invoke('zato.channel.web-socket.invoke-wsx', request)

        if response.ok:
            response_data = response.data['response_data']
            if isinstance(response_data, dict):
                response_data = dict(response_data)
            return HttpResponse(dumps(response_data), content_type='application/javascript')
        else:
            raise Exception(response.details)
    except Exception:
        msg = 'Caught an exception, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
