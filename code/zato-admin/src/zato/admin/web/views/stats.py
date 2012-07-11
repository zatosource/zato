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
from zato.common import zato_path
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

def top_n(req, choice):
    labels = {'last_hour':'Last hour', 'today':'Today', 'yesterday':'Yesterday', 'last_24h':'Last 24h',
            'this_week':'This week', 'this_month':'This month', 'this_year':'This year'}
    
    compare_to = {
        'last_hour':[
            ('prev_hour', 'The previous hour'),
            ('prev_day', 'Same hour the previous day'),
            ('prev_day', 'Same hour and day the previous week'),
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
    slowest, most_used = [], []
    now = datetime.utcnow()
        
    if req.zato.get('cluster'):
        
        def _get_stats(start, stop, granularity, time_elems, stat_type, append_to):
            zato_message, _  = invoke_admin_service(req.zato.cluster, 'zato:stats.get-top-n',
                {'start':start, 'stop':stop, 'granularity':granularity, 'n':n, 
                'trend_elems':trend_elems, 'stat_type':stat_type})
            
            if zato_path('response.item_list.item').get_from(zato_message) is not None:
                for msg_item in zato_message.response.item_list.item:
                    append_to.append({'position':msg_item.position.text, 'service_name':msg_item.service_name.text, 
                                     'value':int(float(msg_item.value.text)), 'trend':msg_item.trend.text})
        
        def _params_last_hour():
            trend_elems = 60
            start = now+relativedelta(minutes=-trend_elems)
            return start.isoformat(), now.isoformat(), (now-start).seconds, 'minutes', trend_elems
            
        start, stop, seconds, granularity, trend_elems = locals()['_params_' + choice]()

        # Collect basic stats
        _get_stats(start, stop, granularity, trend_elems, 'highest_mean', slowest)
        _get_stats(start, stop, granularity, trend_elems, 'highest_usage', most_used)
        
        for item in most_used:
            rate = item['value']/seconds
            item['rate'] = '{:.2f}'.format(rate) if rate > 0.01 else '<0.01'
        
    return_data = {
        'start': start,
        'stop': stop,
        'label': labels[choice], 
        'n_form': NForm(initial={'n':n}),
        'compare_form': CompareForm(compare_to=compare_to[choice]),
        'slowest':slowest,
        'most_used':most_used,
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'choose_cluster_form':req.zato.choose_cluster_form,
    }
    
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [{}]'.format(str(return_data)))

    return render_to_response('zato/stats/top-n.html', return_data, context_instance=RequestContext(req))


