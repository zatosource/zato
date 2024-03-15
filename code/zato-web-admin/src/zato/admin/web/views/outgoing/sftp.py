# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.common.api import GENERIC
from zato.common.json_internal import dumps
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.sftp import CommandShellForm, CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, ping_connection, slugify
from zato.common.odb.model import GenericConn

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

_sio_required = 'name', 'log_level'
_sio_optional = 'is_active', 'host', 'port', 'username', 'password', 'identity_file', \
    'ssh_config_file', 'buffer_size', 'is_compression_enabled', 'bandwidth_limit', 'force_ip_type', 'should_flush', \
    'should_preserve_meta', 'ssh_options', 'sftp_command', 'ping_command', 'default_directory'

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-sftp'
    template = 'zato/outgoing/sftp.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = GenericConn
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id', 'type_')
        output_required = ('id',) + _sio_required
        output_optional = _sio_optional
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(prefix='edit', req=self.req),
            'change_password_form': ChangePasswordForm()
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = _sio_required + _sio_optional
        output_required = ('id', 'name')

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_SFTP
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True
        initial_input_dict['pool_size'] = 1
        initial_input_dict['sec_use_rbac'] = False

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
            return HttpResponse(dumps({
                'msg': 'Response time: {} (#{})'.format(data.response_time, data.command_no),
                'stdout': data.get('stdout') or '(None)',
                'stderr': data.get('stderr') or '(None)',
            }), content_type='application/javascript')
        else:
            raise Exception(response.details)

    except Exception:
        msg = 'Caught an exception, e:`{}`'.format(format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)

# ################################################################################################################################
