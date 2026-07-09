# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.http import HttpResponseServerError, JsonResponse

# Zato
from zato.admin.web.forms.outgoing.soap import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, extract_security_id, id_only_service, Index as _Index, \
    method_allowed
from zato.common.api import CONNECTION, SEC_DEF_TYPE_NAME, URL_TYPE, ZATO_NONE

# ################################################################################################################################
# ################################################################################################################################

class OutgoingSOAPConfigObject:
    """ A config object for outgoing SOAP connections, filled in with attributes from the get-list response.
    """

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-soap'
    template = 'zato/outgoing/soap.html'
    service_name = 'zato.http-soap.get-list'
    output_class = OutgoingSOAPConfigObject
    paginate = True

    def get_initial_input(self):

        return {
            'connection': CONNECTION.OUTGOING,
            'transport': URL_TYPE.SOAP,
        }

    input_required = 'cluster_id',
    output_required = 'id', 'name', 'is_active', 'is_internal'
    output_optional = 'host', 'url_path', 'soap_action', 'soap_version', 'security_id', 'security_name', 'sec_type', \
        'sec_type_name', 'validate_tls', 'ping_method', 'timeout', 'content_type', 'serialization_type', \
        'use_ws_addressing', 'use_mtom', 'body_credentials', 'tls_client_cert', 'tls_client_key'
    output_repeated = True

# ################################################################################################################################

    def on_before_append_item(self, item):

        # Connections without security never had the attribute set at all.
        security_id = getattr(item, 'security_id', None)

        if security_id and security_id != ZATO_NONE:
            item.sec_type_name = SEC_DEF_TYPE_NAME[item.sec_type]

        return item

# ################################################################################################################################

    def handle(self):
        security_list = self.get_sec_def_list(None)
        return {
            'show_search_form': True,
            'create_form': CreateForm(security_list, req=self.req),
            'edit_form': EditForm(security_list, prefix='edit', req=self.req),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'host'
    input_optional = 'is_active', 'url_path', 'soap_action', 'soap_version', 'security_id', 'validate_tls', \
        'ping_method', 'timeout', 'content_type', 'serialization_type', \
        'use_ws_addressing', 'use_mtom', 'body_credentials', 'tls_client_cert', 'tls_client_key'
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['connection'] = CONNECTION.OUTGOING
        initial_input_dict['transport'] = URL_TYPE.SOAP
        initial_input_dict['is_internal'] = False

# ################################################################################################################################

    def pre_process_input_dict(self, input_dict):
        input_dict['security_id'] = extract_security_id(input_dict)

        if not input_dict.get('url_path'):
            input_dict['url_path'] = '/'

        # Checkboxes arrive as 'on' or not at all - the backend expects real booleans.
        for name in ('use_ws_addressing', 'use_mtom'):
            input_dict[name] = bool(input_dict.get(name))

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} outgoing SOAP connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-soap-create'
    service_name = 'zato.http-soap.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-soap-edit'
    form_prefix = 'edit-'
    service_name = 'zato.http-soap.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-soap-delete'
    error_message = 'Could not delete outgoing SOAP connection'
    service_name = 'zato.http-soap.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id): # type: ignore
    response = id_only_service(req, 'zato.http-soap.ping', id, 'Could not ping the connection, e:`{}`')

    if isinstance(response, HttpResponseServerError):
        err = response.content.decode('utf-8', 'replace')
        return JsonResponse({
            'is_success': False,
            'info': err,
        })

    data = response.data
    return JsonResponse({
        'is_success': data.is_success,
        'info': data.info,
    })

# ################################################################################################################################
# ################################################################################################################################
