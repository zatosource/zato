# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from enum import Enum, unique
import logging

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
    Action.DisplayStats.value: 'zato/stats/user/display-stats.html',
    Action.CompareStats.value: 'zato/stats/user/compare-stats.html',
}

default_action = Action.Index.value # type: str

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'stats-user'
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_optional = ('action',)
        output_repeated = True

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
        from bunch import Bunch
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
        response = self.req.zato.client.invoke('stats.get-dict-containers')
        return_data['dicts'] = response.data
        return return_data

# ################################################################################################################################
# ################################################################################################################################
