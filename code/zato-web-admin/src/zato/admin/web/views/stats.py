# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from copy import deepcopy
from csv import DictWriter
from datetime import datetime
from io import StringIO
from traceback import format_exc

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
from django.template.response import TemplateResponse

# pytz
from pytz import timezone, utc

# Zato
from zato.admin.web import from_user_to_utc, from_utc_to_user
from zato.admin.web.forms.stats import MaintenanceForm, NForm, SettingsForm
from zato.admin.web.views import get_js_dt_format, get_sample_dt, method_allowed
from zato.common import DEFAULT_STATS_SETTINGS, StatsElem
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
    def __init__(self, utc_start, utc_stop, user_start, user_stop, label=None, step=None):
        self.utc_start = utc_start
        self.utc_stop = utc_stop
        self.user_start = user_start
        self.user_stop = user_stop or ''
        self.label = label
        self.step = step

    def __repr__(self):
        return make_repr(self)

    def __getitem__(self, name):
        return object.__getattribute__(self, name)

# A mapping a job type, its name and the execution interval unit
job_mappings = {
    JobAttrFormMapping('zato.stats.process-raw-times',
        [JobAttrForm('raw_times', 'seconds'), JobAttrForm('raw_times_batch', {'extra':'max_batch_size'})]),
    JobAttrFormMapping('zato.stats.aggregate-by-minute', [JobAttrForm('per_minute_aggr', 'seconds')]),
    }

compare_to = {
    'last_hour':[
        ('last_hour_prev_hour', 'hour'),
        ('last_hour_prev_hour_day', 'hour/day'),
        ('last_hour_prev_hour_day_week', 'hour/day/week'),
    ],
    'today': [
        ('today_prev_day', 'day'),
        ('today_prev_day_week', 'day/week'),
    ],
    'yesterday': [
        ('yesterday_prev_day', 'day'),
        ('yesterday_prev_day_week', 'day/week'),
    ],
    'this_week': [
        ('this_week_prev_week', 'week'),
        ('this_week_prev_week_month', 'week/month'),
    ],
    'this_month': [
        ('this_month_prev_month', 'month'),
        ('this_month_prev_month_year', 'month/year'),
    ],
    'this_year': [
        ('this_year_prev_year', 'year'),
    ],
}

start_delta_kwargs = {
    'last_hour_prev': {'hours':-1},
    'last_hour_next': {'hours':1},
    'last_hour_prev_hour': {'hours':-1},
    'last_hour_prev_hour_day': {'days':-1},
    'last_hour_prev_hour_day_week': {'weeks':-1},

    'today_prev': {'days':-1},
    'today_next': {'days':1},
    'today_prev_day': {'days':-1},
    'today_prev_day_week': {'weeks':-1},

    'yesterday_prev': {'days':-1},
    'yesterday_next': {'days':1},
    'yesterday_prev_day': {'days':-1},
    'yesterday_prev_day_week': {'weeks':-1},

    'this_week_prev': {'weeks':-1},
    'this_week_next': {'weeks':1},
    'this_week_prev_week': {'weeks':-1},
    'this_week_prev_week_month': {'months':-1},

    'this_month_prev': {'months':-1},
    'this_month_next': {'months':1},
    'this_month_prev_month': {'months':-1},
    'this_month_prev_month_year': {'years':-1},

    'this_year_prev': {'years':-1},
    'this_year_next': {'years':1},
    'this_year_prev_year': {'years':-1},
}

skip_by_duration = {
    'last_hour_prev': 'hour',
    'last_hour_next': 'hour',
    'last_hour_prev_hour': 'hour',
    'last_hour_prev_hour_day': 'hour',
    'last_hour_prev_hour_day_week': 'hour',

    'today_prev': 'day',
    'today_next': 'day',
    'today_prev_day': 'day',
    'today_prev_day_week': 'day',

    'yesterday_prev': 'day',
    'yesterday_next': 'day',
    'yesterday_prev_day': 'day',
    'yesterday_prev_day_week': 'day',

    'this_week_prev': 'week',
    'this_week_next': 'week',
    'this_week_prev_week': 'week',
    'this_week_prev_week_month': 'week',

    'this_month_prev': 'month',
    'this_month_next': 'month',
    'this_month_prev_month': 'month',
    'this_month_prev_month_year': 'month',

    'this_year_prev': 'year',
    'this_year_next': 'year',
    'this_year_prev_year': 'year',
}

