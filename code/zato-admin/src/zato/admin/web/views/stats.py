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
from cStringIO import StringIO
from csv import DictWriter
from datetime import datetime

# anyjson
from anyjson import dumps

# Bunch
from bunch import Bunch

# dateutil
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

# Django
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.template.response import TemplateResponse

# django-settings
from django_settings.models import PositiveInteger, Setting

# pytz
from pytz import UTC

# Zato
from zato.admin.web import invoke_admin_service, from_utc_to_user
from zato.admin.web.forms.stats import CompareForm, MaintenanceForm, NForm, SettingsForm
from zato.admin.web.views import get_sample_dt, meth_allowed
from zato.common import DEFAULT_STATS_SETTINGS, StatsElem, zato_path

logger = logging.getLogger(__name__)

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

def _get_stats(cluster, start, stop, n, n_type):
    """ Returns at most n statistics elements of a given n_type for the period
    between start and stop.
    """
    out = []
    zato_message, _  = invoke_admin_service(cluster, 'zato:stats.get-top-n',
        {'start':start, 'stop':stop, 'n':n, 'n_type':n_type})
    
    if zato_path('response.item_list.item').get_from(zato_message) is not None:
        for msg_item in zato_message.response.item_list.item:
            out.append(StatsElem.from_xml(msg_item))
            
    return out

@meth_allowed('GET')
def top_n(req, choice):
    labels = {'last_hour':'Last hour', 'today':'Today', 'yesterday':'Yesterday', 'last_24h':'Last 24h',
            'this_week':'This week', 'this_month':'This month', 'this_year':'This year'}
    
    compare_to = {
        'last_hour':[
            ('prev_hour', 'The previous hour'),
            ('prev_day', 'Same hour the previous day'),
            ('prev_week', 'Same hour and day the previous week'),
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
            trend_elems = 60
            start = now + relativedelta(minutes=-trend_elems)
            return start.replace(tzinfo=UTC).isoformat(), now.replace(tzinfo=UTC).isoformat()
            
        start, stop = locals()['_params_' + choice]()

    return_data = {
        'start': start,
        'stop': stop,
        'n': n,
        'label': labels[choice], 
        'n_form': NForm(initial={'n':n}),
        'compare_form': CompareForm(compare_to=compare_to[choice]),
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'choose_cluster_form':req.zato.choose_cluster_form,
        'sample_dt': get_sample_dt(req.zato.user_profile),
    }
    
    return TemplateResponse(req, 'zato/stats/top-n.html', return_data)

def _top_n_data_csv(user_profile, req_input, cluster):

    n_type_keys = {
        'mean': ['start', 'stop', 'service_name', 'mean', 'mean_all_services', 
                  'usage_perc_all_services', 'time_perc_all_services', 'all_services_usage', 'mean_trend'],
        'usage': ['start', 'stop', 'service_name', 'usage', 'rate', 'usage_perc_all_services', 
                  'time_perc_all_services', 'all_services_usage', 'usage_trend'],
        }
    
    buff = StringIO()
    writer = DictWriter(buff, n_type_keys[req_input.n_type], extrasaction='ignore')
    writer.writeheader()
    
    for stat in _get_stats(cluster, req_input.start, req_input.stop, req_input.n, req_input.n_type):
        d = stat.to_dict()
        d['start'] = req_input.start
        d['stop'] = req_input.stop
        writer.writerow(d)
        
    out = buff.getvalue()
    buff.close()
        
    response = HttpResponse(out, mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}'.format('zato-stats.csv')
    
    return response

def _top_n_data_html(user_profile, req_input, cluster):
    
    return_data = {'has_stats':False, 'start':req_input.start, 'stop':req_input.stop}
    settings = {}
    query_data = '&amp;'.join('{}={}'.format(key, value) for key, value in req_input.items() if key != 'format')
    
    if req_input.n:
        for name in('atttention_slow_threshold', 'atttention_top_threshold'):
            settings[name] = int(Setting.objects.get_value(name, default=DEFAULT_STATS_SETTINGS[name]))
        
    for name in('mean', 'usage'):
        d = {'cluster_id':cluster.id, 'side':req_input.side}
        if req_input.n:
            stats = _get_stats(cluster, req_input.start, req_input.stop, req_input.n, name)
            
            # I.e. whether it's not an empty list (assuming both stats will always be available or none will be)
            return_data['has_stats'] = len(stats)
            
            return_data['{}_csv_href'.format(name)] = '{}?{}&amp;format=csv&amp;n_type={}&amp;cluster={}'.format(
                reverse('stats-top-n-data'), query_data, name, cluster.id)
            
            d.update({name:stats})
            d.update(settings)
            
        return_data[name] = loader.render_to_string('zato/stats/top-n-table-{}.html'.format(name), d)
        
    for name in('start', 'stop'):
        return_data['{}_label'.format(name)] = from_utc_to_user(return_data[name], user_profile)
        
    return HttpResponse(dumps(return_data), mimetype='application/javascript')

@meth_allowed('GET', 'POST')
def top_n_data(req):
    """ n and n_type will always be given. format may be None and will
    default to 'html'. Also, either start/stop or left_start/left_stop/shift
    will be present - if the latter, start and stop will be computed as left_start/left_stop
    shifted by the value pointed to by shift.
    """
    req_input = Bunch.fromkeys(('start', 'stop', 'n', 'n_type', 'format', 
        'left-start', 'left-stop', 'right-start', 'right-stop', 'shift', 'side'))
    
    for name in req_input:
        req_input[name] = req.GET.get(name, '') or req.POST.get(name, '')

    try:
        req_input.n = int(req_input.n)
    except ValueError:
        req_input.n = 0
        
    req_input.format = req_input.format or 'html'
    
    shift_params = {
        'prev_hour': {'minutes': -60},
        'prev_day': {'days': -1},
        'prev_week': {'days': -7},
        
        'next_hour': {'minutes': 60},
        'next_day': {'days': 1},
        'next_week': {'days': 7},
    }
    
    if req_input.shift:
        for name in('start', 'stop'):
            base_value = parse(req_input[name])
            delta = relativedelta(**shift_params[req_input.shift])
            req_input[name] = (base_value + delta).isoformat()

    return globals()['_top_n_data_{}'.format(req_input.format)](req.zato.user_profile, req_input, req.zato.cluster)
    
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

    return TemplateResponse(req, 'zato/stats/settings.html', return_data)

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
    
    return TemplateResponse(req, 'zato/stats/maintenance.html', return_data)

@meth_allowed('POST')
def maintenance_delete(req):
    start = req.POST['start']
    stop = req.POST['stop']
    
    invoke_admin_service(req.zato.cluster, 'zato:stats.delete', {'start':start, 'stop':stop})
    
    msg = 'Submitted a request to delete statistics from [{}] to [{}]. Check the server logs for details.'.format(start, stop)
    messages.add_message(req, messages.INFO, msg, extra_tags='success')
        
    return redirect('{}?cluster={}'.format(reverse('stats-maintenance'), req.zato.cluster_id))

@meth_allowed('GET')
def by_service(req):
    pass