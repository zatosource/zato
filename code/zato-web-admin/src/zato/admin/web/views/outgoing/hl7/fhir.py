# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web import alerts_tab
from zato.admin.web.forms import health_check_unit_for_form, health_check_unit_to_scheduler
from zato.admin.web.forms.outgoing.hl7.fhir import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, \
    extract_security_id, Index as _Index, invoke_action_handler, method_allowed, ping_connection, SecurityList
from zato.common.alerting.object_config import alert_type_fhir, Field_Prefix
from zato.common.api import GENERIC, generic_attrs, HTTP_SOAP, SEC_DEF_TYPE
from zato.common.model.hl7 import HL7FHIRConfigObject

# ################################################################################################################################
# ################################################################################################################################

# The alert settings of the connection follow the FHIR type
_alert_type = alert_type_fhir
_alert_field_names = alerts_tab.get_storage_field_names(_alert_type)

# How often the connection is pinged - fields of the connection's own, edited on the Alerts tab
_health_check = HTTP_SOAP.HealthCheck
_health_check_field_names = (
    _health_check.Field_Run_Every,
    _health_check.Field_Run_Unit,
    _health_check.Field_Job_ID,
)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'outgoing-hl7-fhir'
    template = 'zato/outgoing/hl7/fhir.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = HL7FHIRConfigObject
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active', 'is_internal', 'address', 'security_id', \
        'pool_size', 'security_name'
    output_optional = ('extra',) + generic_attrs + _health_check_field_names + _alert_field_names
    output_repeated = True

# ################################################################################################################################

    def on_before_append_item(self, item):

        # The scheduler names the health check's unit in the plural, the form in the singular,
        # and a connection that was never given a health check carries no unit at all
        if _health_check.Field_Run_Unit in item:
            run_unit = item[_health_check.Field_Run_Unit]
        else:
            run_unit = None

        item[_health_check.Field_Run_Unit] = health_check_unit_for_form(run_unit)

        # The edit form shows a duration as a count with a unit, not as the seconds it is stored as
        alerts_tab.split_durations(_alert_type, item)

        return item

# ################################################################################################################################

    def handle(self):

        security_list = SecurityList.from_service(
            self.req.zato.client,
            self.cluster_id,
            security_type_list = [SEC_DEF_TYPE.BASIC_AUTH, SEC_DEF_TYPE.OAUTH],
            needs_definition_type_name_label=True
        )

        create_form = CreateForm(self.req, security_list)
        edit_form = EditForm(self.req, security_list, prefix='edit')

        return {
            'show_search_form': True,
            'create_form': create_form,
            'edit_form': edit_form,
            'create_alerts_tab': alerts_tab.get_alerts_tab_context(create_form, _alert_type),
            'edit_alerts_tab': alerts_tab.get_alerts_tab_context(edit_form, _alert_type),
            'alerts_tab_config': alerts_tab.get_alerts_tab_config(_alert_type),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'is_internal', 'address', 'security_id', 'pool_size'
    input_optional = ('is_active', 'extra') + generic_attrs + _health_check_field_names + _alert_field_names
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outgoing'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['recv_timeout'] = 250

# ################################################################################################################################

    def pre_process_item(self, name, value):

        # The Alerts tab's fields arrive as text and are stored typed - booleans, integers and stripped text
        if name.startswith(Field_Prefix):
            value = alerts_tab.pre_process_alert_item(_alert_type, name, value)

        return value

# ################################################################################################################################

    def pre_process_input_dict(self, input_dict):
        input_dict['pool_size'] = int(input_dict['pool_size'])
        input_dict['security_id'] = extract_security_id(input_dict)

        # The form names the health check's unit in the singular, the scheduler in the plural
        if run_unit := input_dict.get(_health_check.Field_Run_Unit):
            input_dict[_health_check.Field_Run_Unit] = health_check_unit_to_scheduler[run_unit]

        # A duration is stored as seconds, which is what its count and unit join into
        alerts_tab.join_durations(_alert_type, input_dict)

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} HL7 FHIR outgoing connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'outgoing-hl7-fhir-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'outgoing-hl7-fhir-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'outgoing-hl7-fhir-delete'
    error_message = 'Could not delete HL7 FHIR outgoing connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def invoke(req, conn_id, max_wait_time, conn_name, conn_slug):

    return_data = {
        'conn_id': conn_id,
        'conn_name': conn_name,
        'conn_slug': conn_slug,
        'conn_type': GENERIC.CONNECTION.TYPE.OUTCONN_HL7_FHIR,
        'timeout': max_wait_time,
        'cluster_id': req.zato.cluster_id,
    }

    return TemplateResponse(req, 'zato/outgoing/hl7/fhir-invoke.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def invoke_action(req, conn_name):
    return invoke_action_handler(req, 'zato.generic.connection.invoke', ('conn_name', 'conn_type', 'request_data', 'timeout'))

# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.generic.connection.change-password', success_msg='Password updated')

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'HL7 FHIR connection')

# ################################################################################################################################