stop_delta_kwargs = {
    'hour': {'hours':1},
    'day': {'days':1},
    'week': {'weeks':1},
    'month': {'months':1},
    'year': {'years':1},
}

user_format = {
    'hour': 'date_time',
    'day': 'date',
    'week': 'date',
    'month': 'month_year',
    'year': 'year',
}

def shift(utc_base_date, user_start, user_profile, shift_type, duration, format):
    """ Shifts the base date by the amount specified and returns resulting start
    and stop dates in UTC and user timezone.
    """
    if shift_type not in start_delta_kwargs:
        raise ValueError('Unknown shift_type:[{}]'.format(shift_type))

    _start_delta_kwargs = start_delta_kwargs[shift_type]

    # Special-case month duration because UTC '2012-09-30 22:00:00+00:00' (which is 2012-10-01 CEST)
    # minus one month happens to be '2012-08-30 22:00:00+00:00' instead of '2012-09-31 22:00:00+00:00'
    # so it's 2012-08-30 CEST instead of 2012-09-01. In other words, we would've jumped from Oct 2012 to Aug 2012 directly.

    if duration != 'month':
        utc_start = utc_base_date + relativedelta(**_start_delta_kwargs)
    else:
        user_start = datetime.strptime(user_start, user_profile.month_year_format_strptime)
        current_month_start = datetime(user_start.year, user_start.month, 1)
        prev_month_start = current_month_start + relativedelta(**_start_delta_kwargs)
        utc_start = from_local_to_utc(prev_month_start, user_profile.timezone)

    _stop_delta_kwargs = stop_delta_kwargs[duration]
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

        label = 'Last hour'
        step = 'hour'

    elif date_type == 'today':
        utc_start, utc_stop, user_start, user_stop = get_today(user_profile, format)
        label = 'Today'
        step = 'day'

    elif date_type == 'yesterday':
        # Yesterday's start is today's start - 1 day
        today_utc_start, today_utc_stop, today_user_start, user_stop = get_today(user_profile, format)

        utc_start = today_utc_start + relativedelta(days=-1)
        utc_stop = utc_start + relativedelta(days=1)

        user_start = from_utc_to_user(utc_start, user_profile, format)

        label = 'Yesterday'
        step = 'day'

    elif date_type == 'this_week':
        # This week extends from Monday midnight to right now
        user_now = now(timezone(user_profile.timezone)).replace(tzinfo=None)
        user_prev_monday = user_now + relativedelta(weekday=MO(-1))
        user_prev_monday = datetime(year=user_prev_monday.year, month=user_prev_monday.month, day=user_prev_monday.day)

        utc_start = from_local_to_utc(user_prev_monday, user_profile.timezone)
        utc_stop = from_local_to_utc(user_now, user_profile.timezone)

        user_start = from_utc_to_user(utc_start, user_profile, format)
        user_stop = from_utc_to_user(utc_stop, user_profile, format)

        label = 'This week'
        step = 'week'

    elif date_type == 'this_month':
        # From midnight the first day of month up until now
        user_now = now(timezone(user_profile.timezone)).replace(tzinfo=None)
        user_1st_of_month = datetime(year=user_now.year, month=user_now.month, day=1)

        utc_start = from_local_to_utc(user_1st_of_month, user_profile.timezone)
        utc_stop = from_local_to_utc(user_now, user_profile.timezone)

        user_start = from_utc_to_user(utc_start, user_profile, format)
        user_stop = None

        label = 'This month'
        step = 'month'

    elif date_type == 'this_year':
        # From midnight the first day of year up until now
        user_now = now(timezone(user_profile.timezone)).replace(tzinfo=None)
        user_new_year = datetime(year=user_now.year, month=1, day=1)

        utc_start = from_local_to_utc(user_new_year, user_profile.timezone)
        utc_stop = from_local_to_utc(user_now, user_profile.timezone)

        user_start = from_utc_to_user(utc_start, user_profile, format)
        user_stop = None

        label = 'This year'
        step = 'year'

    else:
        raise ValueError('Unrecognized date_type:[{}]'.format(date_type))

    return DateInfo(utc_start.isoformat(), utc_stop.isoformat(), user_start, user_stop, label, step)

