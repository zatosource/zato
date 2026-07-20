# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.llm import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
     method_allowed, ping_connection
from zato.common.api import GENERIC, LLM

# Bunch
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Maps provider ids to the names the data table displays
_provider_display = {}

for _provider in LLM.PROVIDER():
    _provider_display[_provider.id] = _provider.name

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-llm'
    template = 'zato/outgoing/llm.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active'
    output_optional = ('provider', 'address', 'model', 'pool_size', 'timeout', 'max_tokens', 'max_history_turns', 'chat_expiry')
    output_repeated = True

    def on_before_append_item(self, item:'any_') -> 'any_':
        item.provider_display = _provider_display[item.provider]
        return item

    def handle(self):
        return {
            'show_search_form': True,
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm()
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'provider', 'address', 'model'
    input_optional = ('is_active', 'pool_size', 'timeout', 'max_tokens', 'max_history_turns', 'chat_expiry')
    output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_LLM
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True

    def success_message(self, item):
        return 'Successfully {} outgoing LLM connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-llm-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-llm-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-llm-delete'
    error_message = 'Could not delete outgoing LLM connection'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.generic.connection.change-password')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id):
    return ping_connection(req, 'zato.generic.connection.ping', id, 'LLM connection')

# ################################################################################################################################
# ################################################################################################################################
