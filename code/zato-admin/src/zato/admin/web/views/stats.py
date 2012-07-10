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
import logging
from datetime import datetime

# dateutil
from dateutil.relativedelta import relativedelta

# Django
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import loader, RequestContext

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms.stats import CompareForm, NForm
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

def top_n(req, choice):
    labels = {'last_hour':'Last hour', 'today':'Today', 'yesterday':'Yesterday', 'last_24h':'Last 24h',
            'this_week':'This week', 'this_month':'This month', 'this_year':'This year'}
    
    compare_to = {
        'last_hour':[
            ('prev_hour', 'The previous hour'),
            ('prev_day', 'Same hour the previous day'),
            ('prev_day', 'Same hour of day the previous week'),
        ], 

        'today':[('', '')], 
        'yesterday':[('', '')], 
        'last_24h':[('', '')],
        'this_week':[('', '')], 
        'this_month':[('', '')], 
        'this_year':[('', '')]
    }
    
    if not choice in labels:
        raise ValueError('choice:[{}] is not one of:[{}]'.format(choice, labels.keys()))
        
    start, stop = '', ''
    n = req.GET.get('n', 10)
    now = datetime.utcnow()
        
    if req.zato.get('cluster'):
        
        def _params_last_hour():
            return (now+relativedelta(hours=-1)).isoformat(), now.isoformat(), 'minute'
            
        start, stop, granularity = locals()['_params_' + choice]()
        
        zato_message, _  = invoke_admin_service(req.zato.cluster, 'zato:stats.get-top-n',
            {'start':start, 'stop':stop, 'granularity':granularity, 'n':n, 'stat_type':'highest_mean'})
    
    return_data = {
        'start': start,
        'stop': stop,
        'label': labels[choice], 
        'n_form': NForm(initial={'n':n}),
        'compare_form': CompareForm(compare_to=compare_to[choice]),
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'choose_cluster_form':req.zato.choose_cluster_form,
    }
    
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [{}]'.format(str(return_data)))

    return render_to_response('zato/stats/top-n.html', return_data, context_instance=RequestContext(req))


