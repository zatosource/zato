# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from enum import Enum, unique
from json import dumps, loads

# Bunch
from bunch import Bunch

# Django
from django.http import HttpResponse

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
item_id_list_param = 'id'

# ################################################################################################################################
# ################################################################################################################################

browse_service = 'stats.browse-stats'

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
    Action.Index.value:        'stats.get-stat-types',
    Action.BrowseStats.value:  browse_service,
    Action.DisplayStats.value: browse_service,
    Action.CompareStats.value: browse_service,
}

action_to_template = {
    Action.Index.value:        'zato/stats/user/index.html',
    Action.BrowseStats.value:  'zato/stats/user/browse.html',
    Action.DisplayStats.value: 'zato/stats/user/browse.html',
    Action.CompareStats.value: 'zato/stats/user/browse.html',
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

    class SimpleIO(_Index.SimpleIO):
        input_optional = ('action',)
        output_repeated = True

    def before_invoke_admin_service(self):
        self.items = {
            'items': [],
            'rows': [],
            'charts': [],
        }

# ################################################################################################################################

    def should_extract_top_level(self, _keys):
        return False

# ################################################################################################################################

    def handle_item_list(self, item_list, is_extracted):

        # We have a single list on input
        if is_extracted:
            self._handle_single_item_list(self.items, item_list)
        else:
            # Otherwise, it is a dictionary and we need to process each of its values.
            # The initial keys in the container (self.items) will be set but a view's
            # before_invoke_admin_service method.
            for key, value_list in (item_list or {}).items():
                container = self.items.get(key, [])
                self._handle_single_item_list(container, value_list)

# ################################################################################################################################

    def get_initial_input(self):

        out = {'id':[]}

        for key, value in self.req.GET.items():
            if key in {'action', 'cluster_id'}:
                continue
            else:
                if key.startswith(form_item_id_prefix):
                    data = key.split(form_item_id_prefix)
                    value = data[1]
                    out['id'].append(value)
                else:
                    out[key] = value

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

        # This is needed by a checkbox in each row to make the checkbox know whether it should be checked or not.
        id_checked = []
        for key in self.req.GET:
            if key.startswith(form_item_id_prefix):
                key = key.split(form_item_id_prefix)
                key
                value = key[1]
                id_checked.append(value)

        return_data['id_checked'] = id_checked

        return return_data

# ################################################################################################################################
# ################################################################################################################################

def get_updates(req):

    # Assume we do not return anything ..
    out = {}

    # .. unless we have some query parameters on input
    if req.body:
        data = loads(req.body)
        if item_id_list_param in data:
            response = req.zato.client.invoke(browse_service, {
                item_id_list_param: data[item_id_list_param],
                'needs_rows':False
            })
            out.update(response.data)

    out = dumps(out)
    return HttpResponse(out)

# ################################################################################################################################
# ################################################################################################################################
