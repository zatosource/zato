# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import dumps

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.llm import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
     method_allowed, ping_connection, SKIP_VALUE
from zato.common.api import GENERIC, LLM
from zato.common.llm_models import model_list

# Bunch
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Catalog models in their published order for the dashboard's model select
_catalog_models = []

for _model in model_list:
    _catalog_models.append({'name': _model['name'], 'id': _model['id'], 'provider': _model['provider']})

# Maps each provider to its API's base URL so the address can follow the model select
_provider_address = {
    LLM.PROVIDER.CLAUDE.id: LLM.ADDRESS.CLAUDE,
    LLM.PROVIDER.OPENAI.id: LLM.ADDRESS.OPENAI,
    LLM.PROVIDER.GEMINI.id: LLM.ADDRESS.GEMINI,
}

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
    output_optional = ('address', 'model', 'pool_size', 'timeout', 'max_tokens', 'max_history_turns', 'chat_expiry')
    output_repeated = True

    def handle(self):
        return {
            'show_search_form': True,
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm(),
            'llm_models_json': dumps(_catalog_models),
            'llm_addresses_json': dumps(_provider_address),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'address', 'model'
    input_optional = ('is_active', 'pool_size', 'timeout', 'max_tokens', 'max_history_turns', 'chat_expiry', 'secret')
    output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.OUTCONN_LLM
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True

    def pre_process_item(self, name, value):
        # The key is empty when a self-hosted endpoint needs none and on the edit path,
        # which has no key field at all - either way there is nothing to send to the backend.
        if name == 'secret' and not value:
            return SKIP_VALUE
        return value

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
