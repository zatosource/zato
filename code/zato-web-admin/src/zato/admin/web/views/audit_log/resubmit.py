# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# SQLAlchemy
from sqlalchemy import select

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web.views import action_json_response, invoke_action_handler, method_allowed, \
    Action_Message_Max_Length, _traceback_marker
from zato.admin.web.views.audit_log.sources import _source_resubmit
from zato.common.audit_log.api import event_table, get_audit_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# What a resubmit's outcome reads as in the tippy
_resubmit_ok_label    = 'Resubmitted'
_resubmit_error_label = 'Resubmit failed'
_retry_ok_label       = 'Retried'

# What the services call a reprocess and a retry in their reports - a report without
# the action key at all is a per-hop resend
_action_reprocess = 'reprocess'
_action_retry     = 'retry'

# The actions whose message is one fixed label.
_action_ok_label = {
    _action_retry: _retry_ok_label,
}

# ################################################################################################################################

def _get_error_summary(error_text:'str') -> 'str':
    """ The one-line summary of a resubmit error - the last line of the traceback,
    which is the exception itself, capped at what the tippy can show.
    """
    lines = error_text.strip().splitlines()
    out = lines[-1].strip()

    if len(out) > Action_Message_Max_Length:
        out = out[:Action_Message_Max_Length] + ' ..'

    return out

# ################################################################################################################################

def _get_resubmit_message(report:'anydict') -> 'str':
    """ The one-line summary of what a resubmit did, built out of the fields
    its source's report carries.
    """

    # The per-hop resend report carries no action at all
    if 'action' in report:
        action = report['action']
    else:
        action = ''

    if ok_label := _action_ok_label.get(action):
        return ok_label

    if action == _action_reprocess:

        # An AS2 or AS4 reprocess names the routing target the documents landed on ..
        if 'target_name' in report and report['target_name']:
            out = f'{_resubmit_ok_label} to {report["target_kind"]} {report["target_name"]}'

            # .. a multi-attachment delivery routes one message per document,
            # so the operator sees how many actually went out
            if report['message_count'] > 1:
                out = f'{out} ({report["message_count"]} documents)'

            return out

        # .. an HL7 reprocess names the channel's service when it has one ..
        if 'service_name' in report and report['service_name']:
            return f'{_resubmit_ok_label} to service {report["service_name"]}'

        # .. or the destinations the message was aimed at when it does not.
        if 'destinations' in report and report['destinations']:
            names = ', '.join(report['destinations'])
            return f'{_resubmit_ok_label} to {names}'

        return _resubmit_ok_label

    # A resend is reported by the CID its new attempt travels under
    return f'{_resubmit_ok_label}; CID {report["cid"]}'

# ################################################################################################################################

def _get_resubmit_response(report:'anydict') -> 'any_':
    """ The display-ready answer a resubmit gives - a one-line summary for the tippy,
    the details for the modal and the lexer they highlight with. A failure's details
    are the traceback alone, a success's the whole report.
    """
    if report['is_ok']:
        message = _get_resubmit_message(report)
        details = json.dumps(report, indent=2)
        details_lexer = 'json'

    else:
        message = f'{_resubmit_error_label} - {_get_error_summary(report["error"])}'
        details = report['error']

        if _traceback_marker in details:
            details_lexer = 'pytb'
        else:
            details_lexer = 'python'

    out = action_json_response(report['is_ok'], message, details, details_lexer)
    return out

# ################################################################################################################################

@method_allowed('POST')
def resubmit(req:'any_') -> 'HttpResponse':
    """ Resubmits one audit event - a resend for outbound rows, a reprocess for inbound ones,
    performed by the service the event's source registered for that event type.
    The new attempt lands as its own event linked to the original one by CID,
    and the answer is display-ready - the frontend renders it without any string surgery.
    """
    # Form data is always a string while the event id column is numeric
    event_id = int(req.POST['id'])

    # Find which event this is, so the right service can perform the resubmit.
    lookup_query = select(event_table.c.source, event_table.c.event_type).where(event_table.c.id == event_id)
    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(lookup_query)
        row = result.fetchone()

    source, event_type = row

    # Each source declares which of its events are resubmittable and which service performs it.
    actions = _source_resubmit[source]
    action = actions[event_type]

    # Who asked for the resubmit travels with the request, so the new event carries the actor
    response = invoke_action_handler(req, action['service'],
        extra={'event_id': event_id, 'actor': req.user.username})

    # An invocation that never produced a report at all - e.g. the server could not
    # be reached - answers with the exception it was caught with
    if isinstance(response, HttpResponseServerError):
        error_text = response.content.decode('utf-8', 'replace')
        report = {'is_ok': False, 'error': error_text}

    # Every service answers with a report, a failed resubmit included -
    # the outcome and its details are inside
    else:
        report = json.loads(response.content)

    out = _get_resubmit_response(report)
    return out

# ################################################################################################################################
# ################################################################################################################################
