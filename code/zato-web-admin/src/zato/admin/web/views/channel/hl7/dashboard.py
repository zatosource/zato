# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The HL7 channel dashboard - health tiles, the hourly traffic chart and per-channel
# cards. The history comes from the audit database, the live counters and the
# green/amber/red health come from the zato.channel.hl7.get-current-state service.

# stdlib
import json
import logging
from datetime import datetime, timezone

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.audit_log.api import get_audit_engine
from zato.common.defaults import default_cluster_id
from zato.common.hl7.dashboard import derive_live_health, get_channel_dashboard, Default_Range, Health_Unknown, \
    Range_Day, Range_Hours, Range_Label, Range_Month, Range_Quarter, Range_Week

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, dictlist, stranydict

    any_ = any_
    anylist = anylist
    dictlist = dictlist
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The poll endpoint of this page
_poll_url = '/zato/channel/hl7/dashboard/poll/'

# The service the live counters come from
_state_service = 'zato.channel.hl7.get-current-state'

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

def _get_live_channels(req:'any_') -> 'anylist':
    """ Returns the live state of every HL7 MLLP channel, as the server reports it -
    an empty list when no server answered, in which case the page still renders
    the audit history, only the live tiles say the state is unknown.
    """
    try:
        response = req.zato.client.invoke(_state_service, {})
    except Exception as e:
        logger.warning('HL7 dashboard could not read the live channel state: %s', e)
        return []

    if not response.ok:
        logger.warning('HL7 dashboard state call failed: %s', response.details)
        return []

    state = json.loads(response.data['response_data'])

    out = state['channels']
    return out

# ################################################################################################################################

def _merge_live_state(data:'stranydict', live_channels:'anylist') -> 'None':
    """ Folds the live counters and health into the per-channel history rows -
    a channel with history but no live listener still shows its numbers,
    and a live channel with no history yet gets a row of its own.
    """
    rows_by_name = {}

    for row in data['channels']:
        row['live'] = None
        row['health'] = Health_Unknown
        rows_by_name[row['name']] = row

    for channel_state in live_channels:

        name = channel_state['name']

        # A channel the window has no traffic for is still on the board
        if name not in rows_by_name:
            row = {
                'name': name,
                'received': 0,
                'errored': 0,
                'error_rate': 0.0,
                'last_event_iso': '',
                'spark': [],
                'live': None,
                'health': Health_Unknown,
            }
            rows_by_name[name] = row
            data['channels'].append(row)

        row = rows_by_name[name]
        row['live'] = channel_state
        row['health'] = derive_live_health(channel_state)

    # The tiles summarize the health colors
    health_counts = {'green': 0, 'amber': 0, 'red': 0, Health_Unknown: 0}

    for row in data['channels']:
        health_counts[row['health']] += 1

    data['health_counts'] = health_counts

# ################################################################################################################################

def _get_dashboard_data(req:'any_', time_range:'str') -> 'stranydict':
    """ Builds the whole dashboard payload - the audit-database history
    with the live state merged in.
    """
    now = datetime.now(timezone.utc)
    engine = get_audit_engine()

    out = get_channel_dashboard(engine, now, time_range)

    live_channels = _get_live_channels(req)
    _merge_live_state(out, live_channels)

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':
    """ The HL7 channel dashboard page.
    """
    time_range = req.GET.get('range', '')
    time_range = _get_time_range(time_range)

    data = _get_dashboard_data(req, time_range)

    return_data = {
        'cluster_id': default_cluster_id,
        'time_range': time_range,
        'ranges': _get_ranges(),
        'poll_url': _poll_url,
        'dashboard_data': json.dumps(data),
        'zato_clusters': True,
        'zato_template_name': 'zato/channel/hl7/dashboard.html',
    }

    out = TemplateResponse(req, 'zato/channel/hl7/dashboard.html', return_data)

    return out

# ################################################################################################################################

@method_allowed('POST')
def poll(req:'any_') -> 'HttpResponse':
    """ The dashboard data as JSON, for range changes and auto-refresh.
    """
    body = json.loads(req.body)
    time_range = _get_time_range(body['range'])

    data = _get_dashboard_data(req, time_range)

    response_json = json.dumps(data)
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')

    return out

# ################################################################################################################################
# ################################################################################################################################
