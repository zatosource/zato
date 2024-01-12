# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.im.slack import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
     method_allowed, ping_connection
from zato.common.odb.model import GenericConn

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-im-slack'
    template = 'zato/outgoing/im/slack.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = GenericConn
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id', 'type_'
        output_required = 'id', 'name'
        output_optional = 'is_active', 'http_proxy_list', 'https_proxy_list'
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm()
        }

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'name',
        input_optional = 'is_active', 'http_proxy_list', 'https_proxy_list'
        output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_IM_SLACK
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True
        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['pool_size'] = 1

    def success_message(self, item):
        return 'Successfully {} outgoing Slack connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-im-slack-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-im-slack-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-im-slack-delete'
    error_message = 'Could not delete outgoing Slack connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.generic.connection.change-password', success_msg='Token updated')

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'Slack connection')

# ################################################################################################################################
