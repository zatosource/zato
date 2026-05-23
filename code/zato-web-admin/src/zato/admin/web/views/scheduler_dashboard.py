# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

dashboard_base_url = '/zato/scheduler/dashboard/'
default_time_range_minutes = 0

_calendar_ranges = {
    1440: 'today',
    2880: 'yesterday',
    10080: 'this_week',
    43200: 'this_month',
    525600: 'this_year',
}

# ################################################################################################################################
# ################################################################################################################################

def _chart_window_for_range(now:'datetime', range_minutes:'int') -> 'tuple':
    """ Computes (chart_since_iso, chart_until_iso) matching the JS _get_chart_window logic. """

    if range_minutes in _calendar_ranges:
        calendar_key = _calendar_ranges[range_minutes]
    else:
        calendar_key = None

    if calendar_key == 'today':
        since = now.replace(hour=0, minute=0, second=0, microsecond=0)
        until = since + timedelta(days=1)
    elif calendar_key == 'yesterday':
        until = now.replace(hour=0, minute=0, second=0, microsecond=0)
        since = until - timedelta(days=1)
    elif calendar_key == 'this_week':
        days_since_monday = now.weekday()
        since = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        until = since + timedelta(days=7)
    elif calendar_key == 'this_month':
        since = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            until = since.replace(year=now.year + 1, month=1)
        else:
            until = since.replace(month=now.month + 1)
    elif calendar_key == 'this_year':
        since = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        until = since.replace(year=now.year + 1)
    else:
        since = now - timedelta(minutes=range_minutes)
        until = now

    chart_since_iso = since.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    chart_until_iso = until.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    return chart_since_iso, chart_until_iso

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req):

    range_minutes = int(req.GET['range'])

    try:
        now = datetime.now(timezone.utc)

        invoke_kwargs = {}
        if range_minutes > 0:
            chart_since_iso, chart_until_iso = _chart_window_for_range(now, range_minutes)
            invoke_kwargs['chart_since_iso'] = chart_since_iso
            invoke_kwargs['chart_until_iso'] = chart_until_iso

        response = req.zato.client.invoke('zato.scheduler.job.get-current-state', invoke_kwargs)
        if response.ok:
            data_json = json.dumps(response.data)
        else:
            data_json = '{}'
    except Exception as e:
        logger.error('Scheduler dashboard error: %s', e)
        data_json = '{}'

    return TemplateResponse(req, 'zato/scheduler/dashboard.html', {
        'cluster_id': default_cluster_id,
        'range_minutes': range_minutes,
        'dashboard_data': data_json,
        'dashboard_base_url': dashboard_base_url,
        'zato_clusters': True,
        'zato_template_name': 'zato/scheduler/dashboard.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def poll(req):

    try:
        chart_since_iso = req.POST.get('chart_since_iso', '')
        chart_until_iso = req.POST.get('chart_until_iso', '')
        recent_since_iso = req.POST.get('recent_since_iso', '')

        t0 = time.monotonic()
        response = req.zato.client.invoke('zato.scheduler.job.get-current-state', {
            'chart_since_iso': chart_since_iso,
            'chart_until_iso': chart_until_iso,
            'recent_since_iso': recent_since_iso,
        })
        elapsed = time.monotonic() - t0
        if elapsed > 2.0:
            logger.warning('Scheduler dashboard poll invoke took %.1fs', elapsed)

        if response.ok:
            data = response.data

            # .. regression guard - warn if incremental mode returned too many recent events ..
            if recent_since_iso:
                recent_count = len(data.get('recent_events') or [])
                if recent_count > 500:
                    logger.warning('Scheduler poll regression: recent_since_iso was set but got %d recent_events', recent_count)

            return HttpResponse(json.dumps(data), content_type='application/json')

        # .. otherwise return the error details.
        else:
            return HttpResponse(
                json.dumps({'error': response.details}),
                content_type='application/json',
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
    except Exception as e:
        logger.error('Scheduler dashboard poll error: %s', e)
        return HttpResponse(
            json.dumps({'error': str(e)}),
            content_type='application/json',
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def job_detail(req, job_id:'int'):

    range_minutes = int(req.GET['range'])

    job_data = {}

    try:
        response = req.zato.client.invoke('zato.scheduler.job.get-by-id', {
            'cluster_id': default_cluster_id,
            'id': job_id,
        })
        if response.ok:
            job_data = response.data
    except Exception as e:
        logger.error('Scheduler job detail error: %s', e)

    try:
        state_response = req.zato.client.invoke('zato.scheduler.job.get-current-state', {})
        if state_response.ok:
            state_data = state_response.data
            job_name = job_data['name']

            for entry in state_data['jobs']:
                if entry['id'] == job_id or entry['name'] == job_name:
                    job_data['next_fire_utc'] = entry['next_fire_utc']
                    job_data['is_running'] = entry['is_running']
                    job_data['current_run'] = entry['current_run']
                    job_data['interval_ms'] = entry['interval_ms']
                    job_data['recent_outcomes'] = entry['recent_outcomes']
                    job_data['last_outcome'] = entry['last_outcome']
                    job_data['last_duration_ms'] = entry['last_duration_ms']
                    break

    except Exception as e:
        logger.error('Scheduler job state error: %s', e)

    return TemplateResponse(req, 'zato/scheduler/job_detail.html', {
        'cluster_id': default_cluster_id,
        'range_minutes': range_minutes,
        'job_id': job_id,
        'job_data': json.dumps(job_data),
        'dashboard_base_url': dashboard_base_url,
        'poll_url': '/zato/dashboard/detail-poll/',
        'zato_clusters': True,
        'zato_template_name': 'zato/scheduler/job_detail.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def run_detail(req, job_id:'int', run_number:'int'):
    """ Shows the log entries for a single execution record of a scheduler job.
    """

    range_minutes = int(req.GET['range'])

    job_data = {}

    try:
        response = req.zato.client.invoke('zato.scheduler.job.get-by-id', {
            'cluster_id': default_cluster_id,
            'id': job_id,
        })
        if response.ok:
            job_data = response.data
    except Exception as e:
        logger.error('Scheduler run detail error: %s', e)

    return TemplateResponse(req, 'zato/scheduler/run_detail.html', {
        'cluster_id': default_cluster_id,
        'range_minutes': range_minutes,
        'job_id': job_id,
        'run_number': run_number,
        'job_data': json.dumps(job_data),
        'dashboard_base_url': dashboard_base_url,
        'poll_url': '/zato/dashboard/detail-poll/',
        'zato_clusters': True,
        'zato_template_name': 'zato/scheduler/run_detail.html',
    })

# ################################################################################################################################
# ################################################################################################################################
