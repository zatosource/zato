# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req):

    cluster_id = req.GET.get('cluster', req.GET.get('cluster_id', ''))

    try:
        response = req.zato.client.invoke('zato.scheduler.job.get-current-state', {})
        if response.ok:
            raw = response.data
            if isinstance(raw, str):
                data_json = raw
            else:
                data_json = json.dumps(raw)
        else:
            data_json = '{}'
    except Exception as e:
        logger.error('Scheduler dashboard error: %s', e)
        data_json = '{}'

    return TemplateResponse(req, 'zato/scheduler/dashboard.html', {
        'cluster_id': cluster_id,
        'dashboard_data': data_json,
        'zato_clusters': True,
        'zato_template_name': 'zato/scheduler/dashboard.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def poll(req):

    try:
        response = req.zato.client.invoke('zato.scheduler.job.get-current-state', {})
        if response.ok:
            raw = response.data
            if isinstance(raw, str):
                return HttpResponse(raw, content_type='application/json')
            else:
                return HttpResponse(json.dumps(raw), content_type='application/json')
        else:
            return HttpResponse(
                json.dumps({'error': response.details or 'Error fetching scheduler state'}),
                content_type='application/json',
                status=500,
            )
    except Exception as e:
        logger.error('Scheduler dashboard poll error: %s', e)
        return HttpResponse(
            json.dumps({'error': str(e)}),
            content_type='application/json',
            status=500,
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def job_detail(req, job_id):

    cluster_id = req.GET.get('cluster', req.GET.get('cluster_id', ''))

    job_data = {}
    history_data = []

    try:
        response = req.zato.client.invoke('zato.scheduler.job.get-by-id', {
            'cluster_id': cluster_id or '1',
            'id': job_id,
        })
        if response.ok:
            raw = response.data
            if isinstance(raw, str):
                job_data = json.loads(raw) if raw else {}
            else:
                job_data = raw if raw else {}
    except Exception as e:
        logger.error('Scheduler job detail error: %s', e)

    try:
        response = req.zato.client.invoke('zato.scheduler.job.get-history', {
            'id': job_id,
        })
        if response.ok:
            raw = response.data
            if isinstance(raw, str):
                history_data = json.loads(raw) if raw else []
            elif isinstance(raw, list):
                history_data = raw
            else:
                history_data = list(raw) if raw else []
    except Exception as e:
        logger.error('Scheduler job history error: %s', e)

    try:
        state_response = req.zato.client.invoke('zato.scheduler.job.get-current-state', {})
        if state_response.ok:
            raw = state_response.data
            if isinstance(raw, str):
                state_data = json.loads(raw)
            else:
                state_data = raw or {}

            for j in state_data.get('jobs', []):
                if str(j.get('id')) == str(job_id):
                    job_data['next_fire_utc'] = j.get('next_fire_utc')
                    job_data['in_flight'] = j.get('in_flight')
                    job_data['current_run'] = j.get('current_run')
                    job_data['interval_ms'] = j.get('interval_ms')
                    break
    except Exception as e:
        logger.error('Scheduler job state error: %s', e)

    if isinstance(job_data, dict):
        job_json = json.dumps(job_data)
    else:
        job_json = json.dumps({})

    if isinstance(history_data, list):
        history_json = json.dumps(history_data)
    else:
        history_json = json.dumps([])

    return TemplateResponse(req, 'zato/scheduler/job_detail.html', {
        'cluster_id': cluster_id,
        'job_id': job_id,
        'job_data': job_json,
        'history_data': history_json,
        'zato_clusters': True,
        'zato_template_name': 'zato/scheduler/job_detail.html',
    })

# ################################################################################################################################
# ################################################################################################################################
