# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http import HTTPStatus
from logging import getLogger
from socket import AF_INET, SOCK_STREAM, socket as socket_
from time import time
from traceback import format_exc
from urllib.parse import urlparse

# Django
from django.http import HttpResponse, JsonResponse

# Zato
from zato.admin.web.forms.channel.hl7.mllp import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, \
    get_security_id_from_select, get_security_groups_from_checkbox_list
from zato.common.api import GENERIC, generic_attrs, HL7, SEC_DEF_TYPE
from zato.common.model.hl7 import HL7MLLPConfigObject

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# .. name prefix for backing REST channels ..
_REST_Channel_Name_Prefix = 'hl7.rest.'

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-hl7-mllp'
    template = 'zato/channel/hl7/mllp.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = HL7MLLPConfigObject
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active', 'is_internal', 'service', 'security_name'
    output_optional = (
        'should_parse_on_input', 'should_validate', 'should_return_errors',
        'should_log_messages', 'logging_level',
        'max_msg_size', 'max_msg_size_unit', 'read_buffer_size', 'recv_timeout',
        'start_seq', 'end_seq',
        'msh3_sending_app', 'msh4_sending_facility',
        'msh5_receiving_app', 'msh6_receiving_facility', 'msh9_message_type',
        'msh9_trigger_event', 'msh11_processing_id', 'msh12_version_id', 'is_default',
        'dedup_ttl_value', 'dedup_ttl_unit',
        'default_character_encoding',
        'normalize_line_endings', 'force_standard_delimiters',
        'repair_truncated_msh', 'split_concatenated_messages', 'use_msh18_encoding',
        'normalize_obx2_value_type', 'replace_invalid_obx2_value_type',
        'normalize_invalid_escape_sequences', 'normalize_obx8_abnormal_flags',
        'normalize_quadruple_quoted_empty', 'allow_short_encoding_characters',
        'fix_off_by_one_field_index',
        'use_rest', 'rest_only', 'rest_channel_id',
    ) + generic_attrs
    output_repeated = True

# ################################################################################################################################

    def handle(self):
        security_list = self.get_sec_def_list(SEC_DEF_TYPE.BASIC_AUTH)
        return {
            'show_search_form': True,
            'create_form': CreateForm(req=self.req, security_list=security_list),
            'edit_form': EditForm(prefix='edit', req=self.req, security_list=security_list),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'is_internal', 'service'
    input_optional = (
        'is_active', 'should_parse_on_input', 'should_validate', 'should_return_errors',
        'should_log_messages', 'logging_level',
        'max_msg_size', 'max_msg_size_unit', 'read_buffer_size', 'recv_timeout',
        'start_seq', 'end_seq',
        'msh3_sending_app', 'msh4_sending_facility',
        'msh5_receiving_app', 'msh6_receiving_facility', 'msh9_message_type',
        'msh9_trigger_event', 'msh11_processing_id', 'msh12_version_id', 'is_default',
        'dedup_ttl_value', 'dedup_ttl_unit',
        'default_character_encoding',
        'normalize_line_endings', 'force_standard_delimiters',
        'repair_truncated_msh', 'split_concatenated_messages', 'use_msh18_encoding',
        'normalize_obx2_value_type', 'replace_invalid_obx2_value_type',
        'normalize_invalid_escape_sequences', 'normalize_obx8_abnormal_flags',
        'normalize_quadruple_quoted_empty', 'allow_short_encoding_characters',
        'fix_off_by_one_field_index',
        'use_rest', 'rest_only', 'rest_channel_id', 'rest_url_path', 'rest_security_id',
    ) + generic_attrs
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['pool_size'] = 1
        initial_input_dict['should_validate'] = True
        initial_input_dict['should_parse_on_input'] = True
        initial_input_dict['data_format'] = HL7.Const.Version.v2.id
        initial_input_dict['hl7_version'] = HL7.Const.Version.v2.id

# ################################################################################################################################

    def pre_process_item(self, name, value):
        if name == 'recv_timeout':
            return int(value)
        else:
            return value

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} HL7 MLLP channel `{}`'.format(self.verb, item.name)

