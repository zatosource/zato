# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.admin.web import alerts_tab
from zato.admin.web.forms.outgoing.smb import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, ping_connection, slugify, \
     SKIP_VALUE
from zato.admin.web.views.outgoing.file_transfer_schedule import get_connection_last_run_list, get_schedules, \
     get_schedules_by_conn_id, set_connection_last_run
from zato.common.api import FileTransfer, GENERIC

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################

# The alert settings of the connection follow the file transfer type
_alert_type = alerts_tab.alert_type_file_transfer

_fields_required = ('name',)
_fields_optional = ('is_active', 'host', 'port', 'username', 'should_store_content', 'verify_how') + \
    alerts_tab.get_storage_field_names(_alert_type)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-smb'
    template = 'zato/outgoing/smb.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = ('id',) + _fields_required
    output_optional = _fields_optional + (FileTransfer.Scheduler.Schedules_Field,)
    output_repeated = True

    def on_before_append_item(self, item:'any_') -> 'any_':
        schedules = get_schedules(item)
        item.scheduler_schedule_count = len(schedules)

        # The edit form shows a duration as a count with a unit, not as the seconds it is stored as
        alerts_tab.split_durations(_alert_type, item)

        return item

    def handle_return_data(self, return_data:'stranydict') -> 'stranydict':
        set_connection_last_run(self.req, self.items)
        return return_data

    def handle(self):
        create_form = CreateForm(req=self.req)
        edit_form = EditForm(prefix='edit', req=self.req)

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

    input_required = _fields_required
    input_optional = _fields_optional + ('secret',)
    output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_SMB
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True
        initial_input_dict['pool_size'] = 1

    def pre_process_item(self, name, value):
        # An empty password on input means the current one is to be kept,
        # which is why the field cannot be sent to the backend at all.
        if name == 'secret' and not value:
            return SKIP_VALUE

        # The Alerts tab's fields arrive as text and are stored typed - booleans and integers
        if name.startswith(alerts_tab.Field_Prefix):
            value = alerts_tab.pre_process_alert_item(_alert_type, name, value)

        return value

    def pre_process_input_dict(self, input_dict:'stranydict') -> 'None':

        # A duration is stored as seconds, which is what its count and unit join into
        alerts_tab.join_durations(_alert_type, input_dict)

    def post_process_return_data(self, return_data:'stranydict') -> 'stranydict':
        # The Scheduler link of a newly added row needs the connection's name in its URL form.
        return_data['name_slug'] = slugify(return_data['name'])
        schedules = get_schedules_by_conn_id(self.req, return_data['id'])
        return_data['scheduler_schedule_count'] = len(schedules)

        last_run_list = get_connection_last_run_list(self.req, [schedules])
        last_run = last_run_list[0]
        return_data.update(last_run)

        return return_data

    def success_message(self, item):
        return 'Successfully {} outgoing SMB connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-smb-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-smb-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-smb-delete'
    error_message = 'Could not delete outgoing SMB connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'SMB connection')

# ################################################################################################################################
