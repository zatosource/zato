# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from json import dumps

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
