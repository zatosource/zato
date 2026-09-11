# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from traceback import format_exc
from urllib.parse import quote

# Bunch
from zato.common.ext.bunch import Bunch

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse
from django.urls import reverse

# Zato
from zato.admin.web import alerts_tab
from zato.admin.web.forms.outgoing.sftp import CommandShellForm, CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, ping_connection, slugify, \
     SKIP_VALUE
from zato.admin.web.views.outgoing.file_transfer_schedule import get_connection_command_shell_url, \
     get_connection_last_run_list, get_schedules, get_schedules_by_conn_id, set_connection_last_run
from zato.common.api import FileTransfer, GENERIC
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictlist, stranydict
    any_ = any_
    dictlist = dictlist
    stranydict = stranydict

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

# The alert settings of the connection follow the file transfer type
_alert_type = alerts_tab.alert_type_file_transfer

_fields_required = ('name',)
_fields_optional = ('is_active', 'address', 'username', 'private_key', 'strict_host_key_checking', \
    'ignore_host_key_changes', 'should_store_content', 'verify_how') + alerts_tab.get_storage_field_names(_alert_type)

# The connection's fields that a checkbox stands for, which is what turns their input into a boolean
_fields_checkbox = ('strict_host_key_checking', 'ignore_host_key_changes', 'should_store_content') + \
    alerts_tab.get_checkbox_field_names(_alert_type)

# How the schedule pages know this transfer type
_transfer_type = 'sftp'

# What the command shell shows in an output pane that the command left empty
Command_Shell_Empty_Output = '(None)'

# What the command shell shows instead of a response time when the command never got as far as being timed
Command_Shell_No_Response_Time = 'n/a'

# What the command shell says when the commands ran but did not succeed
Command_Shell_Error_Message = 'Command failed, see stderr'

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-sftp'
    template = 'zato/outgoing/sftp.html'
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
        item.command_shell_url = get_connection_command_shell_url(
            self.req, _transfer_type, item.id, item.name, schedules)

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
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_SFTP
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True
        initial_input_dict['pool_size'] = 1

    def pre_process_item(self, name, value):

        # An empty password on input means the current one is to be kept,
        # which is why the field cannot be sent to the backend at all.
        if name == 'secret':
            if not value:
                return SKIP_VALUE

        # The Alerts tab's fields arrive as text and are stored typed - booleans and integers
        elif name.startswith(alerts_tab.Field_Prefix):
            value = alerts_tab.pre_process_alert_item(_alert_type, name, value)

        # The checkbox arrives as 'on' when it is checked and as an empty value otherwise
        elif name in _fields_checkbox:
            value = value == 'on'

        return value

    def pre_process_input_dict(self, input_dict:'stranydict') -> 'None':

        # A duration is stored as seconds, which is what its count and unit join into
        alerts_tab.join_durations(_alert_type, input_dict)

    def post_process_return_data(self, return_data:'stranydict') -> 'stranydict':
        return_data['name_slug'] = slugify(return_data['name'])
        schedules = get_schedules_by_conn_id(self.req, return_data['id'])
        return_data['scheduler_schedule_count'] = len(schedules)
        return_data['command_shell_url'] = get_connection_command_shell_url(
            self.req, _transfer_type, return_data['id'], return_data['name'], schedules)

        last_run_list = get_connection_last_run_list(self.req, [schedules])
        last_run = last_run_list[0]
        return_data.update(last_run)

        return return_data

    def success_message(self, item):
        return 'Successfully {} outgoing SFTP connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-sftp-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-sftp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-sftp-delete'
    error_message = 'Could not delete outgoing SFTP connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'SFTP connection')

# ################################################################################################################################

@method_allowed('GET')
def command_shell(req:'any_', id:'str', cluster_id:'str', name_slug:'str') -> 'TemplateResponse':

    # Every outgoing SFTP connection there is ..
    response = req.zato.client.invoke('zato.generic.connection.get-list', {
        'cluster_id': req.zato.cluster_id,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_SFTP,
        'paginate': False,
    })

    if not response.ok:
        raise Exception(response.details)

    # .. each pointing to its own command shell, which is what the page's select navigates to.
    connection_list:'dictlist' = []

    for item in response.data:
        item_id = item['id']
        item_name = item['name']
        item_slug = slugify(item_name)
        item_url = reverse('out-sftp-command-shell', args=[item_id, cluster_id, item_slug])
        item_name_encoded = quote(item_name)
        connection_list.append({
            'name': item_name,
            'url': f'{item_url}?name={item_name_encoded}',
        })

    # A link into the shell, e.g. from a schedule, may say what command to start with.
    if command := req.GET.get('command'):
        form = CommandShellForm(initial_command=command)
    else:
        form = CommandShellForm()

    return_data = {
        'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
        'req': req,
        'conn_id': id,
        'name_slug': name_slug,
        'conn_name': req.GET['name'],
        'connection_list': connection_list,
        'form': form,
        }

    out = TemplateResponse(req, 'zato/outgoing/sftp-command-shell.html', return_data)
    return out

# ################################################################################################################################

@method_allowed('POST')
def command_shell_action(req, id, cluster_id, name_slug):

    try:
        response = req.zato.client.invoke('zato.outgoing.sftp.execute', {
            'cluster_id': req.zato.cluster_id,
            'id': id,
            'data': req.POST['data'],
            'log_level': req.POST['log_level'],
        })

        if response.ok:
            data = response.data

            # Everything below is optional on the service's output, which means that a command
            # that produced nothing, or that never ran at all, leaves the field out of the payload.

            is_ok = data.get('is_ok')
            if is_ok is None:
                is_ok = False

            stdout = data.get('stdout')
            if not stdout:
                stdout = Command_Shell_Empty_Output

            stderr = data.get('stderr')
            if not stderr:
                stderr = Command_Shell_Empty_Output

            response_time = data.get('response_time')
            if not response_time:
                response_time = Command_Shell_No_Response_Time

            return HttpResponse(dumps({
                'is_ok': is_ok,
                'error_message': Command_Shell_Error_Message,
                'response_time': response_time,
                'command_no': data.command_no,
                'stdout': stdout,
                'stderr': stderr,
            }), content_type='application/javascript')
        else:
            raise Exception(response.details)

    except Exception as e:

        # The traceback belongs in the log, whereas the browser only ever shows what went wrong,
        # because the command shell puts this text straight into its output pane.
        logger.error('Caught an exception, e:`%s`', format_exc())
        return HttpResponseServerError(str(e).encode('utf8'))

# ################################################################################################################################
# ################################################################################################################################
