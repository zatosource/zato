# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from json import dumps, loads

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

class OpenAPIChannelConfigObject:
    def __init__(self):
        self._config_attrs = []
        self.id = -1
        self.name = ''
        self.is_active = True
        self.url_path = ''
        self.rest_channel_list = []

    @property
    def rest_channel_list_json(self):
        return dumps(self.rest_channel_list or [])

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
        output_required = 'id', 'name'

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
    cluster_id = req.GET.get('cluster_id')
    channel_id = req.GET.get('channel_id')

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

        rest_channel_list = []
        raw = channel.get('rest_channel_list') if isinstance(channel, dict) else getattr(channel, 'rest_channel_list', None)
        if raw:
            if isinstance(raw, str):
                rest_channel_list = loads(raw)
            else:
                rest_channel_list = raw

        rest_channels_response = req.zato.client.invoke('zato.http-soap.get-list', {
            'cluster_id': cluster_id,
            'connection': CONNECTION.CHANNEL,
            'transport': URL_TYPE.PLAIN_HTTP,
        })

        rest_channels_by_id = {}
        rest_response_data = rest_channels_response.data
        if isinstance(rest_response_data, dict):
            rest_response_data = rest_response_data.get('response', [])
        for ch in rest_response_data:
            ch_id = str(ch['id']) if isinstance(ch, dict) else str(ch.id)
            rest_channels_by_id[ch_id] = ch

        services_info = []
        for item in rest_channel_list:
            if item.get('state') in ('on', 'disabled'):
                rest_channel_id_str = str(item.get('id'))
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
                        services_info.append({
                            'name': rest_channel.service_name,
                            'url_path': rest_channel.url_path,
                            'http_method': getattr(rest_channel, 'method', 'POST') or 'POST',
                            'source_path': source_path,
                        })
                    except Exception as e:
                        logger.warning('Could not get source info for service %s: %s', rest_channel.service_name, e)
                        services_info.append({
                            'name': rest_channel.service_name,
                            'url_path': rest_channel.url_path,
                            'http_method': getattr(rest_channel, 'method', 'POST') or 'POST',
                            'source_path': None,
                        })

        file_paths = [s['source_path'] for s in services_info if s.get('source_path')]

        from zato.openapi.generator.io_scanner import IOScanner
        from zato.openapi.generator.openapi_ import OpenAPIGenerator
        import yaml

        scanner = IOScanner()
        scan_results = scanner.scan_files(file_paths) if file_paths else {'services': [], 'models': {}}

        schema_by_service = {}
        for service in scan_results['services']:
            service_name = service.get('name')
            if service_name:
                schema_by_service[service_name] = {
                    'input': service.get('input'),
                    'output': service.get('output'),
                    'class_name': service.get('class_name')
                }

        for service in services_info:
            schema = schema_by_service.get(service['name'])
            if schema:
                service.update(schema)

        openapi_spec = {
            'openapi': '3.1.0',
            'info': {
                'title': channel.name if hasattr(channel, 'name') else 'API',
                'version': '1.0.0'
            },
            'paths': {},
            'components': {'schemas': {}}
        }

        openapi_generator = OpenAPIGenerator(type_mapper=scanner.type_mapper)

        for service in services_info:
            path = service.get('url_path', f'/{service["name"].replace(".", "/")}')
            method = service.get('http_method', 'post').lower()

            operation = {
                'summary': f'Invoke {service["name"]}',
                'operationId': service['name'].replace('.', '_').replace('-', '_'),
                'responses': {
                    '200': {'description': 'Successful response'},
                    '400': {'description': 'Bad Request'},
                    '500': {'description': 'Internal Server Error'}
                }
            }

            if service.get('input'):
                try:
                    request_schema = openapi_generator._create_request_schema(service['input'], scan_results['models'])
                    if request_schema:
                        input_def = service['input']
                        is_required = True
                        if input_def.get('type') == 'string':
                            is_required = input_def.get('required', True)
                        elif input_def.get('type') == 'tuple':
                            is_required = any(el.get('required', True) for el in input_def.get('elements', []))
                        operation['requestBody'] = {
                            'required': is_required,
                            'content': {'application/json': {'schema': request_schema}}
                        }
                except Exception as e:
                    logger.warning('Could not create request schema for %s: %s', service['name'], e)

            if service.get('output'):
                try:
                    response_schema = openapi_generator._create_response_schema(service['output'], scan_results['models'])
                    if response_schema:
                        operation['responses']['200']['content'] = {
                            'application/json': {'schema': response_schema}
                        }
                except Exception as e:
                    logger.warning('Could not create response schema for %s: %s', service['name'], e)

            if path not in openapi_spec['paths']:
                openapi_spec['paths'][path] = {}
            openapi_spec['paths'][path][method] = operation

        schema_components = openapi_generator.type_mapper.get_schema_components()
        if schema_components:
            openapi_spec['components']['schemas'].update(schema_components)

        yaml_output = yaml.dump(openapi_spec, sort_keys=False, allow_unicode=True)

        response = HttpResponse(yaml_output, content_type='application/x-yaml')
        response['Content-Disposition'] = f'attachment; filename="{channel.name if hasattr(channel, "name") else "openapi"}.yaml"'
        return response

    except Exception as e:
        logger.error('generate_openapi error: %s', e, exc_info=True)
        return HttpResponseServerError(
            dumps({'error': str(e) or 'Error generating OpenAPI spec'}),
            content_type='application/json'
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def get_rest_channels(req):
    cluster_id = req.GET.get('cluster_id')

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
    except Exception as e:
        logger.error('get_rest_channels error: %s', e)
        return HttpResponseServerError(
            dumps({
                'error': str(e) or 'Error retrieving REST channels'
            }),
            content_type='application/json'
        )

# ################################################################################################################################
# ################################################################################################################################
