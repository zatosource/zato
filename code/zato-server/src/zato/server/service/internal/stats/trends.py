# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service import Integer
from zato.server.service.internal.stats import StatsReturningService

class GetTrends(StatsReturningService):
    """ Returns top N slowest or most commonly used services for a given period
    along with their trends.
    """
    class SimpleIO(StatsReturningService.SimpleIO):
        request_elem = 'zato_stats_get_trends_request'
        response_elem = 'zato_stats_get_trends_response'
        input_required = StatsReturningService.SimpleIO.input_required + (Integer('n'), 'n_type')
        input_optional = ('service_name',)

    def handle(self):
        self.response.payload[:] = (elem.to_dict() for elem in self.get_stats(self.request.input.start,
            self.request.input.stop, n=int(self.request.input.n), n_type=self.request.input.n_type))
