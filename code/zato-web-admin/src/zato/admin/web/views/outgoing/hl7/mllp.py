# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http import HTTPStatus
from json import dumps
from time import monotonic

# Django
from django.http import JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web import alerts_tab, delivery_tab
from zato.admin.web.forms import populate_form_initial
from zato.admin.web.forms.outgoing.hl7.mllp import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.alerting.object_config import alert_type_mllp_outgoing, Field_Prefix
from zato.common.api import GENERIC, generic_attrs
from zato.common.ext.bunch import Bunch
from zato.common.hl7.mllp.client import HL7MLLPClient
from zato.common.hl7.mllp.tls import build_client_ssl_context
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

# .. what the live check does, said in its details - a plain connection or one with a TLS handshake ..
_Probe_Action_Tcp = 'TCP connect'
_Probe_Action_Tls = 'TCP connect and TLS handshake'

# .. the details of the live check are a JSON object, which is what they are highlighted as ..
_Probe_Details_Lexer = 'json'

# .. the connection's receive timeout is configured in milliseconds and the client takes seconds ..
_Ms_Per_Second = 1000

# .. the alert settings a connection carries and the names they travel under between the wizard and the backend ..
_alert_type = alert_type_mllp_outgoing
_alert_field_names = alerts_tab.get_storage_field_names(_alert_type)

# .. the retry fields, the queue switch and the DLQ config, stored in the connection's opaque attributes ..
_delivery_field_names = tuple(delivery_tab.field_defaults)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingMLLPConfigObject(Bunch):
    """ A config object for outgoing MLLP connections, filled in with attributes from the get-list response -
    a Bunch, so the Delivery tab's helpers and the template read its fields by name as well.
    """

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'outgoing-hl7-mllp'
    template = 'zato/outgoing/hl7/mllp.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = OutgoingMLLPConfigObject
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active', 'is_internal', 'security_name', 'address', 'pool_size'
    output_optional = (
        'should_log_messages', 'logging_level',
        'max_msg_size', 'read_buffer_size', 'recv_timeout',
        'start_seq', 'end_seq', 'max_wait_time',
        'circuit_breaker_threshold_percent', 'circuit_breaker_window_seconds', 'circuit_breaker_reset_seconds',
        'tls_cert_path', 'tls_key_path', 'tls_ca_path',
    ) + generic_attrs + _delivery_field_names
    output_repeated = True

# ################################################################################################################################

    def on_before_append_item(self, item:'any_') -> 'any_':

        # The retry fields, the queue switch and the DLQ config are opaque attributes - a connection that predates
        # them carries no values, so the defaults show, with each duration split into a count and a unit
        delivery_tab.fill_row(item, item)
        delivery_tab.split_unit_fields(item)

        return item

# ################################################################################################################################

    def handle(self):
        return {
            'show_search_form': True,
            'create_form': CreateForm(self.req),
            'edit_form': EditForm(self.req, prefix='edit'),
            'delivery_tab_config': delivery_tab.get_delivery_tab_config(),
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
        'circuit_breaker_threshold_percent', 'circuit_breaker_window_seconds', 'circuit_breaker_reset_seconds',
        'tls_cert_path', 'tls_key_path', 'tls_ca_path',
    ) + generic_attrs + _delivery_field_names + _alert_field_names
    output_required = 'id', 'name'

# ################################################################################################################################

    def pre_process_item(self, name:'str', value:'any_') -> 'any_':

        # The Alerts popup's fields arrive as text and are stored typed - booleans, integers and stripped text
        if name.startswith(Field_Prefix):
            out = alerts_tab.pre_process_alert_item(_alert_type, name, value)
            return out

        return value

