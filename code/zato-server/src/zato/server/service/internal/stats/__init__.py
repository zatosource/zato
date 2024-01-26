# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

class _Abstract:
    def handle(self):
        pass

class Delete(_Abstract, AdminService):
    pass

class ProcessRawTimes(_Abstract, AdminService):
    pass

class AggregateByMinute(_Abstract, AdminService):
    pass

class AggregateByHour(_Abstract, AdminService):
    pass

class AggregateByDay(_Abstract, AdminService):
    pass

class AggregateByMonth(_Abstract, AdminService):
    pass

class StatsReturningService(_Abstract, AdminService):
    pass

class GetByService(_Abstract, AdminService):
    pass

# ################################################################################################################################
# ################################################################################################################################
