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
from copy import deepcopy
from datetime import datetime

# dateutil
from dateutil.relativedelta import relativedelta

# Django
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.template import loader, RequestContext

# django-settings
from django_settings.models import PositiveInteger, Setting

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms.stats import CompareForm, MaintenanceForm, NForm, SettingsForm
from zato.admin.web.views import meth_allowed
from zato.common import DEFAULT_STATS_SETTINGS, StatsElem, zato_path
from zato.common.util import TRACE1

logger = logging.getLogger(__name__)

# 
# per_minute_aggr

class JobAttrForm(object):
    def __init__(self, form_name, job_attr):
        self.form_name = form_name
        self.job_attr = job_attr
        
    def __repr__(self):
        return '<{} at {} form_name:[{}], job_attr:[{}]>'.format(self.__class__.__name__, hex(id(self)),
            self.form_name, repr(self.job_attr))

class JobAttrFormMapping(object):
    def __init__(self, job_name, attrs):
        self.job_name = job_name
        self.attrs = attrs
        
    def __repr__(self):
        return '<{} at {} job_name:[{}], attrs:[{}]>'.format(self.__class__.__name__, hex(id(self)),
            self.job_name, repr(self.attrs))

# A mapping a job type, its name and the execution interval unit
job_mappings = {
    JobAttrFormMapping('zato.stats.ProcessRawTimes', [JobAttrForm('raw_times', 'seconds'),  JobAttrForm('raw_times_batch', {'extra':'max_batch_size'})]),
    JobAttrFormMapping('zato.stats.AggregateByMinute', [JobAttrForm('per_minute_aggr', 'seconds')]),
    }

@meth_allowed('GET')
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
        
        def _get_stats(start, stop, n_type, append_to):
            zato_message, _  = invoke_admin_service(req.zato.cluster, 'zato:stats.get-top-n',
                {'start':start, 'stop':stop, 'n':n, 'n_type':n_type})
            
            if zato_path('response.item_list.item').get_from(zato_message) is not None:
                for msg_item in zato_message.response.item_list.item:
                    append_to.append(StatsElem.from_xml(msg_item))
        
        def _params_last_hour():
            trend_elems = 60
            start = now+relativedelta(minutes=-trend_elems)
            return start.isoformat(), now.isoformat()
            
        start, stop = locals()['_params_' + choice]()

        # Collect basic stats
        _get_stats(start, stop, 'mean', slowest)
        _get_stats(start, stop, 'usage', most_used)
        
        #for item in most_used:
        #    rate = item['value']/seconds
        #    item['rate'] = '{:.2f}'.format(rate) if rate > 0.01 else '<0.01'
        #    item['percent'] = float(item['value'] / item['total']) * 100
        
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

    for name in('atttention_slow_threshold', 'atttention_top_threshold'):
        return_data[name] = Setting.objects.get_value(name, default=DEFAULT_STATS_SETTINGS[name])
    
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [{}]'.format(str(return_data)))

    return render_to_response('zato/stats/top-n.html', return_data, context_instance=RequestContext(req))


@meth_allowed('GET')
def settings(req):
    
    if req.zato.get('cluster'):
        
        _settings = {}
        defaults = deepcopy(DEFAULT_STATS_SETTINGS)
        
        for mapping in job_mappings:

            zato_message, _  = invoke_admin_service(req.zato.cluster, 'zato:scheduler.job.get-by-name', {'name': mapping.job_name})
            if zato_path('response.item').get_from(zato_message) is not None:
                item = zato_message.response.item
            
                for attr in mapping.attrs:
                    try:
                        attr.job_attr['extra']
                    except TypeError:
                        setting_base_name = 'scheduler_{}_interval'.format(attr.form_name)
                        setting_unit_name = 'scheduler_{}_interval_unit'.format(attr.form_name)
                        
                        defaults[setting_unit_name] = attr.job_attr
                        _settings[setting_base_name] = getattr(zato_message.response.item, attr.job_attr).text
                    else:
                        # A sample item.extra.text is 'max_batch_size=123456'
                        _settings['scheduler_{}'.format(attr.form_name)] = item.extra.text.split('=')[1]

        for name in DEFAULT_STATS_SETTINGS:
            if not name.startswith('scheduler'):
                _settings[name] = Setting.objects.get_value(name, default=DEFAULT_STATS_SETTINGS[name])
    else:
        form, defaults, _settings = None, None, {}

    return_data = {
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'choose_cluster_form':req.zato.choose_cluster_form,
        'form': SettingsForm(initial=_settings),
        'defaults':defaults,
    }

    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [{}]'.format(str(return_data)))

    return render_to_response('zato/stats/settings.html', return_data, context_instance=RequestContext(req))

@meth_allowed('POST')
def settings_save(req):
    
    for name in DEFAULT_STATS_SETTINGS:
        if not name.startswith('scheduler'):
            value = req.POST[name]
            Setting.objects.set_value(name, PositiveInteger, value)

    for mapping in job_mappings:

        zato_message, _  = invoke_admin_service(req.zato.cluster, 'zato:scheduler.job.get-by-name', {'name': mapping.job_name})
        if zato_path('response.item').get_from(zato_message) is not None:
            item = zato_message.response.item
            
            # Gotta love dictionary comprehensions!
            params = {attr: getattr(item, attr).text for attr in('id', 'name', 'is_active', 'job_type', 'start_date', 'extra')}
        
            for attr in mapping.attrs:
                
                try:
                    attr.job_attr['extra']
                except TypeError:
                    key = attr.job_attr
                    value = req.POST['scheduler_{}_interval'.format(attr.form_name)]
                else:
                    key = 'extra'
                    value = '{}={}'.format(attr.job_attr['extra'], req.POST['scheduler_{}'.format(attr.form_name)])
                    
                params[key] = value
                
            params['service'] = item.service_name.text
            params['cluster_id'] = req.zato.cluster.id
                
            invoke_admin_service(req.zato.cluster, 'zato:scheduler.job.edit', params)

    msg = 'Settings saved'
    messages.add_message(req, messages.INFO, msg, extra_tags='success')
        
    return redirect('{}?cluster={}'.format(reverse('stats-settings'), req.zato.cluster_id))

@meth_allowed('GET')
def maintenance(req):
    return_data = {
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'choose_cluster_form':req.zato.choose_cluster_form,
        'form': MaintenanceForm()
    }
    if logger.isEnabledFor(TRACE1):
        logger.log(TRACE1, 'Returning render_to_response [{}]'.format(str(return_data)))

    return render_to_response('zato/stats/maintenance.html', return_data, context_instance=RequestContext(req))

@meth_allowed('POST')
def maintenance_delete(req):
    start = req.POST['start']
    stop = req.POST['stop']
    
    invoke_admin_service(req.zato.cluster, 'zato:stats.delete', {'start':start, 'stop':stop})
    
    msg = 'Submitted a request to delete statistics from [{}] to [{}]. Check the server logs for details.'.format(start, stop)
    messages.add_message(req, messages.INFO, msg, extra_tags='success')
        
    return redirect('{}?cluster={}'.format(reverse('stats-maintenance'), req.zato.cluster_id))
