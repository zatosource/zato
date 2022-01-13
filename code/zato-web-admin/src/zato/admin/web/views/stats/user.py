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
        return value in members.values()

# ################################################################################################################################
# ################################################################################################################################

@unique
class Action(BaseEnum):
    Index = 'index'

action_to_service = {
    Action.Index.value: 'stats1.get-stat-types'
}

action_to_template = {
    Action.Index.value: 'zato/stats/user/index.html'
}

default_action = Action.Index.value # type: str

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'stats-user'
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_optional = 'action'
        output_repeated = True

    def on_after_set_input(self):
        action = self.input.get('action') or default_action

        if not Action.has_value(action):
            action = default_action

        self.ctx['service_name']  = action_to_service[action]
        self.ctx['template_name'] = action_to_template[action]

        return action_to_service[action]

# ################################################################################################################################

    def get_output_class(self) -> 'str':
        #from stats1 import StatsType
        #return StatsType
        from bunch import Bunch
        return Bunch

# ################################################################################################################################

    def get_service_name(self, req:'WSGIRequest') -> 'str':
        return self.ctx['service_name']

# ################################################################################################################################

    def get_template_name(self):
        return self.ctx['template_name']

# ################################################################################################################################

    def handle_return_data(self, return_data:'any_') -> 'any_':
        return return_data

# ################################################################################################################################
# ################################################################################################################################
