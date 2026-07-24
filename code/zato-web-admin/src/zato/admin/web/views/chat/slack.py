# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http import HTTPStatus
from json import loads

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.chat.slack import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
    method_allowed, ping_connection
from zato.common.api import GENERIC, generic_attrs
from zato.common.model.slack import SlackConfigObject

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'chat-slack'
    template = 'zato/chat/slack.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = SlackConfigObject
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active'
    output_optional = generic_attrs
    output_repeated = True

# ################################################################################################################################

    def handle(self):
        return {
            'show_search_form': True,
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm(),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'is_active'
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CHAT_SLACK
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outgoing'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['recv_timeout'] = 250
        initial_input_dict['pool_size'] = 20

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} Slack connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'chat-slack-create'
    service_name = 'zato.generic.connection.create'

    def __call__(self, req, *args, **kwargs):

        # The token from the create form is stored in a follow-up call.
        response = super().__call__(req, *args, **kwargs)

        if response.status_code == HTTPStatus.OK:
            data = loads(response.content)
            token = req.POST.get('token', '')

            if token:
                _ = req.zato.client.invoke('zato.generic.connection.change-password', {
                    'id': data['id'],
                    'password': token,
                    'type_': GENERIC.CONNECTION.TYPE.CHAT_SLACK,
                })

        return response

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'chat-slack-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'chat-slack-delete'
    error_message = 'Could not delete Slack connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    out = _change_password(req, 'zato.generic.connection.change-password', success_msg='Token updated')
    return out

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    out = ping_connection(req, 'zato.generic.connection.ping', id, 'Slack connection')
    return out

# ################################################################################################################################
# ################################################################################################################################
