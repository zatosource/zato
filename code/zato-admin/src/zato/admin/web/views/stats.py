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
from calendar import monthrange
from copy import deepcopy
from cStringIO import StringIO
from csv import DictWriter
from datetime import date, datetime

# anyjson
from anyjson import dumps

# Bunch
from bunch import Bunch

# dateutil
from dateutil.parser import parse
from dateutil.relativedelta import MO, relativedelta

# Django
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.template.defaultfilters import date as django_date_filter
from django.template.response import TemplateResponse

# django-settings
from django_settings.models import PositiveInteger, Setting

# pytz
import pytz
from pytz import UTC

# Zato
from zato.admin.web import from_user_to_utc, from_utc_to_user, invoke_admin_service
from zato.admin.web.forms.stats import MaintenanceForm, NForm, SettingsForm
from zato.admin.web.views import get_js_dt_format, get_sample_dt, meth_allowed
from zato.common import DEFAULT_STATS_SETTINGS, SECONDS_IN_DAY, StatsElem, zato_path

logger = logging.getLogger(__name__)

SUMMARY_PREFIX = 'summary-'

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
    JobAttrFormMapping('zato.stats.ProcessRawTimes', 
        [JobAttrForm('raw_times', 'seconds'),  JobAttrForm('raw_times_batch', {'extra':'max_batch_size'})]),
    JobAttrFormMapping('zato.stats.AggregateByMinute', [JobAttrForm('per_minute_aggr', 'seconds')]),
    }

stats_type_service = {
    'trends': 'zato:stats.get-trends',
    '{}today'.format(SUMMARY_PREFIX): 'zato:stats.get-summary-by-range',
}

skip_by = {
    'last_hour': 'hour',
    'today': 'day',
    'this_week': 'week',
    'this_month': 'month',
    'this_year': 'year',
}

short_date_choice_format = {
    'day': 'date',
    'week': 'date',
    'month': 'month_year',
    'year': 'year',
}

# ##############################################################################

def _get_start_stop(user_profile, stats_type, start, stop):
    if stats_type.startswith(SUMMARY_PREFIX):
        if not start:
            start = date.today().isoformat() + 'T00:00+00:00'
            
        start = from_user_to_utc(start, user_profile, 'month_year')
        
        return start.isoformat(), None
    else:
        return start, stop
        
def _short_utc_to_user(dt, user_profile, choice):
    for k, v in short_date_choice_format.items():
        if k in choice:
            return from_utc_to_user(dt, user_profile, v)
            
def _long_user_to_utc(start, user_profile, summary_type):
    """ Takes input in the user's timezone and calculates start/stop in UTC.
    """
    
    summary_type = summary_type.replace(SUMMARY_PREFIX, '')
    
    if summary_type in('today', 'yesterday'):
        
        # In daily summaries we always start on midnight ..
        start = from_user_to_utc('{} 00:00'.format(start), user_profile)
        
        # .. it's one day earlier though if it was yesterday
        if summary_type == 'yesterday':
            start = start + relativedelta(days=-1)
            
        stop = start + relativedelta(days=1)

    elif summary_type == 'week':    
        
        # Find the last Monday in the user's timezone
        start = parse(start, dayfirst=user_profile.date_format_py.startswith('d'))
        start = start + relativedelta(weekday=MO(-1))
        
        # Only now we can convert it to UTC
        start = from_user_to_utc(start, user_profile)
        
        # Luckily, a week has always 7 days
        stop = start + relativedelta(days=7)
        
    elif summary_type == 'month':

        # Find the first day of month in user's timezone
        start = parse(start, dayfirst=user_profile.date_format_py.startswith('d'))
        start = start.replace(day=1)
        
        # How many days the current month has. Note that we're doing it before
        # switching to UTC as this will very well change the month so if the
        # start on input was '02-2012' (Feb 2012), it would've been changed to
        # Jan 2012 in UTC and that in turn would've meant 31 days instead of 29.
        days = monthrange(start.year, start.month)[1]

        # Now we can safely convert to UTC
        start = from_user_to_utc(start, user_profile)
        
        # stop will be equal to the number of seconds since in the month user
        # was referring to
        stop = start + relativedelta(seconds=days*SECONDS_IN_DAY)
        
    elif summary_type == 'year':
        # Midnight 1st of Jan in user's timezone won't necessarily be midnight 1st of Jun in UTC
        
        year = int(start)
        
        start = datetime(year=year, month=1, day=1, hour=0, minute=0, second=0).isoformat()
        stop = datetime(year=year, month=12, day=31, hour=23, minute=59, second=59).isoformat()
        
        start = from_user_to_utc(start, user_profile)
        stop = from_user_to_utc(stop, user_profile)
        
    else:
        raise ValueError('Could not understand summary_type:[{}]'.format(summary_type))
        
    now = datetime.utcnow()    
    if stop > now:
        stop = now
        
    return start.isoformat(), stop.isoformat()

