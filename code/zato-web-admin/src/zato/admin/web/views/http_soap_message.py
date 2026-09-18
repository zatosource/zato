# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.admin.web import alerts_tab, delivery_tab, from_user_to_utc, from_utc_to_user
from zato.admin.web.forms import health_check_unit_for_form, health_check_unit_to_scheduler
from zato.admin.web.views import get_security_id_from_select, get_security_groups_from_checkbox_list
from zato.common.alerting.object_config import get_alert_type
from zato.common.api import generic_attrs, HTTP_SOAP, PARAMS_PRIORITY, URL_PARAMS_PRIORITY, URL_TYPE

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# Names of the fields that describe the declarative invocation profile of an outgoing REST connection
_invocation_field_names = (
    'scheduler_run_every',
    'scheduler_run_unit',
    'scheduler_start_date',
    'scheduler_job_id',
    'request_method',
    'request_query_string',
    'request_path_params',
    'request_headers',
    'request_data',
    'request_data_mode',
    'response_map',
    'response_map_mode',
    'callback_type',
    'callback_name',
    'health_check_run_every',
    'health_check_run_unit',
    'health_check_job_id',
)

# The retry config of an outgoing connection - each field maps to its shared default
_retry = HTTP_SOAP.Retry

_health_check = HTTP_SOAP.HealthCheck

_retry_field_defaults = {
    _retry.Field_Max_Retries: _retry.Default_Max_Retries,
    _retry.Field_Sleep_Time: _retry.Default_Sleep_Time,
    _retry.Field_Backoff_Threshold: _retry.Default_Backoff_Threshold,
    _retry.Field_Backoff_Multiplier: _retry.Default_Backoff_Multiplier,
}

# The callback name arrives from the widget that matches the callback type selected
_callback_widget_names = {
    'service': 'callback_service',
    'topic': 'callback_topic',
    'rest': 'callback_rest',
}

# ################################################################################################################################
# ################################################################################################################################

def get_edit_create_message(params:'any_', prefix:'str'='', user_profile:'any_'=None) -> 'stranydict':
    """ A bunch of attributes that can be used by both 'edit' and 'create' actions
    for channels and outgoing connections.
    """
    security_id = get_security_id_from_select(params, prefix)
    security_groups = get_security_groups_from_checkbox_list(params, prefix)

    message = {
        'is_internal': False,
        'connection': params['connection'],
        'transport': params['transport'],
        'id': params.get('id'),
        'cluster_id': params['cluster_id'],
        'name': params[prefix + 'name'],
        'is_active': bool(params.get(prefix + 'is_active')),
        'is_audit_log_active': bool(params.get(prefix + 'is_audit_log_active')),
        'host': params.get(prefix + 'host'),
        'url_path': params.get(prefix + 'url_path', '/'),
        'merge_url_params_req': bool(params.get(prefix + 'merge_url_params_req')),
        'match_slash': bool(params.get(prefix + 'match_slash')),
        'http_accept': params.get(prefix + 'http_accept'),
        'url_params_pri': params.get(prefix + 'url_params_pri', URL_PARAMS_PRIORITY.DEFAULT),
        'params_pri': params.get(prefix + 'params_pri', PARAMS_PRIORITY.DEFAULT),
        'method': params.get(prefix + 'method'),
        'soap_action': params.get(prefix + 'soap_action', ''),
        'soap_version': params.get(prefix + 'soap_version', None),
        'use_mtom': bool(params.get(prefix + 'use_mtom')),
        'data_format': params.get(prefix + 'data_format') or None,
        'service': params.get(prefix + 'service'),
        'ping_method': params.get(prefix + 'ping_method'),
        'pool_size': params.get(prefix + 'pool_size'),
        'timeout': params.get(prefix + 'timeout'),
        'security_id': security_id,
        'security_groups': security_groups,
        'content_type': params.get(prefix + 'content_type'),
        'validate_tls': params.get(prefix + 'validate_tls'),
        'data_encoding': params.get(prefix + 'data_encoding'),
        'gateway_service_list': params.get(prefix + 'gateway_service_list'),
    }

    # The OpenAPI checkbox exists only in the forms of REST channels
    if params['connection'] == 'channel':
        if params['transport'] == 'plain_http':
            message['should_include_in_openapi'] = bool(params.get(prefix + 'should_include_in_openapi'))

            # The deprecation fields exist only in the forms of REST channels too
            message['is_deprecated'] = bool(params.get(prefix + 'is_deprecated'))
            message['deprecation_sunset'] = params.get(prefix + 'deprecation_sunset', '')
            message['deprecation_successor'] = params.get(prefix + 'deprecation_successor', '')

    # The Alerts tab's fields exist in the forms of REST and SOAP channels and of outgoing REST connections
    if alert_type := get_alert_type(params['connection'], params['transport']):
        for name in alerts_tab.get_storage_field_names(alert_type):
            value = params.get(prefix + name, '')
            message[name] = alerts_tab.pre_process_alert_item(alert_type, name, value)

        alerts_tab.join_unit_fields(alert_type, message)

    # The declarative invocation fields exist only in the forms of outgoing connections
    for name in _invocation_field_names:
        message[name] = params.get(prefix + name)

    # The form names the health check's unit in the singular, the scheduler in the plural
    if run_unit := message[_health_check.Field_Run_Unit]:
        message[_health_check.Field_Run_Unit] = health_check_unit_to_scheduler[run_unit]

    # The retry fields exist only in the forms of outgoing connections too - they are sent
    # as integers, with the shared defaults filling in for anything left empty in a form.
    if params['connection'] == 'outgoing':
        for name, default in _retry_field_defaults.items():
            if value := params.get(prefix + name):
                message[name] = int(value)
            else:
                message[name] = default

        # The queue switch and the DLQ config exist only in the forms of outgoing REST connections,
        # whose Delivery tab enters each count of seconds as a count and a unit
        if params['transport'] == URL_TYPE.PLAIN_HTTP:
            message.update(delivery_tab.get_message_fields(params, prefix))
            delivery_tab.join_unit_fields(params, prefix, message)

    # The start date is entered in the user's own timezone and format and it is stored in UTC
    if scheduler_start_date := message['scheduler_start_date']:
        message['scheduler_start_date'] = from_user_to_utc(scheduler_start_date, user_profile).isoformat()

    # The callback name comes from whichever widget matches the callback type selected
    if callback_type := message['callback_type']:
        widget_name = _callback_widget_names[callback_type]
        message['callback_name'] = params.get(prefix + widget_name)

    return message

