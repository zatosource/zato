# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The analytics screens - fixed pages answering fixed questions over the hourly
# aggregate store the rollup maintains. They read the analytics store only,
# never the live tables, and each screen exports its table as CSV too.

# stdlib
import json
import logging
from datetime import datetime, timezone

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.analytics.csv_export import channel_csv, consumer_csv, overview_csv
from zato.common.analytics.query import get_channel, get_consumer, get_overview, Default_Range, Range_Day, Range_Hours, \
    Range_Label, Range_Month, Range_Quarter, Range_Week
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictlist

    # Dummy assignments to satisfy type checkers
    any_ = any_
    dictlist = dictlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The poll endpoints of each screen
_overview_poll_url = '/zato/analytics/poll/'
_channel_poll_url  = '/zato/analytics/channel/poll/'
_consumer_poll_url = '/zato/analytics/consumer/poll/'

# The CSV endpoints of each screen
_overview_csv_url = '/zato/analytics/csv/'
_channel_csv_url  = '/zato/analytics/channel/csv/'
_consumer_csv_url = '/zato/analytics/consumer/csv/'

# ################################################################################################################################
# ################################################################################################################################

def _get_time_range(value:'str') -> 'str':
    """ Validates a time window off the query string - anything unknown means the default.
    """
    if value in Range_Hours:
        out = value
    else:
        out = Default_Range

    return out

# ################################################################################################################################

def _get_ranges() -> 'dictlist':
    """ The window choices of the time-range menu, in their display order.
    """

    # Our response to produce
    out:'dictlist' = []

    for value in (Range_Day, Range_Week, Range_Month, Range_Quarter):
        out.append({'value': value, 'label': Range_Label[value]})

    return out

# ################################################################################################################################

def _json_response(data:'any_') -> 'HttpResponse':
    """ Renders one poll response as JSON.
    """
    response_json = json.dumps(data)
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')

    return out

# ################################################################################################################################

def _csv_response(content:'str', file_name:'str') -> 'HttpResponse':
    """ Renders one screen's table as a CSV download.
    """
    content_bytes = content.encode('utf-8')

    out = HttpResponse(content_bytes, content_type='text/csv')
    out['Content-Disposition'] = f'attachment; filename={file_name}'

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':
    """ The overview - total traffic, error rate, latency and the busiest channels
    and consumers of the window, each linking to its own screen.
    """
    time_range = req.GET.get('range', '')
    time_range = _get_time_range(time_range)

    now = datetime.now(timezone.utc)
    data = get_overview(now, time_range)

    ranges = _get_ranges()
    dashboard_data = json.dumps(data)

    return_data = {
        'cluster_id': default_cluster_id,
        'time_range': time_range,
        'ranges': ranges,
        'poll_url': _overview_poll_url,
        'csv_url': _overview_csv_url,
        'dashboard_data': dashboard_data,
        'zato_clusters': True,
        'zato_template_name': 'zato/analytics/overview.html',
    }

    out = TemplateResponse(req, 'zato/analytics/overview.html', return_data)

    return out

# ################################################################################################################################

@method_allowed('POST')
def index_poll(req:'any_') -> 'HttpResponse':
    """ The overview data as JSON, for range changes and auto-refresh.
    """
    body = json.loads(req.body)
    time_range = _get_time_range(body['range'])

    now = datetime.now(timezone.utc)
    data = get_overview(now, time_range)

    out = _json_response(data)

    return out

# ################################################################################################################################

@method_allowed('GET')
def index_csv(req:'any_') -> 'HttpResponse':
    """ The overview's channel ranking as CSV - the same query the screen runs.
    """
    time_range = req.GET.get('range', '')
    time_range = _get_time_range(time_range)

    now = datetime.now(timezone.utc)
    data = get_overview(now, time_range)

    content = overview_csv(data)
    file_name = f'analytics-overview-{time_range}.csv'

    out = _csv_response(content, file_name)

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def channel(req:'any_') -> 'TemplateResponse':
    """ The per-channel screen - one channel's traffic, errors by source, latency
    and the consumers behind the numbers.
    """
    name = req.GET['name']
    time_range = req.GET.get('range', '')
    time_range = _get_time_range(time_range)

    now = datetime.now(timezone.utc)
    data = get_channel(now, time_range, name)

    ranges = _get_ranges()
    dashboard_data = json.dumps(data)

    return_data = {
        'cluster_id': default_cluster_id,
        'name': name,
        'time_range': time_range,
        'ranges': ranges,
        'poll_url': _channel_poll_url,
        'csv_url': _channel_csv_url,
        'dashboard_data': dashboard_data,
        'zato_clusters': True,
        'zato_template_name': 'zato/analytics/channel.html',
    }

    out = TemplateResponse(req, 'zato/analytics/channel.html', return_data)

    return out

# ################################################################################################################################

@method_allowed('POST')
def channel_poll(req:'any_') -> 'HttpResponse':
    """ The per-channel data as JSON, for range changes and auto-refresh.
    """
    body = json.loads(req.body)

    name = body['name']
    time_range = _get_time_range(body['range'])

    now = datetime.now(timezone.utc)
    data = get_channel(now, time_range, name)

    out = _json_response(data)

    return out

# ################################################################################################################################

@method_allowed('GET')
def channel_csv_export(req:'any_') -> 'HttpResponse':
    """ The per-channel consumer breakdown as CSV - the same query the screen runs.
    """
    name = req.GET['name']
    time_range = req.GET.get('range', '')
    time_range = _get_time_range(time_range)

    now = datetime.now(timezone.utc)
    data = get_channel(now, time_range, name)

    content = channel_csv(data)
    file_name = f'analytics-channel-{name}-{time_range}.csv'

    out = _csv_response(content, file_name)

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def consumer(req:'any_') -> 'TemplateResponse':
    """ The per-consumer screen - everything one credential does across all channels.
    """
    name = req.GET['name']
    time_range = req.GET.get('range', '')
    time_range = _get_time_range(time_range)

    now = datetime.now(timezone.utc)
    data = get_consumer(now, time_range, name)

    ranges = _get_ranges()
    dashboard_data = json.dumps(data)

    return_data = {
        'cluster_id': default_cluster_id,
        'name': name,
        'time_range': time_range,
        'ranges': ranges,
        'poll_url': _consumer_poll_url,
        'csv_url': _consumer_csv_url,
        'dashboard_data': dashboard_data,
        'zato_clusters': True,
        'zato_template_name': 'zato/analytics/consumer.html',
    }

    out = TemplateResponse(req, 'zato/analytics/consumer.html', return_data)

    return out

# ################################################################################################################################

@method_allowed('POST')
def consumer_poll(req:'any_') -> 'HttpResponse':
    """ The per-consumer data as JSON, for range changes and auto-refresh.
    """
    body = json.loads(req.body)

    name = body['name']
    time_range = _get_time_range(body['range'])

    now = datetime.now(timezone.utc)
    data = get_consumer(now, time_range, name)

    out = _json_response(data)

    return out

# ################################################################################################################################

@method_allowed('GET')
def consumer_csv_export(req:'any_') -> 'HttpResponse':
    """ The per-consumer channel breakdown as CSV - the same query the screen runs.
    """
    name = req.GET['name']
    time_range = req.GET.get('range', '')
    time_range = _get_time_range(time_range)

    now = datetime.now(timezone.utc)
    data = get_consumer(now, time_range, name)

    content = consumer_csv(data)
    file_name = f'analytics-consumer-{name}-{time_range}.csv'

    out = _csv_response(content, file_name)

    return out

# ################################################################################################################################
# ################################################################################################################################