# ################################################################################################################################

    def _build_rest_channel_message(self, mllp_name:'str') -> 'dict':
        """ Builds the input dict for zato.http-soap.create or edit,
        .. reading REST-specific fields from POST data.
        """

        # .. extract security ID from the select widget ..
        security_id = get_security_id_from_select(
            self.req.POST, self.form_prefix or '', field_name='rest_security_id')

        # .. extract security groups from the checkbox list ..
        security_groups = get_security_groups_from_checkbox_list(
            self.req.POST, self.form_prefix or '', field_name_prefix='mllp_security_group_checkbox_')

        prefix = self.form_prefix or ''

        out = {
            'cluster_id': self.cluster_id,
            'is_internal': False,
            'is_active': True,
            'connection': 'channel',
            'transport': 'plain_http',
            'name': _REST_Channel_Name_Prefix + mllp_name,
            'url_path': self.req.POST[prefix + 'rest_url_path'],
            'service': self.req.POST[prefix + 'service'],
            'security_id': security_id,
            'security_groups': security_groups,
            'data_format': 'hl7-v2',
            'should_parse_on_input': True,
            'match_slash': False,
            'merge_url_params_req': True,
        }

        return out

# ################################################################################################################################

    def _create_rest_channel(self, mllp_name:'str') -> 'int':
        """ Creates a backing REST channel and returns its ID.
        """
        message = self._build_rest_channel_message(mllp_name)
        response = self.req.zato.client.invoke('zato.http-soap.create', message)

        if response.ok:
            rest_channel_id = response.data.id
            logger.info('Created backing REST channel id=%s for MLLP channel `%s`', rest_channel_id, mllp_name)
            return rest_channel_id
        else:
            logger.error('Could not create backing REST channel for `%s`: %s', mllp_name, response.details)
            return 0

# ################################################################################################################################

    def _edit_rest_channel(self, rest_channel_id:'int', mllp_name:'str') -> 'None':
        """ Updates the backing REST channel with current form values.
        """
        message = self._build_rest_channel_message(mllp_name)
        message['id'] = rest_channel_id
        response = self.req.zato.client.invoke('zato.http-soap.edit', message)

        if response.ok:
            logger.info('Updated backing REST channel id=%s for MLLP channel `%s`', rest_channel_id, mllp_name)
        else:
            logger.error('Could not update backing REST channel id=%s: %s', rest_channel_id, response.details)

# ################################################################################################################################

    def _delete_rest_channel(self, rest_channel_id:'int') -> 'None':
        """ Deletes the backing REST channel.
        """
        message = {
            'id': rest_channel_id,
            'cluster_id': self.cluster_id,
        }
        response = self.req.zato.client.invoke('zato.http-soap.delete', message)

        if response.ok:
            logger.info('Deleted backing REST channel id=%s', rest_channel_id)
        else:
            logger.error('Could not delete backing REST channel id=%s: %s', rest_channel_id, response.details)

# ################################################################################################################################

    def post_process_return_data(self, return_data:'dict') -> 'dict':
        """ After the MLLP channel is saved, manage the backing REST channel.
        """

        prefix = self.form_prefix or ''
        use_rest = bool(self.req.POST.get(prefix + 'use_rest'))
        mllp_name = return_data['name']

        # .. read the existing rest_channel_id, if any ..
        rest_channel_id = self.req.POST.get('rest_channel_id') or return_data.get('rest_channel_id') or 0
        rest_channel_id = int(rest_channel_id) if rest_channel_id else 0

        if use_rest:

            if rest_channel_id:
                # .. the backing channel already exists, update it ..
                self._edit_rest_channel(rest_channel_id, mllp_name)
            else:
                # .. create a new backing channel ..
                rest_channel_id = self._create_rest_channel(mllp_name)

        else:
            if rest_channel_id:
                # .. REST was toggled off, delete the backing channel ..
                self._delete_rest_channel(rest_channel_id)
                rest_channel_id = 0

        # .. update the MLLP channel config with the rest_channel_id ..
        if rest_channel_id != int(return_data.get('rest_channel_id') or 0):
            mllp_id = return_data.get('id') or self.req.POST.get('id')
            if mllp_id:
                self.req.zato.client.invoke('zato.generic.connection.edit', {
                    'id': mllp_id,
                    'cluster_id': self.cluster_id,
                    'rest_channel_id': rest_channel_id,
                    'type_': GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP,
                    'is_internal': False,
                    'is_channel': True,
                    'is_outconn': False,
                    'name': mllp_name,
                    'service': self.req.POST[prefix + 'service'],
                })

        return_data['rest_channel_id'] = rest_channel_id
        return_data['use_rest'] = use_rest

        return return_data

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-hl7-mllp-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-hl7-mllp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-hl7-mllp-delete'
    error_message = 'Could not delete HL7 MLLP channel'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

