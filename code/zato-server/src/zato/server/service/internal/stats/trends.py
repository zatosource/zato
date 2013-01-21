# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
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

    def handle(self):
        self.response.payload[:] = (elem.to_dict() for elem in self.get_stats(self.request.input.start, 
            self.request.input.stop, n=int(self.request.input.n), n_type=self.request.input.n_type))