# ################################################################################################################################
# ################################################################################################################################

def fill_row_from_item(
    http_soap:'any_',
    item:'any_',
    alert_type:'str',
    connection:'str',
    transport:'str',
    user_profile:'any_',
) -> 'None':
    """ The fields of a listed channel or outgoing connection that the edit form reads off its row -
    the Alerts tab's, the generic attributes and, for an outgoing REST connection, the declarative
    invocation profile, the retry settings and the scheduler's start date in the user's own timezone.
    """
    # The Alerts tab's fields ride in the row for the edit form to read.
    if alert_type:
        for name in alerts_tab.get_storage_field_names(alert_type):
            if name in item:
                http_soap[name] = item[name]

        alerts_tab.split_unit_fields(alert_type, http_soap)

    for name in generic_attrs:
        setattr(http_soap, name, item.get(name))

    # The declarative invocation details are opaque attributes so they are absent
    # from connections that never set them.
    if connection == 'outgoing' and transport == URL_TYPE.PLAIN_HTTP:
        for name in _invocation_field_names:
            setattr(http_soap, name, item.get(name))

        # The scheduler names the health check's unit in the plural, the form in the singular
        http_soap[_health_check.Field_Run_Unit] = health_check_unit_for_form(item.get(_health_check.Field_Run_Unit))

        # The retry fields are opaque attributes too - connections that predate them
        # carry no values, in which case the shared defaults are displayed.
        for name, default in _retry_field_defaults.items():
            value = item.get(name)
            if value is None:
                value = default
            setattr(http_soap, name, value)

        # The queue switch and the DLQ config are opaque attributes too, and the Delivery tab
        # shows each count of seconds as a count and a unit
        delivery_tab.fill_row(http_soap, item)
        delivery_tab.split_unit_fields(http_soap)

        # The start date is stored in UTC and displayed in the user's own timezone and format
        if scheduler_start_date := http_soap.get('scheduler_start_date'):
            http_soap.scheduler_start_date = from_utc_to_user(
                scheduler_start_date + '+00:00', user_profile)

# ################################################################################################################################
# ################################################################################################################################
