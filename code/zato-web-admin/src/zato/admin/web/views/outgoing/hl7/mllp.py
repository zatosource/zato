# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# Django
from django.http import JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.outgoing.hl7.mllp import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, invoke_action_handler, method_allowed
from zato.common.api import GENERIC, generic_attrs
from zato.common.crypto.api import CryptoManager
from zato.common.hl7.mllp.client import HL7MLLPClient
from zato.common.hl7.mllp.fields import Outconn_Defaults
from zato.common.hl7.mllp.tls import build_client_ssl_context
from zato.common.model.hl7 import HL7MLLPOutconnConfigObject
from zato.common.util.api import hex_sequence_to_bytes
from zato.common.util.tcp import parse_address

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# .. the multi-step wizard template, serving both the create and the edit page ..
_Wizard_Template = 'zato/outgoing/hl7/mllp-wizard.html'

# .. what the live check sends - an admission, which is the message type every receiving
# system in the field handles, so a rejection means the endpoint is wrong rather than that
# the sample was ..
_Probe_Message = (
    'MSH|^~\\&|ZATO|ZATO|RECEIVER|RECEIVER|20240315120000||ADT^A01^ADT_A01|{control_id}|P|2.5\r'
    'EVN|A01|20240315120000\r'
    'PID|1||12345^^^FAC^MR||SMITH^JOHN^A||19800115|M\r'
    'PV1|1|I'
)

# .. how many bits the control id of one check is made of - it is echoed back in MSA-2,
# .. which is what tells a reply meant for this check apart from any other ..
_Probe_Control_Id_Bits = 32

# .. the connection's receive timeout is configured in milliseconds and the client takes seconds ..
_Ms_Per_Second = 1000

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'outgoing-hl7-mllp'
    template = 'zato/outgoing/hl7/mllp.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = HL7MLLPOutconnConfigObject
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active', 'is_internal', 'security_name', 'address', 'pool_size'
    output_optional = (
        'should_log_messages', 'logging_level',
        'max_msg_size', 'read_buffer_size', 'recv_timeout',
        'start_seq', 'end_seq', 'max_wait_time',
        'max_retries', 'backoff_base_seconds', 'backoff_cap_seconds', 'backoff_jitter_percent',
        'circuit_breaker_threshold_percent', 'circuit_breaker_window_seconds', 'circuit_breaker_reset_seconds',
        'tls_cert_path', 'tls_key_path', 'tls_ca_path',
    ) + generic_attrs
    output_repeated = True

# ################################################################################################################################

    def handle(self):
        return {
            'show_search_form': True,
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'is_internal', 'address'
    input_optional = (
        'is_active', 'pool_size',
        'should_log_messages', 'logging_level',
        'max_msg_size', 'read_buffer_size', 'recv_timeout',
        'start_seq', 'end_seq', 'max_wait_time',
        'max_retries', 'backoff_base_seconds', 'backoff_cap_seconds', 'backoff_jitter_percent',
        'circuit_breaker_threshold_percent', 'circuit_breaker_window_seconds', 'circuit_breaker_reset_seconds',
        'tls_cert_path', 'tls_key_path', 'tls_ca_path',
    ) + generic_attrs
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict:'stranydict') -> 'None':
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outgoing'] = True
        initial_input_dict['is_outconn'] = True
        initial_input_dict['sec_use_rbac'] = False

# ################################################################################################################################

    def success_message(self, item:'any_') -> 'str':
        out = 'Successfully {} HL7 MLLP outgoing connection `{}`'.format(self.verb, item.name)
        return out

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'outgoing-hl7-mllp-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'outgoing-hl7-mllp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'outgoing-hl7-mllp-delete'
    error_message = 'Could not delete HL7 MLLP outgoing connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def wizard_create(req:'any_') -> 'TemplateResponse':
    """ A multi-step wizard for a new HL7 MLLP outgoing connection.
    """
    return_data = {
        'cluster_id': req.zato.cluster_id,
        'form': CreateForm(),
        'is_edit': False,
        'item_id': '',
    }

    out = TemplateResponse(req, _Wizard_Template, return_data)
    return out

# ################################################################################################################################

def _get_wizard_initial(item:'stranydict') -> 'stranydict':
    """ What the wizard's fields open with for one stored connection - what it has on record,
    with the shared defaults standing in for any field added after it was created.
    """
    out = dict(Outconn_Defaults)

    for name in out:

        if name not in item:
            continue

        value = item[name]

        # A field the record has nothing under is one the default answers for. Rendering the blank
        # instead would post a blank back, and a blank is not a number - which is what the server
        # would have to make of one arriving under a field that counts seconds or bytes.
        if value is None:
            continue

        if value == '':
            continue

        out[name] = value

    # Name and address are required rather than defaulted, so they are not among the fields above
    out['name'] = item['name']
    out['address'] = item['address']

    return out

