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
from pytz import timezone, utc

# Zato
from zato.admin.web import from_user_to_utc, from_utc_to_user, invoke_admin_service
from zato.admin.web.forms.stats import MaintenanceForm, NForm, SettingsForm
from zato.admin.web.views import get_js_dt_format, get_sample_dt, meth_allowed
from zato.common import DEFAULT_STATS_SETTINGS, SECONDS_IN_DAY, StatsElem, zato_path
from zato.common.util import from_local_to_utc, make_repr, now, utcnow

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

class DateInfo(object):
    def __init__(self, utc_start, utc_stop, user_start, user_stop, label=None):
        self.utc_start = utc_start
        self.utc_stop = utc_stop
        self.user_start = user_start
        self.user_stop = user_stop
        self.label = label

    def __repr__(self):
        return make_repr(self)

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

skip_by_duration = {
    'last_hour': 'hour',
    'prev_hour': 'hour',
    'next_hour': 'hour',
    'today': 'day',
    'prev_hour_day': 'hour',
    'prev_hour_day_week': 'hour',
    'this_week': 'week',
    'this_month': 'month',
    'this_year': 'year',
}

user_format = {
    'hour': 'date_time',
    'day': 'date',
    'week': 'date',
    'month': 'month_year',
    'year': 'year',
}

# ##############################################################################