# ################################################################################################################################

    def pre_process_input_dict(self, input_dict:'stranydict') -> 'None':

        # A duration is stored as seconds, which is what its count and unit join into
        alerts_tab.join_unit_fields(_alert_type, input_dict)

        # The retry fields, the queue switch and the DLQ config arrive as text and are stored typed,
        # with each duration's count and unit joined into seconds
        input_dict.update(delivery_tab.get_message_fields(self.req.POST, self.form_prefix))
        delivery_tab.join_unit_fields(self.req.POST, self.form_prefix, input_dict)

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
    form = CreateForm(req)

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'form': form,
        'is_edit': False,
        'item_id': '',
        'alerts_tab': alerts_tab.get_alerts_tab_context(form, _alert_type),
        'alerts_tab_config': alerts_tab.get_alerts_tab_config(_alert_type),
    }

    out = TemplateResponse(req, _Wizard_Template, return_data)
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
    form = EditForm(req, prefix='edit')

    # A duration is stored as seconds and edited as a count with a unit, and a connection that predates
    # the retry, queue and DLQ fields opens with their defaults
    alerts_tab.split_unit_fields(_alert_type, item_dict)
    delivery_tab.fill_row(item_dict, item_dict)
    delivery_tab.split_unit_fields(item_dict)
    populate_form_initial(form, item_dict)

    return_data = {
        'cluster_id': req.zato.cluster_id,
        'form': form,
        'is_edit': True,
        'item_id': item_dict['id'],
        'alerts_tab': alerts_tab.get_alerts_tab_context(form, _alert_type),
        'alerts_tab_config': alerts_tab.get_alerts_tab_config(_alert_type),
    }

    out = TemplateResponse(req, _Wizard_Template, return_data)
    return out

# ################################################################################################################################

def _build_probe_client(req:'any_', address:'str', ca_path:'str') -> 'HL7MLLPClient':
    """ Builds the client the live check connects with, out of what the wizard currently has on
    screen rather than out of anything stored - which is what lets a check run before the
    connection has ever been saved.
    """
    host, port = parse_address(address)

    start_sequence = hex_sequence_to_bytes(req.POST['start_seq'])
    end_sequence   = hex_sequence_to_bytes(req.POST['end_seq'])

    # TLS turns on once a CA bundle is named, the same rule the connection itself is built under
    if ca_path:
        ssl_context = build_client_ssl_context(ca_path, req.POST['tls_cert_path'], req.POST['tls_key_path'])
    else:
        ssl_context = None

    out = HL7MLLPClient(
        host,
        port,
        start_sequence,
        end_sequence,
        ssl_context=ssl_context,
    )

    return out

# ################################################################################################################################

@method_allowed('POST')
def wizard_test_action(req:'any_') -> 'JsonResponse':
    """ Opens a connection to the endpoint the wizard currently names and closes it again, with the
    TLS handshake if TLS is on. Nothing is sent and nothing is stored either way - this only says
    whether the answers given so far reach an endpoint that is listening.
    """
    # An address that cannot be connected to at all never gets this far, the wizard says so beside its button
    address = req.POST['address'].strip()

    # What the check is about to do, named in its details either way
    ca_path = req.POST['tls_ca_path']
    action = _Probe_Action_Tls if ca_path else _Probe_Action_Tcp

    try:
        client = _build_probe_client(req, address, ca_path)

        started_at = monotonic()
        client.ping()
        elapsed_ms = (monotonic() - started_at) * _Ms_Per_Second

    except Exception as e:

        error_text = str(e)
        if not error_text:
            error_text = e.__class__.__name__

        # The details say what was being done and what went wrong, and nothing else
        details = {
            'address': address,
            'action': action,
            'error': error_text,
        }

        return JsonResponse({
            'is_ok': False,
            'summary': f'{address} could not be reached - {error_text}',
            'details': dumps(details, indent=2),
            'details_lexer': _Probe_Details_Lexer,
        })

    details = {
        'address': address,
        'action': action,
        'elapsed_ms': round(elapsed_ms),
    }

    out = JsonResponse({
        'is_ok': True,
        'summary': f'{address} answered in {elapsed_ms:.0f} ms',
        'details': dumps(details, indent=2),
        'details_lexer': _Probe_Details_Lexer,
    })

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def invoke_action(req:'any_', conn_name:'str') -> 'JsonResponse':
    """ Sends the popup invoker's message through the outgoing connection and returns the raw ER7 acknowledgment.
    """
    try:
        request = {
            'conn_type': GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP,
            'conn_name': conn_name,
            'request_data': req.POST['data-request'],
        }

        started_at = monotonic()
        response = req.zato.client.invoke('zato.generic.connection.invoke', request)
        elapsed_ms = (monotonic() - started_at) * _Ms_Per_Second

        # A failed invocation still carries the details of what went wrong,
        # which the error branch below turns into a response for the popup
        if not response.ok:
            raise Exception(response.details)

        return JsonResponse({
            'data': response.data['response_data'],
            'response_time_human': '{:.1f}ms'.format(elapsed_ms),
            'content_type': 'text/plain',
        })

    except Exception as e:
        return JsonResponse({
            'data': str(e),
            'response_time_human': '',
            'content_type': 'text/plain',
        }, status=HTTPStatus.INTERNAL_SERVER_ERROR)

# ################################################################################################################################
