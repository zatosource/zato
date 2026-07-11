# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.http import HttpResponseServerError, JsonResponse

# Zato
from zato.admin.web import from_user_to_utc, from_utc_to_user
from zato.admin.web.forms import add_http_soap_select
from zato.admin.web.forms.outgoing.soap import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, extract_security_id, get_js_dt_format, id_only_service, \
    Index as _Index, method_allowed
from zato.common.api import CONNECTION, SEC_DEF_TYPE_NAME, URL_TYPE, ZATO_NONE

# ################################################################################################################################
# ################################################################################################################################

# The declarative invocation profile of an outgoing SOAP connection - all these fields
# live in the connection's opaque attributes.
_invocation_field_names = (
    'request_operation',
    'request_message',
    'request_message_map',
    'request_soap_headers',
    'wsa_action',
    'wsa_to',
    'wsa_reply_to',
    'response_map',
    'response_map_mode',
    'callback_type',
    'callback_name',
    'scheduler_run_every',
    'scheduler_run_unit',
    'scheduler_start_date',
    'scheduler_job_id',
    'health_check_run_every',
    'health_check_run_unit',
    'health_check_notify_on',
    'health_check_job_id',
    'health_check_callback_type',
    'health_check_callback_name',
)

# The callback name arrives from the widget that matches the callback type selected
_callback_widget_names = {
    'service': 'callback_service',
    'topic': 'callback_topic',
    'rest': 'callback_rest',
}

# The same pattern applies to the health check tab's callback widgets
_health_check_callback_widget_names = {
    'service': 'health_check_callback_service',
    'topic': 'health_check_callback_topic',
    'rest': 'health_check_callback_rest',
}

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
    output_optional = ('host', 'url_path', 'soap_action', 'soap_version', 'security_id', 'security_name', 'sec_type', \
        'sec_type_name', 'validate_tls', 'ping_method', 'timeout', 'content_type', 'serialization_type', \
        'use_ws_addressing', 'use_mtom', 'body_credentials', 'tls_client_cert', 'tls_client_key') + _invocation_field_names
    output_repeated = True

# ################################################################################################################################

    def on_before_append_item(self, item):

        # Connections without security never had the attribute set at all.
        security_id = getattr(item, 'security_id', None)

        if security_id and security_id != ZATO_NONE:
            item.sec_type_name = SEC_DEF_TYPE_NAME[item.sec_type]

        # The start date is stored in UTC and displayed in the user's own timezone and format,
        # and only connections with a scheduler configured carry it at all.
        if scheduler_start_date := getattr(item, 'scheduler_start_date', None):
            item.scheduler_start_date = from_utc_to_user(scheduler_start_date + '+00:00', self.req.zato.user_profile)

        return item

# ################################################################################################################################

    def handle(self):
        security_list = self.get_sec_def_list(None)

        create_form = CreateForm(security_list, req=self.req)
        edit_form = EditForm(security_list, prefix='edit', req=self.req)

        # The callback tabs let outgoing SOAP connections deliver responses
        # and health check outcomes to outgoing REST connections
        add_http_soap_select(create_form, 'callback_rest', self.req, CONNECTION.OUTGOING, URL_TYPE.PLAIN_HTTP, by_id=False)
        add_http_soap_select(edit_form, 'callback_rest', self.req, CONNECTION.OUTGOING, URL_TYPE.PLAIN_HTTP, by_id=False)
        add_http_soap_select(create_form, 'health_check_callback_rest', self.req, CONNECTION.OUTGOING, URL_TYPE.PLAIN_HTTP, by_id=False)
        add_http_soap_select(edit_form, 'health_check_callback_rest', self.req, CONNECTION.OUTGOING, URL_TYPE.PLAIN_HTTP, by_id=False)

        out = {
            'show_search_form': True,
            'create_form': create_form,
            'edit_form': edit_form,
        }

        # The scheduler tab's start date picker needs the user's date and time format
        out.update(get_js_dt_format(self.req.zato.user_profile))

        return out

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'host'
    input_optional = ('is_active', 'url_path', 'soap_action', 'soap_version', 'security_id', 'validate_tls', \
        'ping_method', 'timeout', 'content_type', 'serialization_type', \
        'use_ws_addressing', 'use_mtom', 'body_credentials', 'tls_client_cert', 'tls_client_key') + \
        _invocation_field_names + ('callback_service', 'callback_topic', 'callback_rest') + \
        ('health_check_callback_service', 'health_check_callback_topic', 'health_check_callback_rest')
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

        # The start date is entered in the user's own timezone and format and it is stored in UTC
        if scheduler_start_date := input_dict.get('scheduler_start_date'):
            input_dict['scheduler_start_date'] = from_user_to_utc(
                scheduler_start_date, self.req.zato.user_profile).isoformat()

        # Checkboxes arrive as 'on' or not at all - the backend expects real booleans.
        for name in ('use_ws_addressing', 'use_mtom'):
            input_dict[name] = bool(input_dict.get(name))

        # The callback name comes from whichever widget matches the callback type selected
        if callback_type := input_dict.get('callback_type'):
            widget_name = _callback_widget_names[callback_type]
            input_dict['callback_name'] = input_dict.get(widget_name)

        # The health check tab's callback widgets work the same way
        if health_check_callback_type := input_dict.get('health_check_callback_type'):
            widget_name = _health_check_callback_widget_names[health_check_callback_type]
            input_dict['health_check_callback_name'] = input_dict.get(widget_name)

        # The widgets themselves are not part of the backend's input
        for widget_name in _callback_widget_names.values():
            input_dict.pop(widget_name, None)
        for widget_name in _health_check_callback_widget_names.values():
            input_dict.pop(widget_name, None)

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
