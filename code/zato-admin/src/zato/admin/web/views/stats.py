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

# stdlib
from datetime import datetime, timedelta

def top_n(req, choice):
    choices = ('last_hour', 'today', 'yesterday', 'last_24h', 'this_week', 'this_month', 'this_year')
    if not choice in choices:
        raise ValueError('choice:[{}] is not one of:[{}]'.format(choice, choices))
        
    n = req.GET.get('n', 10)
    now = datetime.utcnow()
    
    def _params_last_hour():
        return now - timedelta(minutes=60), now, 'minute'
        
    start, stop, granularity = locals()['_params_' + choice]()
    
    print(333, start, stop, granularity)
    
    #start_stop['last-hour'].append(now() - timedelta(seconds=60), now)    


