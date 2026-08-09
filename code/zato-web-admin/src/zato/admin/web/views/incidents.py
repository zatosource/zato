# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import invoke_action_handler, method_allowed
from zato.common.api import Incidents
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpResponse
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The listing's tabs, in the order they show, one per status plus one with everything.
_listing_tabs = (
    (Incidents.Status.Awaiting_Approval, 'Awaiting approval'),
    (Incidents.Status.Approved, 'Approved'),
    (Incidents.Status.Rejected, 'Rejected'),
    (Incidents.Status.Resolved, 'Resolved'),
    ('all', 'All'),
)

# Which service each decision action invokes.
_action_services = {
    'approve': 'zato.incidents.approve',
    'reject': 'zato.incidents.reject',
    'resubmit': 'zato.incidents.resubmit',
}

# ################################################################################################################################
# ################################################################################################################################

def _format_time(time_iso:'str') -> 'str':
    """ An ISO timestamp reduced to what the screens show - the date and the time down to seconds.
    """
    out = time_iso[:19].replace('T', ' ')
    return out

# ################################################################################################################################

@method_allowed('GET')
def index(req:'any_') -> 'TemplateResponse':
    """ The incidents listing - one tab per status plus one with everything.
    """
    response = req.zato.client.invoke('zato.incidents.get-list', {
        'cluster_id': default_cluster_id,
    })

    items = []

    if response.ok:
        data = json.loads(response.data['response_data'])

        for item in data['items']:
            item['created_display'] = _format_time(item['created_iso'])
            items.append(item)

    # One tab per status, with everything in the last one.
    tabs = []

    for value, label in _listing_tabs:

        if value == 'all':
            tab_items = items
        else:
            tab_items = [item for item in items if item['status'] == value]

        tabs.append({
            'name': value,
            'label': label,
            'items': tab_items,
            'count': len(tab_items),
        })

    return TemplateResponse(req, 'zato/incidents/index.html', {
        'cluster_id': default_cluster_id,
        'tabs': tabs,
        'default_tab': Incidents.Status.Awaiting_Approval,
        'zato_clusters': True,
        'zato_template_name': 'zato/incidents/index.html',
    })

# ################################################################################################################################

@method_allowed('GET')
def detail(req:'any_', name:'str') -> 'TemplateResponse':
    """ One incident in full - the diagnosis, the evidence and the history,
    with the decision buttons for the statuses that allow them.
    """
    response = req.zato.client.invoke('zato.incidents.get', {
        'cluster_id': default_cluster_id,
        'name': name,
    })

    incident = None

    if response.ok:
        data = json.loads(response.data['response_data'])
        incident = data['incident']

    if incident:

        incident['created_display'] = _format_time(incident['created_iso'])

        for entry in incident['history']:
            entry['time_display'] = _format_time(entry['time_iso'])

        for event in incident['evidence']['audit_trail']:
            event['time_display'] = _format_time(event['event_time_iso'])

        # The connection's configuration displays as sorted key/value rows.
        config_rows = []

        for key in sorted(incident['evidence']['connection']):
            config_rows.append({'key': key, 'value': incident['evidence']['connection'][key]})

    else:
        config_rows = []

    # Which buttons the status allows.
    is_awaiting = bool(incident) and incident['status'] == Incidents.Status.Awaiting_Approval
    can_resubmit = bool(incident) and incident['status'] in (Incidents.Status.Awaiting_Approval, Incidents.Status.Approved)

    return TemplateResponse(req, 'zato/incidents/detail.html', {
        'cluster_id': default_cluster_id,
        'name': name,
        'incident': incident,
        'config_rows': config_rows,
        'is_awaiting': is_awaiting,
        'can_resubmit': can_resubmit,
        'auto_action': req.GET.get('action', ''),
        'zato_clusters': True,
        'zato_template_name': 'zato/incidents/detail.html',
    })

# ################################################################################################################################

@method_allowed('POST')
def action(req:'any_') -> 'HttpResponse':
    """ Runs one decision - approve, reject or resubmit - through the matching service,
    with the Dashboard user as the actor.
    """
    action_name = req.POST['action']
    service_name = _action_services[action_name]

    extra = {
        'name': req.POST['name'],
        'actor': req.user.username,
    }

    if reason := req.POST.get('reason'):
        extra['reason'] = reason

    out = invoke_action_handler(req, service_name, extra=extra)
    return out

# ################################################################################################################################
# ################################################################################################################################