def _get_stats(cluster, start, stop, n, n_type, stats_type=None):
    """ Returns at most n statistics elements of a given n_type for the period
    between start and stop.
    """
    out = []
    input_dict = {'start':start, 'n':n, 'n_type':n_type}
    
    if stop:
        input_dict['stop'] = stop

    zato_message, _  = invoke_admin_service(cluster, stats_type_service[stats_type], input_dict)
    
    if zato_path('response.item_list.item').get_from(zato_message) is not None:
        for msg_item in zato_message.response.item_list.item:
            out.append(StatsElem.from_xml(msg_item))
            
    return out

def _get_stats_params(req, choice, is_summary):
    
    labels = {'last_hour':'Last hour', 'today':'Today', 'yesterday':'Yesterday', 'last_24h':'Last 24h',
            'this_week':'This week', 'this_month':'This month', 'this_year':'This year'}
    
    compare_to = {
        'last_hour':[
            ('prev_hour', 'hour'),
            ('prev_day', 'hour/day'),
            ('prev_week', 'hour/day/week'),
        ], 

        'today':[
            ('prev_day', 'day'),
            ('prev_week', 'day/week'),
        ], 
        'yesterday':[('', '')], 
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
            elems = 60
            start = now + relativedelta(minutes=-elems)
            return start.replace(tzinfo=UTC), now.replace(tzinfo=UTC)
        
        def _params_today():
            start = now.strftime('%Y-%m-%dT%H:%M+00:00')
            return start, ''
            
        start, stop = locals()['_params_' + choice]()
        
        if is_summary:
            start = _short_utc_to_user(start, req.zato.user_profile, choice)
        else:
            start = from_utc_to_user(start, req.zato.user_profile)
        
        if stop:
            stop = from_utc_to_user(stop, req.zato.user_profile)
        
    return start, stop, n, labels[choice], compare_to[choice]

# ##############################################################################

def _stats_start_stop(start, stop, user_profile, stats_type):
    if stats_type.startswith(SUMMARY_PREFIX):
        start, stop = _long_user_to_utc(start, user_profile, stats_type)
    else:
        start = from_user_to_utc(start, user_profile)
        stop = from_user_to_utc(stop, user_profile)
        
    return start, stop

# ##############################################################################

def _stats_data_csv(user_profile, req_input, cluster, stats_type):

    n_type_keys = {
        'mean': ['start', 'stop', 'service_name', 'mean', 'mean_all_services', 
                  'usage_perc_all_services', 'time_perc_all_services', 'all_services_usage', 'mean_trend'],
        'usage': ['start', 'stop', 'service_name', 'usage', 'rate', 'usage_perc_all_services', 
                  'time_perc_all_services', 'all_services_usage', 'usage_trend'],
        }
    
    start, stop = _stats_start_stop(req_input.start, req_input.stop, user_profile, stats_type)
    
    buff = StringIO()
    writer = DictWriter(buff, n_type_keys[req_input.n_type], extrasaction='ignore')
    writer.writeheader()
    
    for stat in _get_stats(cluster, req_input.start, req_input.stop, req_input.n, req_input.n_type, stats_type):
        d = stat.to_dict()
        d['start'] = req_input.start
        d['stop'] = req_input.stop
        writer.writerow(d)
        
    out = buff.getvalue()
    buff.close()
        
    response = HttpResponse(out, mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}'.format('zato-stats.csv')
    
    return response

def _stats_data_html(user_profile, req_input, cluster, stats_type):
    
    return_data = {'has_stats':False, 'start':req_input.start, 'stop':req_input.stop}
    settings = {}
    query_data = '&amp;'.join('{}={}'.format(key, value) for key, value in req_input.items() if key != 'format')
    
    start, stop = _stats_start_stop(req_input.start, req_input.stop, user_profile, stats_type)
    
    if req_input.n:
        for name in('atttention_slow_threshold', 'atttention_top_threshold'):
            settings[name] = int(Setting.objects.get_value(name, default=DEFAULT_STATS_SETTINGS[name]))
            
    for name in('mean', 'usage'):
        d = {'cluster_id':cluster.id, 'side':req_input.side, 'needs_trends': stats_type == 'trends'}
        if req_input.n:

            stats = _get_stats(cluster, start, stop, req_input.n, name, stats_type)
            
            # I.e. whether it's not an empty list (assuming both stats will always be available or neither will be)
            return_data['has_stats'] = len(stats)
            
            return_data['{}_csv_href'.format(name)] = '{}?{}&amp;format=csv&amp;n_type={}&amp;cluster={}'.format(
                reverse('stats-trends-data'), query_data, name, cluster.id)
            
            d.update({name:stats})
            d.update(settings)
            
        return_data[name] = loader.render_to_string('zato/stats/trends-table-{}.html'.format(name), d)
        
    for name in('start', 'stop'):
        return_data['{}_label'.format(name)] = return_data[name]
        
    return HttpResponse(dumps(return_data), mimetype='application/javascript')

def _stats_data_test(*ignored_args, **ignored_kwargs):
    """ A fake stats-returning function which is actually mocked out in tests only.
    """
    raise NotImplementedError('This function should not be called directly')

def stats_data(req, stats_type):
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
            req_input[name] = django_date_filter(base_value + delta, req.zato.user_profile.date_time_format_py)
            
    return globals()['_stats_data_{}'.format(req_input.format)](req.zato.user_profile, 
        req_input, req.zato.cluster, stats_type)

def stats_data2(req, stats_type):

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
            req_input[name] = django_date_filter(base_value + delta, req.zato.user_profile.date_time_format_py)
            
    return globals()['_stats_data_{}'.format(req_input.format)](req.zato.user_profile, 
        req_input, req.zato.cluster, stats_type)

@meth_allowed('GET', 'POST')
def stats_trends_data(req):
    print(req.zato.user_profile)
    return stats_data(req, 'trends')

@meth_allowed('GET', 'POST')
def stats_summary_data(req):
    return stats_data2(req, '{}{}'.format(SUMMARY_PREFIX, req.POST.get('choice', 'missing-value')))

def trends_summary(req, choice, stats_title, is_summary):
    start, stop, n, label, compare_to = _get_stats_params(req, choice, is_summary)
        
    return_data = {
        'start': start,
        'stop': stop,
        'n': n,
        'choice': choice, 
        'label': label, 
        'n_form': NForm(initial={'n':n}),
        'compare_to': compare_to,
        'needs_compare_to_other': choice in('last_hour', 'today'),
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'choose_cluster_form':req.zato.choose_cluster_form,
        'sample_dt': get_sample_dt(req.zato.user_profile),
        'stats_title': stats_title,
        'skip_by': skip_by[choice],
    }
    
    return_data.update(get_js_dt_format(req.zato.user_profile))
    return TemplateResponse(req, 'zato/stats/trends_summary.html', return_data)

@meth_allowed('GET')
def trends(req, choice):
    return trends_summary(req, choice, 'Trends', False)

@meth_allowed('GET')
def summary(req, choice):
    return trends_summary(req, choice, 'Summary', True)

# ##############################################################################
    
@meth_allowed('GET')
def settings(req):
    
    if req.zato.get('cluster'):
        
        _settings = {}
        defaults = deepcopy(DEFAULT_STATS_SETTINGS)
        
        for mapping in job_mappings:

            zato_message, _  = invoke_admin_service(req.zato.
                cluster, 'zato:scheduler.job.get-by-name', {'name': mapping.job_name})
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

        zato_message, _  = invoke_admin_service(
            req.zato.cluster, 'zato:scheduler.job.get-by-name', {'name': mapping.job_name})
        if zato_path('response.item').get_from(zato_message) is not None:
            item = zato_message.response.item
            
            # Gotta love dictionary comprehensions!
            params = {attr: getattr(item, attr).text for attr in(
                'id', 'name', 'is_active', 'job_type', 'start_date', 'extra')}
        
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

# ##############################################################################

@meth_allowed('GET')
def maintenance(req):
    return_data = {
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'choose_cluster_form':req.zato.choose_cluster_form,
        'form': MaintenanceForm()
    }
    
    return_data.update(get_js_dt_format(req.zato.user_profile))
    
    return TemplateResponse(req, 'zato/stats/maintenance.html', return_data)

@meth_allowed('POST')
def maintenance_delete(req):
    start = from_user_to_utc(req.POST['start'], req.zato.user_profile)
    stop = from_user_to_utc(req.POST['stop'], req.zato.user_profile)
    
    invoke_admin_service(req.zato.cluster, 'zato:stats.delete', {'start':start, 'stop':stop})
    
    msg = 'Submitted a request to delete statistics from [{}] to [{}]. Check the server logs for details.'.format(
        from_utc_to_user(start, req.zato.user_profile), 
        from_utc_to_user(stop, req.zato.user_profile))
        
    messages.add_message(req, messages.INFO, msg, extra_tags='success')
        
    return redirect('{}?cluster={}'.format(reverse('stats-maintenance'), req.zato.cluster_id))

# ##############################################################################

