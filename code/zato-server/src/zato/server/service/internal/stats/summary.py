# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

class BaseSummarizingService(AdminService):
    pass

class CreateSummaryByDay(AdminService):
    pass

class CreateSummaryByWeek(AdminService):
    pass

class CreateSummaryByMonth(AdminService):
    pass

class CreateSummaryByYear(AdminService):
    pass

class GetSummaryBase(AdminService):
    pass

class GetSummaryByDay(AdminService):
    pass

class GetSummaryByWeek(AdminService):
    pass

class GetSummaryByMonth(AdminService):
    pass

class GetSummaryByYear(AdminService):
    pass

class GetSummaryByRange(AdminService):
    pass

# ################################################################################################################################
# ################################################################################################################################
