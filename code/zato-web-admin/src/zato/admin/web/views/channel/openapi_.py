# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from json import dumps, loads
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web.forms.channel.openapi import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.api import CONNECTION, GENERIC, generic_attrs, URL_TYPE

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def get_openapi_path_prefix():
    prefix = os.environ.get('Zato_OpenAPI_Path_Prefix', '/openapi/')
    if not prefix.endswith('/'):
        prefix = prefix + '/'
    return prefix

# ################################################################################################################################
# ################################################################################################################################

def build_openapi_spec(req, cluster_id, channel_name, rest_channel_list):
    """ Collects service info and delegates to shared OpenAPI generation.
    """
    from zato.common.util.openapi_.exporter import build_openapi_spec as _build_openapi_spec

    # Get all REST channels for this cluster
    rest_channels_response = req.zato.client.invoke('zato.http-soap.get-list', {
        'cluster_id': cluster_id,
        'connection': CONNECTION.CHANNEL,
        'transport': URL_TYPE.PLAIN_HTTP,
    })

    # Build lookup by ID
    rest_channels_by_id = {}
    rest_response_data = rest_channels_response.data
    if isinstance(rest_response_data, dict):
        rest_response_data = rest_response_data.get('response', [])
    for ch in rest_response_data:
        ch_id = str(ch['id']) if isinstance(ch, dict) else str(ch.id)
        rest_channels_by_id[ch_id] = ch

    # Collect service info for active channels
    services_info = []
    for item in rest_channel_list:
        if item['state'] == 'on':
            rest_channel_id_str = str(item['id'])
            rest_channel = rest_channels_by_id.get(rest_channel_id_str)
            if rest_channel:
                try:
                    source_info = req.zato.client.invoke('zato.service.get-source-info', {
                        'cluster_id': cluster_id,
                        'name': rest_channel.service_name,
                    })
                    source_path = None
                    if hasattr(source_info, 'data') and source_info.data:
                        source_path = source_info.data.get('source_path') if isinstance(source_info.data, dict) else getattr(source_info.data, 'source_path', None)
                    security_name = getattr(rest_channel, 'security_name', None) or getattr(rest_channel, 'sec_def', None)
                    services_info.append({
                        'name': rest_channel.service_name,
                        'url_path': rest_channel.url_path,
                        'http_method': getattr(rest_channel, 'method', 'POST') or 'POST',
                        'source_path': source_path,
                        'security_name': security_name,
                    })
                except Exception:
                    logger.warning('Could not get source info for service %s: %s', rest_channel.service_name, format_exc())
                    security_name = getattr(rest_channel, 'security_name', None) or getattr(rest_channel, 'sec_def', None)
                    services_info.append({
                        'name': rest_channel.service_name,
                        'url_path': rest_channel.url_path,
                        'http_method': getattr(rest_channel, 'method', 'POST') or 'POST',
                        'source_path': None,
                        'security_name': security_name,
                    })

    # Collect file paths for scanning
    file_paths = []
    for item in services_info:
        if item['source_path']:
            file_paths.append(item['source_path'])

    # Use shared OpenAPI generation
    return _build_openapi_spec(channel_name, services_info, file_paths)

# ################################################################################################################################
# ################################################################################################################################

class OpenAPIChannelConfigObject:
    def __init__(self):
        self._config_attrs = []
        self.id = -1
        self.name = ''
        self.is_active = True
        self.is_public = False
        self.url_path = ''
        self.rest_channel_list = []

    @property
    def rest_channel_list_json(self):
        return dumps(self.rest_channel_list or [])

    @property
    def channel_count(self):
        count = 0
        for item in (self.rest_channel_list or []):
            if item['state'] == 'on':
                count += 1
        return count

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-openapi'
    template = 'zato/channel/openapi.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = OpenAPIChannelConfigObject
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id', 'type_'
        output_required = 'id', 'name', 'is_active'
        output_optional = generic_attrs
        output_repeated = True

