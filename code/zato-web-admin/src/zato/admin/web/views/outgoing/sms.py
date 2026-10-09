# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http import HTTPStatus
from json import dumps
from traceback import format_exc

# Django
from django.http import JsonResponse

# Zato
from zato.admin.web import alerts_tab, delivery_tab, sms_tab
from zato.admin.web.forms import add_select_from_service
from zato.admin.web.forms.outgoing.sms import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, SKIP_VALUE
from zato.common.alerting.object_config import alert_type_sms_outgoing, Field_Prefix
from zato.common.api import GENERIC, SMS
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The alert settings of the connection follow the SMS outgoing type
_alert_type = alert_type_sms_outgoing
_alert_field_names = alerts_tab.get_storage_field_names(_alert_type)

# The retry fields, stored in the connection's opaque attributes
_retry_field_names = tuple(delivery_tab.retry_field_defaults)

# The use_queue field and the DLQ config of the Delivery tab, stored in the connection's opaque attributes
_delivery_field_names = tuple(delivery_tab.field_defaults)

# The connection's own fields beyond its name and its secrets - the ones a form must fill in and the ones it may leave empty
_sms_required_field_names = sms_tab.Outgoing_Required_Field_Names
_sms_optional_field_names = sms_tab.Outgoing_Optional_Field_Names
_sms_field_names = sms_tab.Outgoing_Field_Names

# The fields that are stored encrypted and never shown again
_secret_field_names = sms_tab.Secret_Field_Names

# What the Invoke dialog posts
_post_body = 'data-request'
_post_from = 'from_'
_post_to = 'to'

# The content type the Invoke dialog's answer is shown as
_invoke_content_type = 'application/json'
_invoke_error_content_type = 'text/plain'

# How many decimal places of a second the response time is shown with
_response_time_format = '{:.3f}s'

# ################################################################################################################################
# ################################################################################################################################

def _add_channel_select(form:'any_', req:'any_') -> 'None':
    """ Fills the channel select with the existing SMS channels.
    """
    service_extra = {'type_': GENERIC.CONNECTION.TYPE.CHANNEL_SMS, 'paginate': False}
    add_select_from_service(form, req, 'zato.generic.connection.get-list', SMS.Field_Channel_Name, by_id=False,
        service_extra=service_extra)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-sms'
    template = 'zato/outgoing/sms.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active'
    output_optional = _sms_field_names + _retry_field_names + _delivery_field_names + _alert_field_names
    output_repeated = True

# ################################################################################################################################

    def on_before_append_item(self, item:'any_') -> 'any_':

        item.provider_human = SMS.ProviderHuman[item.provider]

        # The retry fields are opaque attributes
        delivery_tab.fill_retry_row(item)

        # The Delivery tab's fields are shown with their defaults and durations split into a count and a unit
        delivery_tab.fill_row(item, item)
        delivery_tab.split_unit_fields(item)

        # The Alerts tab shows a duration as a count with a unit, not as the seconds it is stored as
        alerts_tab.split_unit_fields(_alert_type, item)

        # The timeout is shown as a count with a unit
        sms_tab.split_timeout(item)

        return item

# ################################################################################################################################

    def handle(self) -> 'anydict':

        create_form = CreateForm(self.req)
        edit_form = EditForm(self.req, prefix='edit')

        _add_channel_select(create_form, self.req)
        _add_channel_select(edit_form, self.req)

        # A message from the DLQ is forwarded to a pub/sub topic, selected by name from the topics that currently exist
        add_select_from_service(create_form, self.req, 'zato.pubsub.topic.get-list', 'dlq_forward_to', by_id=False)
        add_select_from_service(edit_form, self.req, 'zato.pubsub.topic.get-list', 'dlq_forward_to', by_id=False)

        out = {
            'show_search_form': True,
            'create_form': create_form,
            'edit_form': edit_form,
            'delivery_tab_config': delivery_tab.get_delivery_tab_config(),
            'create_alerts_tab': alerts_tab.get_alerts_tab_context(create_form, _alert_type),
            'edit_alerts_tab': alerts_tab.get_alerts_tab_context(edit_form, _alert_type),
            'alerts_tab_config': alerts_tab.get_alerts_tab_config(_alert_type),
            'sms_config': sms_tab.get_provider_config(),
        }

        return out

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = ('name',) + _sms_required_field_names
    input_optional = ('is_active',) + _secret_field_names + _sms_optional_field_names + _retry_field_names + \
        _delivery_field_names + _alert_field_names
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict:'anydict') -> 'None':
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_SMS
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True

