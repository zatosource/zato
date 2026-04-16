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
        response = req.zato.client.invoke('zato.broker.dashboard', {})
        if response.ok:
            raw = response.data
            if isinstance(raw, str):
                data_json = raw
            else:
                data_json = json.dumps(raw)
        else:
            data_json = '{}'
    except Exception as e:
        logger.error('EDA dashboard error: %s', e)
        data_json = '{}'

    return TemplateResponse(req, 'zato/eda/dashboard.html', {
        'cluster_id': cluster_id,
        'dashboard_data': data_json,
        'zato_clusters': True,
        'zato_template_name': 'zato/eda/dashboard.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def poll(req):

    try:
        response = req.zato.client.invoke('zato.broker.dashboard', {})
        if response.ok:
            raw = response.data
            if isinstance(raw, str):
                return HttpResponse(raw, content_type='application/json')
            else:
                return HttpResponse(json.dumps(raw), content_type='application/json')
        else:
            return HttpResponse(
                json.dumps({'error': response.details or 'Error fetching dashboard data'}),
                content_type='application/json',
                status=500,
            )
    except Exception as e:
        logger.error('EDA dashboard poll error: %s', e)
        return HttpResponse(
            json.dumps({'error': str(e)}),
            content_type='application/json',
            status=500,
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET', 'POST')
def import_demo_config(req):

    response = req.zato.client.invoke('zato.server.invoker', {
        'func_name': 'import_demo_eda',
    })

    out = HttpResponse()
    out.content = str(response.data)

    return out

# ################################################################################################################################
# ################################################################################################################################