# ################################################################################################################################

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'openapi_path_prefix': get_openapi_path_prefix(),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'id', 'name', 'is_active', 'url_path'
        input_optional = 'is_public',
        output_required = 'id', 'name'
        output_optional = 'rest_channel_list',

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CHANNEL_OPENAPI
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outgoing'] = False
        initial_input_dict['is_outconn'] = False
        initial_input_dict['recv_timeout'] = 250
        initial_input_dict['pool_size'] = 20

# ################################################################################################################################

    def pre_process_input_dict(self, input_dict):
        if self.req.method == 'POST':
            rest_channel_list_raw = self.req.POST.getlist('rest_channel_list')
            if rest_channel_list_raw:
                rest_channel_list = []
                for item_json in rest_channel_list_raw:
                    rest_channel_list.append(loads(item_json))
                input_dict['rest_channel_list'] = rest_channel_list

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} OpenAPI channel `{}`'.format(self.verb, item.name)

# ################################################################################################################################

    def post_process_return_data(self, return_data):
        rest_channel_list_raw = self.req.POST.getlist('rest_channel_list')
        if rest_channel_list_raw:
            rest_channel_list = []
            for item_json in rest_channel_list_raw:
                rest_channel_list.append(loads(item_json))
            return_data['rest_channel_list'] = dumps(rest_channel_list)
        else:
            return_data['rest_channel_list'] = '[]'
        return return_data

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-openapi-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-openapi-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-openapi-delete'
    error_message = 'Could not delete OpenAPI channel'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def generate_openapi(req):
    cluster_id = req.GET['cluster_id']
    channel_id = req.GET['channel_id']

    try:
        channel_response = req.zato.client.invoke('zato.generic.connection.get-list', {
            'cluster_id': cluster_id,
            'type_': GENERIC.CONNECTION.TYPE.CHANNEL_OPENAPI,
        })

        channel = None
        channel_id_int = int(channel_id)
        response_data = channel_response.data
        if isinstance(response_data, dict):
            response_data = response_data.get('response', [])
        for item in response_data:
            if item['id'] == channel_id_int:
                channel = item
                break

        if not channel:
            return HttpResponseServerError(
                dumps({'error': 'OpenAPI channel not found'}),
                content_type='application/json'
            )

        channel_name = channel['name'] if isinstance(channel, dict) else channel.name

        rest_channel_list = []
        raw = channel.get('rest_channel_list') if isinstance(channel, dict) else getattr(channel, 'rest_channel_list', None)
        if raw:
            if isinstance(raw, str):
                rest_channel_list = loads(raw)
            else:
                rest_channel_list = raw

        yaml_output = build_openapi_spec(req, cluster_id, channel_name, rest_channel_list)

        logger.info('Generated OpenAPI for channel %s (%s)', channel_id, channel_name)
        response = HttpResponse(yaml_output, content_type='application/x-yaml')
        response['Content-Disposition'] = f'attachment; filename="{channel_name}.yaml"'
        return response

    except Exception:
        logger.error('generate_openapi error: %s', format_exc())
        return HttpResponseServerError(
            dumps({'error': format_exc()}),
            content_type='application/json'
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_rest_channels(req):
    cluster_id = req.GET['cluster_id']

    try:
        response = req.zato.client.invoke('zato.http-soap.get-list', {
            'cluster_id': cluster_id,
            'connection': CONNECTION.CHANNEL,
            'transport': URL_TYPE.PLAIN_HTTP,
        })

        channels_list = []
        for item in response:
            channels_list.append({
                'id': item.id,
                'name': item.name,
                'service_name': item.service_name,
                'url_path': item.url_path,
            })

        return HttpResponse(
            dumps({
                'rest_channels': channels_list
            }),
            content_type='application/json'
        )
    except Exception:
        logger.error('get_rest_channels error: %s', format_exc())
        return HttpResponseServerError(
            dumps({
                'error': format_exc()
            }),
            content_type='application/json'
        )

# ################################################################################################################################
# ################################################################################################################################
