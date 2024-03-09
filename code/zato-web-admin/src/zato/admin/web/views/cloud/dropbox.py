# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.cloud.dropbox import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
     method_allowed, ping_connection, slugify
from zato.common.odb.model import GenericConn

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

_sio_required = 'name',
_sio_optional = 'is_active', 'max_retries_on_error', 'max_retries_on_rate_limit', 'timeout', 'oauth2_access_token_expiration', \
    'oauth2_access_token', 'default_directory', 'default_scope', 'user_agent', 'http_headers'

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'cloud-dropbox'
    template = 'zato/cloud/dropbox.html'
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
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CLOUD_DROPBOX
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True
        initial_input_dict['pool_size'] = 10
        initial_input_dict['sec_use_rbac'] = False

    def post_process_return_data(self, return_data):
        return_data['name_slug'] = slugify(return_data['name'])
        return return_data

    def success_message(self, item):
        return 'Successfully {} Dropbox connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'cloud-dropbox-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'cloud-dropbox-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'cloud-dropbox-delete'
    error_message = 'Could not delete Dropbox connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.generic.connection.change-password', success_msg='Token updated')

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'Dropbox connection')

# ################################################################################################################################
