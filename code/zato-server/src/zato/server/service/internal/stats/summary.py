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

class BaseSummarizingService(_Abstract, AdminService):
    pass

class CreateSummaryByDay(_Abstract, AdminService):
    pass

class CreateSummaryByWeek(_Abstract, AdminService):
    pass

class CreateSummaryByMonth(_Abstract, AdminService):
    pass

class CreateSummaryByYear(_Abstract, AdminService):
    pass

class GetSummaryBase(_Abstract, AdminService):
    pass

class GetSummaryByDay(_Abstract, AdminService):
    pass

class GetSummaryByWeek(_Abstract, AdminService):
    pass

class GetSummaryByMonth(_Abstract, AdminService):
    pass

class GetSummaryByYear(_Abstract, AdminService):
    pass

class GetSummaryByRange(_Abstract, AdminService):
    pass

# ################################################################################################################################
# ################################################################################################################################
