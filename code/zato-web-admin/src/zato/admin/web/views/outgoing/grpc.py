# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from base64 import b64decode
from http import HTTPStatus
from io import BytesIO
from traceback import format_exc
from zipfile import ZipFile

# Django
from django.http import HttpResponse, JsonResponse

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.admin.web.forms.outgoing.grpc import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, ping_connection, SecurityList
from zato.common.api import GENERIC, generic_attrs, SEC_DEF_TYPE

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-grpc'
    template = 'zato/outgoing/grpc.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active', 'address'
    output_optional = ('is_tls', 'tls_ca_certs_file', 'proto_path', 'stub_module', 'stub_class', 'ping_timeout',
        'max_send_message_size', 'max_recv_message_size', 'security_id', 'security_name', 'auth_type') + generic_attrs
    output_repeated = True

# ################################################################################################################################

    def on_before_append_item(self, item):
        if item.auth_type:
            item.sec_type = item.auth_type
        return item

    def handle(self):

        security_list = SecurityList.from_service(
            self.req.zato.client,
            self.cluster_id,
            sec_type=[SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.OAUTH, SEC_DEF_TYPE.APIKEY],
            needs_def_type_name_label=True
        )

        return {
            'show_search_form': True,
            'create_form': CreateForm(self.req, security_list),
            'edit_form': EditForm(self.req, security_list, prefix='edit'),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'address', 'security_id'
    input_optional = ('is_active', 'is_tls', 'tls_ca_certs_file', 'proto_path', 'stub_module', 'stub_class', 'ping_timeout',
        'max_send_message_size', 'max_recv_message_size') + generic_attrs
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_GRPC
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outgoing'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['pool_size'] = 1

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} gRPC outgoing connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-grpc-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-grpc-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-grpc-delete'
    error_message = 'Could not delete gRPC outgoing connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'gRPC connection')

# ################################################################################################################################

@method_allowed('POST')
def invoke(req, id):
    try:
        params = {
            'id': id,
            'method': req.POST.get('method', ''),
            'request_data': req.POST.get('data-request', ''),
        }
        response = req.zato.client.invoke('zato.generic.connection.invoke-grpc', params)
        if response.ok:
            return JsonResponse({
                'data': response.data.response_data,
                'response_time_human': response.data.response_time,
                'content_type': 'application/json',
            })
        return JsonResponse({'data': str(response.details), 'response_time_human': '', 'content_type': 'text/plain'},
            status=HTTPStatus.INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error('invoke error: %s', format_exc())
        return JsonResponse({'data': str(e), 'response_time_human': '', 'content_type': 'text/plain'},
            status=HTTPStatus.INTERNAL_SERVER_ERROR)

# ################################################################################################################################

@method_allowed('GET')
def download_stubs(req, id):
    """ Returns a zip archive with the Python modules generated out of the connection's .proto file.
    """
    try:
        response = req.zato.client.invoke('zato.outgoing.grpc.get-stub-modules', {'id': id})
        if not response.ok:
            return HttpResponse(str(response.details), status=HTTPStatus.BAD_REQUEST, content_type='text/plain')

        # Build the archive in memory out of the modules the service returned ..
        archive = BytesIO()

        with ZipFile(archive, 'w') as zip_file:
            for item in response.data.files:
                data = b64decode(item['data'])
                zip_file.writestr(item['name'], data)

        # .. and let the caller download it.
        out = HttpResponse(archive.getvalue(), content_type='application/zip')
        out['Content-Disposition'] = 'attachment; filename="grpc-stubs.zip"'
        return out

    except Exception as e:
        logger.error('download stubs error: %s', format_exc())
        return HttpResponse(str(e), status=HTTPStatus.INTERNAL_SERVER_ERROR, content_type='text/plain')

# ################################################################################################################################