compare_to = {
    'last_hour':[
        ('prev_hour', 'hour'),
        ('prev_hour_day', 'hour/day'),
        ('prev_hour_day_week', 'hour/day/week'),
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

# The two dictionary below return keyword args passed into relativedelta for both start and
# stop dates. The former is a delta relative to the base_date, the latter
# is relative to the resulting start_date.

start_delta_kwargs = {
    'prev_hour': {'hours':-1},
    'prev_hour_day': {'days':-1},
    'prev_hour_day_week': {'weeks':-1},
    
    'prev_day': {'days':-1},
    'prev_week': {'weeks':-1},
    'prev_month': {'months':-1},
    'prev_year': {'years':-1},
    
    'next_hour': {'hours':1},
    'next_day': {'days':1},
    'next_week': {'weeks':1},
    'next_month': {'months':1},
    'next_year': {'years':1},
}

stop_delta_kwargs = {
    'hour': {'hours':1},
    'day': {'days':1},
    'week': {'weeks':1},
    'month': {'months':1},
    'year': {'years':1},
}

def shift(utc_base_date, user_profile, shift_type, duration, format):
    """ Shifts the base date by the amount specified and returns resulting start
    and stop dates in UTC and user timezone.
    """
    if shift_type not in start_delta_kwargs:
        raise ValueError('Unknown shift_type:[{}]'.format(shift_type))

    _start_delta_kwargs = start_delta_kwargs[shift_type]
    _stop_delta_kwargs = stop_delta_kwargs[duration]
    
    utc_start = utc_base_date + relativedelta(**_start_delta_kwargs)
    utc_stop = utc_start + relativedelta(**_stop_delta_kwargs)
    
    user_start = from_utc_to_user(utc_start, user_profile, format)
    user_stop = from_utc_to_user(utc_stop, user_profile, format)
        
    return DateInfo(utc_start.isoformat(), utc_stop.isoformat(), user_start, user_stop)

def get_default_date(date_type, user_profile, format):
    """ Returns default start and stop date in UTC and user's timezone depending
    on the stats type and duration requested.
    """
    def get_today(_user_profile, _format):
        """ user_start is today's midnight but it needs to be in user's TZ. user_stop is current time simply,
        in user's timezone again.
        """
        user_now = now(timezone(_user_profile.timezone)).replace(tzinfo=None)
        user_today_midnight = datetime(user_now.year, user_now.month, user_now.day)
        
        utc_start = from_local_to_utc(user_today_midnight, _user_profile.timezone)
        utc_stop = from_local_to_utc(user_now, _user_profile.timezone)
        
        user_start = from_utc_to_user(utc_start, _user_profile, _format)
        user_stop = None
        
        return utc_start, utc_stop, user_start, user_stop
    
    if date_type == 'last_hour':
        # stop is what current time is now so return it in UTC and user's TZ
        # along with start which will be equal to stop - 1 hour.
        utc_stop = utc.fromutc(utcnow())
        utc_start = utc.fromutc(utc_stop + relativedelta(hours=-1))
        
        user_start = from_utc_to_user(utc_start, user_profile)
        user_stop = from_utc_to_user(utc_stop, user_profile)
        
        label = 'one hour'
        
    elif date_type == 'today':
        utc_start, utc_stop, user_start, user_stop = get_today(user_profile, format)
        label = 'today'
    
    elif date_type == 'yesterday':
        # Yesterday's start is today's start - 1 day
        today_utc_start, today_utc_stop, today_user_start, user_stop = get_today(user_profile, format)
        
        utc_start = today_utc_start + relativedelta(days=-1)
        utc_stop = utc_start + relativedelta(days=1)
        
        user_start = from_utc_to_user(utc_start, user_profile, format)
        
        label = 'yesterday'
        
    elif date_type == 'this_week':
        # This week extends from Monday midnight to right now
        user_now = now(timezone(user_profile.timezone)).replace(tzinfo=None)
        user_prev_monday = user_now + relativedelta(weekday=MO(-1))
        user_prev_monday = datetime(year=user_prev_monday.year, month=user_prev_monday.month, day=user_prev_monday.day)
        
        utc_start = from_local_to_utc(user_prev_monday, user_profile.timezone)
        utc_stop = from_local_to_utc(user_now, user_profile.timezone)
        
        user_start = from_utc_to_user(utc_start, user_profile, format)
        user_stop = from_utc_to_user(utc_stop, user_profile, format)
        
        label = 'this week'
        
    elif date_type == 'this_month':
        # From midnight the first day of month up until now
        user_now = now(timezone(user_profile.timezone)).replace(tzinfo=None)
        user_1st_of_month = datetime(year=user_now.year, month=user_now.month, day=1)
        
        utc_start = from_local_to_utc(user_1st_of_month, user_profile.timezone)
        utc_stop = from_local_to_utc(user_now, user_profile.timezone)
        
        user_start = from_utc_to_user(utc_start, user_profile, format)
        user_stop = None
        
        label = 'this month'
        
    elif date_type == 'this_year':
        # From midnight the first day of year up until now
        user_now = now(timezone(user_profile.timezone)).replace(tzinfo=None)
        user_new_year = datetime(year=user_now.year, month=1, day=1)
        
        utc_start = from_local_to_utc(user_new_year, user_profile.timezone)
        utc_stop = from_local_to_utc(user_now, user_profile.timezone)
        
        user_start = from_utc_to_user(utc_start, user_profile, format)
        user_stop = None
        
        label = 'this year'
    
    else:
        raise ValueError('Unrecognized date_type:[{}]'.format(date_type))
    
    return DateInfo(utc_start.isoformat(), utc_stop.isoformat(), user_start, user_stop, label)

# ##############################################################################


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
    
    return_data = {
        'has_stats':False, 
        'utc_start':req_input.utc_start, 
        'utc_stop':req_input.utc_stop,
        'user_start':req_input.user_start, 
        'user_stop':req_input.user_stop,
    }
    
    settings = {}
    query_data = '&amp;'.join('{}={}'.format(key, value) for key, value in req_input.items() if key != 'format')
    
    if req_input.n:
        for name in('atttention_slow_threshold', 'atttention_top_threshold'):
            settings[name] = int(Setting.objects.get_value(name, default=DEFAULT_STATS_SETTINGS[name]))
            
    for name in('mean', 'usage'):
        d = {'cluster_id':cluster.id, 'side':req_input.side, 'needs_trends': stats_type == 'trends'}
        if req_input.n:

            stats = _get_stats(cluster, req_input.utc_start, req_input.utc_stop, req_input.n, name, stats_type)
            
            # I.e. whether it's not an empty list (assuming both stats will always be available or neither will be)
            return_data['has_stats'] = len(stats)
            
            return_data['{}_csv_href'.format(name)] = '{}?{}&amp;format=csv&amp;n_type={}&amp;cluster={}'.format(
                reverse('stats-trends-data'), query_data, name, cluster.id)
            
            d.update({name:stats})
            d.update(settings)
            
        return_data[name] = loader.render_to_string('zato/stats/trends-table-{}.html'.format(name), d)
        
    for name in('user_start', 'user_stop'):
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
    req_input = Bunch.fromkeys(('utc_start', 'utc_stop', 'user_start', 'user_stop',
        'n', 'n_type', 'format', 'left-start', 'left-stop', 'right-start', 'right-stop', 
        'shift', 'side'))
    
    for name in req_input:
        req_input[name] = req.GET.get(name, '') or req.POST.get(name, '')
        
    try:
        req_input.n = int(req_input.n)
    except ValueError:
        req_input.n = 0
        
    req_input.format = req_input.format or 'html'

    if req_input.shift:
        duration = skip_by_duration[req_input.shift]
        format = user_format[duration]

        shift_info = shift(parse(req_input.utc_start), req.zato.user_profile, req_input.shift, duration, format)

        req_input['utc_start'] = shift_info.utc_start
        req_input['utc_stop'] = shift_info.utc_stop
        
        req_input['user_start'] = shift_info.user_start
        req_input['user_stop'] = shift_info.user_stop

    return globals()['_stats_data_{}'.format(req_input.format)](req.zato.user_profile, 
        req_input, req.zato.cluster, stats_type)

@meth_allowed('GET', 'POST')
def stats_trends_data(req):
    return stats_data(req, 'trends')

@meth_allowed('GET', 'POST')
def stats_summary_data(req):
    return stats_data(req, '{}{}'.format(SUMMARY_PREFIX, req.POST.get('choice', 'missing-value')))

def trends_summary(req, choice, stats_title, is_summary):
    info = get_default_date(choice, req.zato.user_profile, 'date')
    
    n = 10 # TODO: Actually read it off somewhere
    _compare_to = compare_to[choice]
        
    return_data = {
        'utc_start': info.utc_start,
        'utc_stop': info.utc_stop,
        'user_start': info.user_start,
        'user_stop': info.user_stop,
        'n': n,
        'choice': choice, 
        'label': info.label, 
        'n_form': NForm(initial={'n':n}),
        'compare_to': _compare_to,
        'needs_compare_to_other': choice in('last_hour', 'today'),
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'choose_cluster_form':req.zato.choose_cluster_form,
        'sample_dt': get_sample_dt(req.zato.user_profile),
        'stats_title': stats_title,
        'skip_by': skip_by_duration[choice],
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
