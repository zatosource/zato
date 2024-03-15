# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.cloud.salesforce import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, invoke_action_handler, method_allowed, \
    ping_connection
from zato.common.api import GENERIC, generic_attrs
from zato.common.model.salesforce import SalesforceConfigObject

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'cloud-salesforce'
    template = 'zato/cloud/salesforce/index.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = SalesforceConfigObject
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id', 'type_'
        output_required = 'id', 'name', 'is_active', 'is_internal', 'address', 'username', 'api_version', \
            'password', 'consumer_key', 'consumer_secret'
        output_optional = generic_attrs
        output_repeated = True

# ################################################################################################################################

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'name', 'is_internal', 'address', 'username', 'api_version', \
            'password', 'consumer_key', 'consumer_secret'
        input_optional = ('is_active', 'pool_size') + generic_attrs
        output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outgoing'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['recv_timeout'] = 250
        initial_input_dict['pool_size'] = 20

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} Salesforce cloud connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'cloud-salesforce-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'cloud-salesforce-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'cloud-salesforce-delete'
    error_message = 'Could not delete Salesforce connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def invoke(req, conn_id, max_wait_time, conn_name, conn_slug):

    return_data = {
        'conn_id': conn_id,
        'conn_name': conn_name,
        'conn_slug': conn_slug,
        'conn_type': GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE,
        'timeout': max_wait_time,
        'cluster_id': req.zato.cluster_id,
    }

    return TemplateResponse(req, 'zato/cloud/salesforce/invoke.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def invoke_action(req, conn_name):
    return invoke_action_handler(req, 'zato.generic.connection.invoke', ('conn_name', 'conn_type', 'request_data', 'timeout'))

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'Salesforce connection')

# ################################################################################################################################