# ################################################################################################################################

    def pre_process_item(self, name:'str', value:'any_') -> 'any_':

        # An empty secret on input means the current one is to be kept,
        # which is why the field cannot be sent to the backend at all.
        if name in _secret_field_names:
            if not value:
                return SKIP_VALUE

        # The Alerts tab's fields arrive as text and are stored typed - booleans, integers and stripped text
        if name.startswith(Field_Prefix):
            value = alerts_tab.pre_process_alert_item(_alert_type, name, value)

        return value

# ################################################################################################################################

    def pre_process_input_dict(self, input_dict:'anydict') -> 'None':

        # The retry fields arrive as strings and the backend expects integers,
        # with the shared defaults filling in for anything left empty in a form.
        delivery_tab.type_retry_fields(input_dict)

        # The Delivery tab's fields arrive as text and are stored typed, with each duration's count and unit joined
        # into seconds - the retry durations among them, which is why the join runs over the whole input
        input_dict.update(delivery_tab.get_message_fields(self.req.POST, self.form_prefix))
        delivery_tab.join_unit_fields(self.req.POST, self.form_prefix, input_dict)

        # A duration of the Alerts tab is stored as seconds, joined from its count and unit
        alerts_tab.join_unit_fields(_alert_type, input_dict)

        # The timeout is stored as seconds, joined from its count and unit
        sms_tab.join_timeout(self.req.POST, self.form_prefix, input_dict)

# ################################################################################################################################

    def success_message(self, item:'any_') -> 'str':
        out = 'Successfully {} outgoing SMS connection `{}`'.format(self.verb, item.name)
        return out

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-sms-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-sms-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-sms-delete'
    error_message = 'Could not delete outgoing SMS connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

def _build_invoke_error(error_message:'str') -> 'JsonResponse':
    """ The error response of a failed send, in the format of the invoker overlay.
    """
    out = JsonResponse({
        'data': error_message,
        'response_time_human': '',
        'content_type': _invoke_error_content_type,
    }, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    return out

# ################################################################################################################################

@method_allowed('POST')
def invoke_outconn(req:'any_', id:'str') -> 'JsonResponse':
    """ Sends one message through an outgoing SMS connection and responds in the format of the invoker overlay.
    """
    try:
        request = {
            'id': id,
            'from_': req.POST[_post_from],
            'to': req.POST[_post_to],
            'body': req.POST[_post_body],
        }

        response = req.zato.client.invoke(SMS.Invoke_Service, request)

        # The message never left if the service did not succeed ..
        if not response.ok:
            out = _build_invoke_error(str(response.details))
            return out

        # .. otherwise, the provider's own answer is what the caller is shown.
        data = response.data
        response_time_ms = data['response_time_ms']
        response_time = _response_time_format.format(response_time_ms / 1000)

        result = {
            'id': data['id'],
            'status': data['status'],
            'raw': data['raw'],
        }

        out = JsonResponse({
            'data': dumps(result, indent=2),
            'response_time_human': response_time,
            'content_type': _invoke_content_type,
        })

        return out

    except Exception as e:
        logger.error('Could not send an SMS message, e:`%s`', format_exc())
        out = _build_invoke_error(str(e))
        return out

# ################################################################################################################################
# ################################################################################################################################
