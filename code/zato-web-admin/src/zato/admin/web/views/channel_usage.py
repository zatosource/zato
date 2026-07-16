# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.audit_log.api import Retention_Days
from zato.common.audit_log.reports import Default_Range, Range_Day, Range_Hours, Range_Month, Range_Week
from zato.common.audit_log.usage import get_usage, usage_csv
from zato.common.defaults import default_cluster_id
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dictlist
    any_ = any_
    dictlist = dictlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# What each report range is called on the page - the widest one is the audit log's
# own retention window rather than any fixed period.
_range_label = {
    Range_Day:   'Last 24 hours',
    Range_Week:  'Last 7 days',
    Range_Month: f'Retention window ({Retention_Days} days)',
}

# ################################################################################################################################
# ################################################################################################################################

def _get_report_filters(req:'any_') -> 'any_':
    """ Reads the report filters off the query string - an unknown or absent range
    means the default one and the channel filter is optional.
    """
    if time_range := req.GET.get('range'):
        if time_range not in Range_Hours:
            time_range = Default_Range
    else:
        time_range = Default_Range

    if channel := req.GET.get('channel'):
        channel = channel.strip()
    else:
        channel = ''

    out = time_range, channel
    return out

# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':
    """ The channel usage page - who calls which channel and how often, over the data
    the audit log already holds, filterable by channel and date range, with each row
    linking back to the filtered audit log page. This is what deciding to retire
    a deprecated channel runs on.
    """
    time_range, channel = _get_report_filters(req)

    now = utcnow()

    rows = get_usage(now, time_range, channel)

    # The range choices of the filter form, in their display order
    ranges:'dictlist' = []

    for value in (Range_Day, Range_Week, Range_Month):
        ranges.append({'value': value, 'label': _range_label[value]})

    return_data = {
        'cluster_id': default_cluster_id,
        'time_range': time_range,
        'channel': channel,
        'ranges': ranges,
        'rows': rows,
        'zato_clusters': True,
        'zato_template_name': 'zato/channel-usage.html',
    }

    out = TemplateResponse(req, 'zato/channel-usage.html', return_data)

    return out

# ################################################################################################################################

@method_allowed('GET')
def index_csv(req:'any_') -> 'HttpResponse':
    """ The usage table as CSV - the same query the page runs, returned as text/csv.
    """
    time_range, channel = _get_report_filters(req)

    now = utcnow()

    rows = get_usage(now, time_range, channel)

    content = usage_csv(rows)
    content_bytes = content.encode('utf-8')

    out = HttpResponse(content_bytes, content_type='text/csv')
    out['Content-Disposition'] = f'attachment; filename=channel-usage-{time_range}.csv'

    return out

# ################################################################################################################################
# ################################################################################################################################
