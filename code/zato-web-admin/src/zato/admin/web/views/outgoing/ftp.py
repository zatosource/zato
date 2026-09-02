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
from zato.admin.web.forms.outgoing.ftp import CommandShellForm, CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, ping_connection, \
     SKIP_VALUE, slugify
from zato.common.api import GENERIC
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

_fields_required = ('name',)
_fields_optional = 'is_active', 'host', 'port', 'username', 'use_ssl', 'should_store_content'

# The connection's fields that a checkbox stands for, which is what turns their input into a boolean.
_fields_checkbox = 'use_ssl', 'should_store_content'

# What the command shell shows in an output pane that the command left empty.
Command_Shell_Empty_Output = '(None)'

# What the command shell shows instead of a response time when the command never got as far as being timed.
Command_Shell_No_Response_Time = 'n/a'

# What the command shell says when the commands ran but did not succeed.
Command_Shell_Error_Message = 'Command failed, see stderr'

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-ftp'
    template = 'zato/outgoing/ftp.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = ('id',) + _fields_required
    output_optional = _fields_optional
    output_repeated = True

    def handle(self) -> 'stranydict':
        out = {
            'show_search_form': True,
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(prefix='edit', req=self.req),
        }
        return out

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = _fields_required
    input_optional = _fields_optional + ('secret',)
    output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict:'stranydict') -> 'None':
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_FTP
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True
        initial_input_dict['pool_size'] = 1

    def pre_process_item(self, name:'str', value:'any_') -> 'any_':

        # An empty password on input means the current one is to be kept.
        if name == 'secret':
            if not value:
                return SKIP_VALUE

        # The checkbox arrives as 'on' when it is checked and as an empty value otherwise.
        elif name in _fields_checkbox:
            value = value == 'on'

        return value

    def post_process_return_data(self, return_data:'stranydict') -> 'stranydict':
        # The Schedules link of a newly added row needs the connection's name in its URL form.
        return_data['name_slug'] = slugify(return_data['name'])
        return return_data

    def success_message(self, item:'any_') -> 'str':
        out = f'Successfully {self.verb} outgoing FTP connection `{item.name}`'
        return out

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-ftp-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-ftp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-ftp-delete'
    error_message = 'Could not delete outgoing FTP connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################

@method_allowed('POST')
def ping(req:'any_', id:'str', cluster_id:'str') -> 'any_':
    out = ping_connection(req, 'zato.generic.connection.ping', id, 'FTP connection')
    return out

# ################################################################################################################################

@method_allowed('GET')
def command_shell(req:'any_', id:'str', cluster_id:'str', name_slug:'str') -> 'TemplateResponse':

    # Every outgoing FTP connection there is ..
    response = req.zato.client.invoke('zato.generic.connection.get-list', {
        'cluster_id': req.zato.cluster_id,
        'type_': GENERIC.CONNECTION.TYPE.OUTCONN_FTP,
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
        item_url = reverse('out-ftp-command-shell', args=[item_id, cluster_id, item_slug])
        item_name_encoded = quote(item_name)
        connection_list.append({
            'name': item_name,
            'url': f'{item_url}?name={item_name_encoded}',
        })

    return_data = {
        'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
        'req': req,
        'conn_id': id,
        'name_slug': name_slug,
        'conn_name': req.GET['name'],
        'connection_list': connection_list,
        'form':CommandShellForm(),
        }

    out = TemplateResponse(req, 'zato/outgoing/ftp-command-shell.html', return_data)
    return out

# ################################################################################################################################

@method_allowed('POST')
def command_shell_action(req:'any_', id:'str', cluster_id:'str', name_slug:'str') -> 'any_':

    try:
        response = req.zato.client.invoke('zato.outgoing.ftp.execute', {
            'cluster_id': req.zato.cluster_id,
            'id': id,
            'data': req.POST['data'],
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

            payload = dumps({
                'is_ok': is_ok,
                'error_message': Command_Shell_Error_Message,
                'response_time': response_time,
                'command_no': data.command_no,
                'stdout': stdout,
                'stderr': stderr,
            })

            out = HttpResponse(payload, content_type='application/javascript')
            return out
        else:
            raise Exception(response.details)

    except Exception as e:
        exc = format_exc()
        logger.error('Caught an exception, e:`%s`', exc)

        error_text = str(e)
        error_bytes = error_text.encode('utf8')

        out = HttpResponseServerError(error_bytes)
        return out

# ################################################################################################################################
# ################################################################################################################################