# .. MLLP framing bytes ..
_MLLP_Start_Byte = b'\x0b'
_MLLP_End_Bytes  = b'\x1c\x0d'

# .. TCP recv buffer size ..
_Recv_Buffer_Size = 65536

# .. socket timeout in seconds ..
_Socket_Timeout = 90

# ################################################################################################################################
# ################################################################################################################################

def _resolve_mllp_listener_address(req:'any_') -> 'tuple[str, int]':
    """ Resolves where the shared MLLP listener accepts connections - the port lives
    in the server process and the listener runs on the same host as the server itself.
    """
    response = req.zato.client.invoke('zato.server.invoker', {'func_name': 'get_hl7_mllp_port'})
    port = int(response.data)

    host = urlparse(req.zato.client.address).hostname

    return host, port

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def invoke_channel(req:'any_', id:'str') -> 'JsonResponse':
    """ Sends an MLLP-framed HL7 message to the server's MLLP listener and returns the response.
    """
    try:
        payload = req.POST['data-request']
        payload_bytes = payload.encode('utf-8')

        # .. find the listener - a port of zero means no MLLP channel is running ..
        listener_host, listener_port = _resolve_mllp_listener_address(req)

        if not listener_port:
            return JsonResponse({
                'data': 'No HL7 MLLP listener is running - create an active MLLP channel first',
                'response_time_human': '',
                'content_type': 'text/plain',
            }, status=HTTPStatus.BAD_REQUEST)

        # .. wrap in MLLP framing ..
        mllp_message = _MLLP_Start_Byte + payload_bytes + _MLLP_End_Bytes

        start = time()

        # .. open a TCP connection to the listener ..
        sock = socket_(AF_INET, SOCK_STREAM)
        sock.settimeout(_Socket_Timeout)

        try:
            sock.connect((listener_host, listener_port))
            sock.sendall(mllp_message)

            # .. read the MLLP-framed response ..
            response_data = b''
            while True:
                chunk = sock.recv(_Recv_Buffer_Size)
                if not chunk:
                    break
                response_data += chunk

                # .. stop once we see the MLLP end bytes ..
                if _MLLP_End_Bytes in response_data:
                    break

        finally:
            sock.close()

        elapsed = time() - start

        # .. strip MLLP framing from the response ..
        response_text = response_data
        if response_text.startswith(_MLLP_Start_Byte):
            response_text = response_text[1:]
        end_idx = response_text.find(_MLLP_End_Bytes)
        if end_idx != -1:
            response_text = response_text[:end_idx]

        response_body = response_text.decode('utf-8', errors='replace')

        return JsonResponse({
            'data': response_body,
            'response_time_human': '{:.1f}ms'.format(elapsed * 1000),
            'content_type': 'text/plain',
        })

    except Exception as e:
        logger.error('invoke_channel error: %s', format_exc())
        return JsonResponse({
            'data': str(e),
            'response_time_human': '',
            'content_type': 'text/plain',
        }, status=HTTPStatus.INTERNAL_SERVER_ERROR)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def import_demo_config(req:'any_') -> 'HttpResponse':
    """ Runs the HL7 demo import on the server - the demo connections, the alert
    rules, the seeded week of audit history and the live traffic burst.
    """
    response = req.zato.client.invoke('zato.server.invoker', {'func_name': 'import_demo_hl7'})

    out = HttpResponse()
    out.content = str(response.data)

    return out

# ################################################################################################################################
# ################################################################################################################################