# ##############################################################################


def _get_stats(client, start, stop, n, n_type, stats_type=None):
    """ Returns at most n statistics elements of a given n_type for the period
    between start and stop.
    """
    out = []
    input_dict = {'start':start, 'n':n, 'n_type':n_type}

    if stop:
        input_dict['stop'] = stop

    if stats_type == 'trends':
        service_name = 'zato.stats.trends.get-trends'
    else:
        service_name = 'zato.stats.summary.get-summary-by-range'

    response = client.invoke(service_name, input_dict)

    if response.has_data:
        for item in response.data:
            out.append(StatsElem.from_json(item))

    return out

# ##############################################################################

def _stats_data_csv(user_profile, req_input, client, ignored, stats_type, is_custom, req):

    n_type_keys = {
        'mean': ['start', 'stop', 'service_name', 'mean', 'mean_all_services',
                  'usage_perc_all_services', 'time_perc_all_services', 'all_services_usage', 'mean_trend'],
        'usage': ['start', 'stop', 'service_name', 'usage', 'rate', 'usage_perc_all_services',
                  'time_perc_all_services', 'all_services_usage', 'usage_trend'],
        }

    buff = StringIO()
    writer = DictWriter(buff, n_type_keys[req_input.n_type], extrasaction='ignore')
    writer.writeheader()

    for stat in _get_stats(client, req_input.utc_start, req_input.utc_stop, req_input.n, req_input.n_type, stats_type):
        d = stat.to_dict()
        d['start'] = req_input.user_start
        d['stop'] = req_input.user_stop if stats_type == 'trends' or is_custom else ''
        writer.writerow(d)

    out = buff.getvalue()
    buff.close()

    response = HttpResponse(out, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}'.format('zato-stats.csv')

    return response

