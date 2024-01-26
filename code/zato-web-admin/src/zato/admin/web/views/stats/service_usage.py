# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.admin.web.views import Index as _Index

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class StatsItem:
    pass

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'stats-service-usage'
    template = 'zato/stats/service-usage.html'
    service_name = 'zato.service.get-stats-table'
    output_class = StatsItem
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        output_optional = ('name', 'item_mean', 'item_max', 'item_min', 'item_time_share', \
            'item_usage_share', 'item_total_usage', 'item_total_time', 'item_total_usage_human',
            'item_total_time_human')
        output_repeated = True

    def handle(self):
        return {}

# ################################################################################################################################
# ################################################################################################################################
