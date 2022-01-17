# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from enum import Enum, unique

# Bunch
from bunch import Bunch

# Zato
from zato.admin.web.views import Index as _Index
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.core.handlers.wsgi import WSGIRequest
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

form_item_id_prefix = 'item-id-'

# ################################################################################################################################
# ################################################################################################################################

class BaseEnum(Enum):

    @classmethod
    def has_value(cls:'any_', value:'str') -> 'bool':
        members = cast_('dict', cls.__members__)
        values = members.values()
        values = [elem.value for elem in values]
        return value in values

# ################################################################################################################################
# ################################################################################################################################

@unique
class Action(BaseEnum):
    Index   = 'Index'
    BrowseStats  = 'BrowseStats'
    DisplayStats = 'DisplayStats'
    CompareStats = 'CompareStats'

action_to_service = {
    Action.Index.value:   'stats.get-stat-types',
    Action.BrowseStats.value: 'stats.browse-stats',
    Action.DisplayStats.value: 'stats.browse-stats',
    Action.CompareStats.value: 'stats.browse-stats',
}

action_to_template = {
    Action.Index.value: 'zato/stats/user/index.html',
    Action.BrowseStats.value: 'zato/stats/user/browse-stats.html',
    Action.DisplayStats.value: 'zato/stats/user/browse-stats.html',
    Action.CompareStats.value: 'zato/stats/user/browse-stats.html',
}

default_action = Action.Index.value # type: str

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):

    method_allowed = 'GET'
    url_name = 'stats-user'
    paginate = True
    clear_self_items = False
    update_request_with_self_input = False
    extract_top_level_key_from_payload = False

    class SimpleIO(_Index.SimpleIO):
        input_optional = ('action',)
        output_repeated = True

    def before_invoke_admin_service(self):
        self.items = {
            'rows': [],
            'charts': [],
        }

# ################################################################################################################################

    def get_initial_input(self):
        out = {}
        query = {'id':[]}

        for key, value in self.req.GET.items():
            if key in {'action', 'cluster_id'}:
                continue
            else:
                if key.startswith(form_item_id_prefix):
                    data = key.split(form_item_id_prefix)
                    value = data[1]
                    query['id'].append(value)
                else:
                    query[key] = value

        out['query'] = query

        return out

# ################################################################################################################################

    def on_after_set_input(self):
        action = self.input.get('action')
        action = action or default_action

        if not Action.has_value(action):
            action = default_action

        self.ctx['action']        = action
        self.ctx['service_name']  = action_to_service[action]
        self.ctx['template_name'] = action_to_template[action]

        return action_to_service[action]

# ################################################################################################################################

    def get_output_class(self) -> 'any_':
        return Bunch

# ################################################################################################################################

    def get_service_name(self, _:'WSGIRequest') -> 'str':
        return self.ctx['service_name']

# ################################################################################################################################

    def get_template_name(self):
        return self.ctx['template_name']

# ################################################################################################################################

    def _handle_item(self, item:'any_') -> 'any_':
        return item

# ################################################################################################################################

    def handle_return_data(self, return_data:'any_') -> 'any_':

        dicts = self.req.zato.client.invoke('stats.get-dict-containers')

        columns = self.req.zato.client.invoke('stats.get-table-columns')
        columns = columns.data['columns']

        return_data['dicts']   = dicts.data
        return_data['columns'] = columns

        return_data['action'] = self.ctx['action']
        return_data['form_item_id_prefix'] = form_item_id_prefix

        return return_data

# ################################################################################################################################
# ################################################################################################################################