def _stats_data_html(user_profile, req_input, client, cluster, stats_type, is_custom, req):

    is_trends = stats_type == 'trends'
    if is_trends:
        data_url = reverse('stats-trends-data')
    else:
        data_url = reverse('stats-summary-data')

    return_data = {
        'has_stats':False,
        'utc_start':req_input.utc_start,
        'utc_stop':req_input.utc_stop,
        'user_start':req_input.user_start,
        'user_stop':req_input.user_stop,
        'is_custom': is_custom,
        'is_trends': is_trends,
    }

    settings = {}

    # We will deal with these ignored keys one by one later on
    ignored_keys = ['format']
    if not is_custom:
        ignored_keys.extend(('utc_start', 'utc_stop'))

    query_data = '&amp;'.join('{}={}'.format(key, value) for key, value in req_input.items() if key not in ignored_keys)

    for name in req_input:
        if name.startswith('orig_'):
            target_name = name.replace('orig_', '')
            query_data += '&amp;{}={}'.format(target_name, req_input[name])

    if req_input.n:
        for name in('atttention_slow_threshold', 'atttention_top_threshold'):
            settings[name] = req.zato.settings_db.get(name, default=DEFAULT_STATS_SETTINGS[name])

    for name in('mean', 'usage'):
        d = {'cluster_id':cluster.id, 'side':req_input.side, 'needs_trends': is_trends}
        if req_input.n:

            stats = _get_stats(client, req_input.utc_start, req_input.utc_stop, req_input.n, name, stats_type)

            # I.e. whether it's not an empty list (assuming both stats will always be available or neither will be)
            return_data['has_stats'] = len(stats)

            return_data['{}_csv_href'.format(name)] = '{}?{}&amp;format=csv&amp;n_type={}&amp;cluster={}'.format(
                data_url, query_data, name, cluster.id)

            d.update({name:stats})
            d.update(settings)

        return_data[name] = loader.render_to_string('zato/stats/trends-table-{}.html'.format(name), d)

    for name in('user_start', 'user_stop'):
        return_data['{}_label'.format(name)] = return_data[name]

    return HttpResponse(dumps(return_data), content_type='application/javascript')

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
        'shift', 'side', 'custom_range'))

    for name in req_input:
        req_input[name] = req.GET.get(name, '') or req.POST.get(name, '')

    # Now, this may look odd but for some reason UTC timestamps submitted
    # in the form of '2012-10-31T21:47:11.592868+00:00' get translated
    # by Django into '2012-10-31T21:47:11.592868+00:00' so the plus sign disappears.
    # We bring it back taking an advantage of the fact that ' 00:00' alone is never
    # a proper string of characters in a UTC timestamp.
    for name in('utc_start', 'utc_stop'):
        req_input[name] = req_input[name].replace(' 00:00', '+00:00')
        req_input['orig_{}'.format(name)] = req_input[name]

    try:
        req_input.n = int(req_input.n)
    except ValueError:
        req_input.n = 0

    req_input.format = req_input.format or 'html'
    is_custom = False

    if req_input.shift:
        duration = skip_by_duration[req_input.shift]
        format = user_format[duration]

        shift_info = shift(parse(req_input.utc_start), req_input.user_start, req.zato.user_profile, req_input.shift, duration, format)

        for date_type in('utc', 'user'):
            for direction in('start', 'stop'):
                full_name = '{}_{}'.format(date_type, direction)
                req_input[full_name] = shift_info[full_name]

    elif req_input.custom_range:
        is_custom = True
        req_input['utc_start'] = utc.fromutc(from_user_to_utc(req_input.user_start, req.zato.user_profile)).isoformat()
        req_input['utc_stop'] = utc.fromutc(from_user_to_utc(req_input.user_stop, req.zato.user_profile)).isoformat()

        req_input['user_start'] = req_input.user_start
        req_input['user_stop'] = req_input.user_stop

    return globals()['_stats_data_{}'.format(req_input.format)](req.zato.user_profile,
        req_input, req.zato.client, req.zato.cluster, stats_type, is_custom, req)

@method_allowed('GET', 'POST')
def stats_trends_data(req):
    return stats_data(req, 'trends')

@method_allowed('GET', 'POST')
def stats_summary_data(req):
    return stats_data(req, '{}{}'.format(SUMMARY_PREFIX, req.POST.get('choice', 'missing-value')))

def trends_summary(req, choice, stats_title, is_summary):
    if choice == 'this_month':
        format = 'month_year'
    elif choice == 'this_year':
        format = 'year'
    else:
        format = 'date'

    info = get_default_date(choice, req.zato.user_profile, format)

    try:
        n = int(req.GET.get('n', 10))
    except ValueError:
        n = 10

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
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'search_form':req.zato.search_form,
        'sample_dt': get_sample_dt(req.zato.user_profile),
        'stats_title': stats_title,
        'step': info.step,
        'needs_stop': choice == 'last_hour',
    }

    return_data.update(get_js_dt_format(req.zato.user_profile))
    return TemplateResponse(req, 'zato/stats/trends_summary.html', return_data)

@method_allowed('GET')
def trends(req, choice):
    return trends_summary(req, choice, 'Trends', False)

@method_allowed('GET')
def summary(req, choice):
    return trends_summary(req, choice, 'Summary', True)

# ##############################################################################

