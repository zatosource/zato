# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service.internal import AdminService
from zato.server.worker_list import get_worker_list

# ################################################################################################################################
# ################################################################################################################################

_service_name_prefix = 'zato.server.worker.'

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns the process ID, the generation, the state, the heartbeat age, the number of owned subscription keys
    and the singleton flag of the worker of each slot.
    """
    name = _service_name_prefix + 'get-list'

    def handle(self) -> 'None':
        self.response.payload = {
            'items': get_worker_list(),
        }

# ################################################################################################################################
# ################################################################################################################################
