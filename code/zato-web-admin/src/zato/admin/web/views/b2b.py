# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
from http.client import BAD_REQUEST

# Django
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.audit_log.api import Retention_Days
from zato.common.audit_log.reports import ack_discipline_csv, get_ack_discipline, get_outcomes, get_volume, outcomes_csv, \
     volume_csv, Default_Range, Range_Day, Range_Hours, Range_Month, Range_Week
from zato.common.defaults import default_cluster_id
from zato.common.util.api import utcnow
from zato.x12.control import ControlNumberStore, Kind_Group, Kind_Interchange, Kind_Transaction_Set, Max_Control_Number, \
     get_control_db_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, dictlist
    anydict = anydict
    dictlist = dictlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# What each control number kind is called on the page
_kind_label = {
    Kind_Interchange: 'Interchange',
    Kind_Group: 'Group',
    Kind_Transaction_Set: 'Transaction set',
}

# ################################################################################################################################
# ################################################################################################################################

# What each report range is called on the page - the widest one is the audit log's
# own retention window rather than any fixed period.
_range_label = {
    Range_Day:   'Last 24 hours',
    Range_Week:  'Last 7 days',
    Range_Month: f'Retention window ({Retention_Days} days)',
}

# Each exportable table maps to the query the page runs and its CSV renderer
_csv_tables:'anydict' = {
    'volume':   (get_volume, volume_csv),
    'outcomes': (get_outcomes, outcomes_csv),
    'acks':     (get_ack_discipline, ack_discipline_csv),
}

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def control_numbers(req:'any_') -> 'TemplateResponse':
    """ The X12 control numbers page - one row per sender-receiver pair
    and control number level.
    """

    # The rows the page shows
    rows:'anylist' = []

    # The store lives in a file shared with the servers - the listing is read directly from it.
    store = ControlNumberStore(get_control_db_path())

    try:
        for item in store.get_sequences():
            rows.append({
                'sender': item.sender,
                'receiver': item.receiver,
                'kind': item.kind,
                'kind_label': _kind_label[item.kind],
                'next_number': item.next_number,
                'last_used': item.last_used,
                'last_used_time': item.last_used_time,
            })
    finally:
        store.close()

    return_data = {
        'cluster_id': default_cluster_id,
        'rows': rows,
        'zato_clusters': True,
        'zato_template_name': 'zato/b2b-control-numbers.html',
    }

    return TemplateResponse(req, 'zato/b2b-control-numbers.html', return_data)

# ################################################################################################################################

@method_allowed('POST')
def set_next(req:'any_') -> 'JsonResponse':
    """ Repositions one sequence so its next number is the one given on input.
    """
    body = json.loads(req.body)

    sender = body['sender']
    receiver = body['receiver']
    kind = body['kind']
    next_number = body['next_number']

    # The number arrives from a text input, so it is validated at this boundary.
    try:
        next_number = int(next_number)
    except ValueError:
        return JsonResponse({'is_ok': False, 'message': 'Next number must be an integer'}, status=400)

    if next_number < 1 or next_number > Max_Control_Number:
        message = 'Next number must be between 1 and {}'.format(Max_Control_Number)
        return JsonResponse({'is_ok': False, 'message': message}, status=400)

    store = ControlNumberStore(get_control_db_path())

    try:
        store.set_next(sender, receiver, kind, next_number)
    finally:
        store.close()

    return JsonResponse({'is_ok': True, 'message': 'Next number saved', 'next_number': next_number})

# ################################################################################################################################
# ################################################################################################################################

def _get_report_filters(req:'any_') -> 'any_':
    """ Reads the report filters off the query string - an unknown or absent range
    means the default one and the partner filter is optional.
    """
    if time_range := req.GET.get('range'):
        if time_range not in Range_Hours:
            time_range = Default_Range
    else:
        time_range = Default_Range

    if partner := req.GET.get('partner'):
        partner = partner.strip()
    else:
        partner = ''

    out = time_range, partner
    return out

# ################################################################################################################################

@method_allowed('GET')
def reports(req:'any_') -> 'TemplateResponse':
    """ The B2B reports page - volume, outcomes and acknowledgment discipline tables
    over the data the audit log already holds, filterable by partner and date range,
    with each aggregate row linking back to the filtered audit log page.
    """
    time_range, partner = _get_report_filters(req)

    now = utcnow()

    volume_rows = get_volume(now, time_range, partner)
    outcome_rows = get_outcomes(now, time_range, partner)
    ack_rows = get_ack_discipline(now, time_range, partner)

    # The range choices of the filter form, in their display order
    ranges:'dictlist' = []

    for value in (Range_Day, Range_Week, Range_Month):
        ranges.append({'value': value, 'label': _range_label[value]})

    return_data = {
        'cluster_id': default_cluster_id,
        'time_range': time_range,
        'partner': partner,
        'ranges': ranges,
        'volume_rows': volume_rows,
        'outcome_rows': outcome_rows,
        'ack_rows': ack_rows,
        'zato_clusters': True,
        'zato_template_name': 'zato/b2b-reports.html',
    }

    return TemplateResponse(req, 'zato/b2b-reports.html', return_data)

# ################################################################################################################################

@method_allowed('GET')
def reports_csv(req:'any_') -> 'HttpResponse':
    """ One report table as CSV - the same query the page runs, returned as text/csv.
    """
    table = req.GET['table']

    # The table name arrives from a query string, so it is validated at this boundary.
    if table_entry := _csv_tables.get(table):
        get_rows, to_csv = table_entry
    else:
        return HttpResponse(b'Unknown table', status=BAD_REQUEST)

    time_range, partner = _get_report_filters(req)

    now = utcnow()

    rows = get_rows(now, time_range, partner)

    content = to_csv(rows)
    content_bytes = content.encode('utf-8')

    out = HttpResponse(content_bytes, content_type='text/csv')
    out['Content-Disposition'] = f'attachment; filename=b2b-{table}-{time_range}.csv'

    return out

# ################################################################################################################################
# ################################################################################################################################