@method_allowed('GET')
def settings(req):

    if req.zato.get('cluster'):

        return_data = {
            'zato_clusters': req.zato.clusters,
            'cluster_id': req.zato.cluster_id,
            'search_form':req.zato.search_form,
        }

        _settings = {}
        defaults = deepcopy(DEFAULT_STATS_SETTINGS)

        for mapping in job_mappings:

            request = {'cluster_id':req.zato.cluster.id, 'name': mapping.job_name}
            try:
                response = req.zato.client.invoke('zato.scheduler.job.get-by-name', request)
            except Exception:
                logger.warn(format_exc())
                return_data['has_scheduler_jobs'] = False
                break
            if response.has_data:

                for attr in mapping.attrs:
                    try:
                        attr.job_attr['extra']
                    except TypeError:
                        setting_base_name = 'scheduler_{}_interval'.format(attr.form_name)
                        setting_unit_name = 'scheduler_{}_interval_unit'.format(attr.form_name)

                        defaults[setting_unit_name] = attr.job_attr
                        _settings[setting_base_name] = getattr(response.data, attr.job_attr)
                    else:
                        # A sample response.data.extra is, for instance, 'max_batch_size=123456'
                        _settings['scheduler_{}'.format(attr.form_name)] = response.data.extra.split('=')[1]

        # No break in the exception handler above means we were able to read in all the scheduler jobs needed
        else:
            return_data['has_scheduler_jobs'] = True

        for name in DEFAULT_STATS_SETTINGS:
            if not name.startswith('scheduler'):
                _settings[name] = req.zato.settings_db.get(name, default=DEFAULT_STATS_SETTINGS[name])
    else:
        defaults, _settings = None, {}

    return_data['form'] = SettingsForm(initial=_settings)
    return_data['defaults'] = defaults

    return TemplateResponse(req, 'zato/stats/settings.html', return_data)

@method_allowed('POST')
def settings_save(req):

    for name in DEFAULT_STATS_SETTINGS:
        if not name.startswith('scheduler'):
            value = req.POST[name]
            req.zato.settings_db.set(name, value)

    for mapping in job_mappings:

        response = req.zato.client.invoke('zato.scheduler.job.get-by-name', {'cluster_id':req.zato.cluster.id, 'name': mapping.job_name})
        if response.has_data:

            # Gotta love dictionary comprehensions!
            params = {attr: getattr(response.data, attr) for attr in(
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

            params['service'] = response.data.service_name
            params['cluster_id'] = req.zato.cluster.id

            req.zato.client.invoke('zato.scheduler.job.edit', params)

    msg = 'Settings saved'
    messages.add_message(req, messages.INFO, msg, extra_tags='success')

    return redirect('{}?cluster={}'.format(reverse('stats-settings'), req.zato.cluster_id))

# ##############################################################################

@method_allowed('GET')
def maintenance(req):
    return_data = {
        'zato_clusters': req.zato.clusters,
        'cluster_id': req.zato.cluster_id,
        'search_form':req.zato.search_form,
        'form': MaintenanceForm()
    }

    return_data.update(get_js_dt_format(req.zato.user_profile))

    return TemplateResponse(req, 'zato/stats/maintenance.html', return_data)

@method_allowed('POST')
def maintenance_delete(req):
    start = from_user_to_utc(req.POST['start'], req.zato.user_profile)
    stop = from_user_to_utc(req.POST['stop'], req.zato.user_profile)

    req.zato.client.invoke('zato.stats.delete', {'start':start, 'stop':stop})

    msg = 'Submitted a request to delete statistics from [{}] to [{}]. Check the server logs for details.'.format(
        from_utc_to_user(start.isoformat() + '+00:00', req.zato.user_profile),
        from_utc_to_user(stop.isoformat() + '+00:00', req.zato.user_profile))

    messages.add_message(req, messages.INFO, msg, extra_tags='success')

    return redirect('{}?cluster={}'.format(reverse('stats-maintenance'), req.zato.cluster_id))

# ##############################################################################
