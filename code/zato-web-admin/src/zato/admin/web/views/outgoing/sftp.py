# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from traceback import format_exc

# Bunch
from zato.common.ext.bunch import Bunch

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms.outgoing.sftp import CommandShellForm, CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, ping_connection, slugify, \
     SKIP_VALUE
from zato.common.api import GENERIC
from zato.common.json_internal import dumps

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

_fields_required = ('name',)
_fields_optional = 'is_active', 'address', 'username', 'private_key', 'strict_host_key_checking'

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
    output_optional = _fields_optional
    output_repeated = True

    def handle(self):
        return {
            'show_search_form': True,
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(prefix='edit', req=self.req),
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

        # The checkbox arrives as 'on' when it is checked and as an empty value otherwise
        elif name == 'strict_host_key_checking':
            value = value == 'on'

        return value

    def post_process_return_data(self, return_data):
        return_data['name_slug'] = slugify(return_data['name'])
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
def command_shell(req, id, cluster_id, name_slug):

    return_data = {
        'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
        'req': req,
        'conn_id': id,
        'name_slug': name_slug,
        'conn_name': req.GET['name'],
        'form':CommandShellForm(),
        }

    return TemplateResponse(req, 'zato/outgoing/sftp-command-shell.html', return_data)

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

            stdout = data.get('stdout')
            if not stdout:
                stdout = '(None)'

            stderr = data.get('stderr')
            if not stderr:
                stderr = '(None)'

            return HttpResponse(dumps({
                'msg': 'Response time: {} (#{})'.format(data.response_time, data.command_no),
                'stdout': stdout,
                'stderr': stderr,
            }), content_type='application/javascript')
        else:
            raise Exception(response.details)

    except Exception:
        msg = 'Caught an exception, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