# ################################################################################################################################

@method_allowed('GET')
def wizard_edit(req:'any_', id:'str') -> 'TemplateResponse':
    """ The same wizard, opened on one existing HL7 MLLP outgoing connection.
    """

    # The URL points to one connection, so one connection is what is fetched ..
    response = req.zato.client.invoke('zato.generic.connection.get-by-id', {'id': id})

    if not response.ok:
        raise Exception(f'HL7 MLLP outgoing connection with id `{id}` could not be read')

    item_dict = response.data

    # .. the edit endpoint reads its input under the edit- prefix, which is what the form
    # .. is built with and what the wizard's own fieldPrefix mirrors ..
    form = EditForm(prefix='edit')

    for name, value in _get_wizard_initial(item_dict).items():
        form.fields[name].initial = value

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'form': form,
        'is_edit': True,
        'item_id': item_dict['id'],
    }

    out = TemplateResponse(req, _Wizard_Template, return_data)
    return out

# ################################################################################################################################

def _build_probe_client(req:'any_') -> 'HL7MLLPClient':
    """ Builds the client the live check sends with, out of what the wizard currently has on
    screen rather than out of anything stored - which is what lets a check run before the
    connection has ever been saved.
    """
    host, port_string = parse_address(req.POST['address'])
    port = int(port_string)

    start_sequence = hex_sequence_to_bytes(req.POST['start_seq'])
    end_sequence   = hex_sequence_to_bytes(req.POST['end_seq'])

    # TLS turns on once a CA bundle is named, the same rule the connection itself is built under
    ca_path = req.POST['tls_ca_path']

    if ca_path:
        ssl_context = build_client_ssl_context(ca_path, req.POST['tls_cert_path'], req.POST['tls_key_path'])
    else:
        ssl_context = None

    out = HL7MLLPClient(
        host,
        port,
        start_sequence,
        end_sequence,
        receive_timeout=int(req.POST['recv_timeout']) / _Ms_Per_Second,
        max_message_size=int(req.POST['max_msg_size']),
        read_buffer_size=int(req.POST['read_buffer_size']),
        ssl_context=ssl_context,
    )

    return out

# ################################################################################################################################

@method_allowed('POST')
def wizard_test_action(req:'any_') -> 'JsonResponse':
    """ Sends one message to the endpoint the wizard currently names and reports what came back.
    Nothing is stored either way - this only says whether the answers given so far reach a
    receiver that speaks MLLP.
    """
    address = req.POST['address']

    try:
        client = _build_probe_client(req)

        control_id = CryptoManager.generate_hex_string(_Probe_Control_Id_Bits)
        message = _Probe_Message.format(control_id=control_id)

        # The control id goes along, so the acknowledgment is checked for having echoed it
        # rather than merely for having arrived
        started_at = monotonic()
        result = client.send(message.encode('utf-8'), control_id)
        elapsed_ms = (monotonic() - started_at) * _Ms_Per_Second

    except Exception as e:

        error_text = str(e)
        if not error_text:
            error_text = e.__class__.__name__

        return JsonResponse({
            'is_ok': False,
            'summary': f'{address} could not be reached - {error_text}',
        })

    # A receiver that turns the message away has still answered, so the check reports what it
    # said rather than reporting that nothing was there
    if result.is_accepted:
        summary = f'{address} answered {result.ack_code} in {elapsed_ms:.0f} ms'
    else:
        summary = f'{address} answered {result.ack_code} - {result.error_text}'

    out = JsonResponse({
        'is_ok': result.is_accepted,
        'summary': summary,
    })

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def invoke(
    req:'any_',
    conn_id:'str',
    max_wait_time:'str',
    conn_name:'str',
    conn_slug:'str',
    ) -> 'TemplateResponse':

    return_data = {
        'conn_id': conn_id,
        'conn_name': conn_name,
        'conn_slug': conn_slug,
        'conn_type': GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP,
        'timeout': max_wait_time,
        'cluster_id': req.zato.cluster_id,
    }

    out = TemplateResponse(req, 'zato/outgoing/hl7/mllp-invoke.html', return_data)
    return out

# ################################################################################################################################

@method_allowed('POST')
def invoke_action(req:'any_', conn_name:'str') -> 'any_':
    field_names = ('conn_name', 'conn_type', 'request_data', 'timeout')

    out = invoke_action_handler(req, 'zato.generic.connection.invoke', field_names)
    return out

# ################################################################################################################################
