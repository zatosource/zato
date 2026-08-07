# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

What one source can do with its own events - which exchanges of it are open, which of its events
can be resubmitted and by what, and the columns and parsed views it renders out of a payload.
"""

# stdlib
import json
from dataclasses import dataclass

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.admin.web.views.audit_log.columns import _source_event_label
from zato.common.as2.mdn import describe_disposition
from zato.common.audit_log.api import event_table, AuditEvent
from zato.common.hl7.display import parse_and_render

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OutstandingFilter:
    """ The outstanding filter of one source - the event that opens an exchange, the acknowledgment
    that closes it, and whether the close matches on the partner pair too. AS2 MDNs answer
    the Message-ID alone while X12 acknowledgments echo both the pair and the control number.
    """
    open_event: str = ''
    close_event: str = ''
    needs_object_name_match: bool = False

# ################################################################################################################################

def _new_outstanding_filter(open_event:'str', close_event:'str', needs_object_name_match:'bool') -> 'OutstandingFilter':
    out = OutstandingFilter()
    out.open_event = open_event
    out.close_event = close_event
    out.needs_object_name_match = needs_object_name_match

    return out

# ################################################################################################################################

# The sources whose pages carry the outstanding filter pill
_source_outstanding = {
    'as2': _new_outstanding_filter(AuditEvent.Message_Sent, AuditEvent.MDN_Received, False),
    'as4': _new_outstanding_filter(AuditEvent.Message_Sent, AuditEvent.Receipt_Received, True),
    'x12': _new_outstanding_filter(AuditEvent.Interchange_Sent, AuditEvent.Ack_Received, True),
    'hl7': _new_outstanding_filter(AuditEvent.Message_Sent, AuditEvent.Ack_Received, True),
}

# ################################################################################################################################
# ################################################################################################################################

# Per-source resubmit actions - each source declares which of its events are resubmittable,
# how the row action is labelled and which service performs it.
_as2_resubmit = {
    AuditEvent.Message_Sent:     {'label': 'Resend',    'service': 'zato.audit-log.as2.resend'},
    AuditEvent.Message_Received: {'label': 'Reprocess', 'service': 'zato.audit-log.as2.reprocess'},
}

_as4_resubmit = {
    AuditEvent.Message_Sent:     {'label': 'Resend',    'service': 'zato.audit-log.as4.resend'},
    AuditEvent.Message_Received: {'label': 'Reprocess', 'service': 'zato.audit-log.as4.reprocess'},
}

_hl7_resubmit = {
    AuditEvent.Message_Sent:     {'label': 'Resend',    'service': 'zato.audit-log.hl7.resend'},
    AuditEvent.Message_Received: {'label': 'Reprocess', 'service': 'zato.audit-log.hl7.reprocess'},

    # A message a channel fanned out to one of its destinations is repeated per hop, that one
    # delivery going out again without the rest of the destinations being involved
    AuditEvent.Request_Sent:     {'label': 'Resend',    'service': 'zato.audit-log.resend-hop'},
}

# One recorded delivery to one destination is repeated on its own, whatever kind of connection
# it went through - the row says which destination it went to and what repeating it needs.
_hop_resubmit = {
    AuditEvent.Request_Sent: {'label': 'Resend', 'service': 'zato.audit-log.resend-hop'},
}

# The sources whose pages carry resubmit actions
_source_resubmit = {
    'as2': _as2_resubmit,
    'as4': _as4_resubmit,
    'hl7': _hl7_resubmit,
    'fhir': _hop_resubmit,
    'rest-outgoing': _hop_resubmit,
    'email-smtp': _hop_resubmit,
}

# ################################################################################################################################
# ################################################################################################################################

def _enrich_as2_row(row:'anydict') -> 'None':
    """ Extracts the disposition and MIC of an AS2 event out of its JSON data,
    so they render as columns of their own.
    """
    row['disposition'] = ''
    row['mic'] = ''

    data = row['data']
    if not data:
        return

    # A payload that is not JSON, e.g. a raw MIME body, has nothing to extract.
    try:
        details = json.loads(data)
    except ValueError:
        return

    # A message-sent event carries the MIC computed at send time,
    # an mdn-received event carries what the receipt itself reported.
    if mic := details.get('mic'):
        row['mic'] = mic

    if disposition := details.get('disposition'):
        row['disposition'] = describe_disposition(disposition, details['modifier_kind'], details['modifier'])

# ################################################################################################################################

def _enrich_as4_row(row:'anydict') -> 'None':
    """ Extracts the conversation id of an AS4 event out of its JSON data, so it renders as a column
    of its own - one conversation groups the messages of a business exchange that spans several.
    """
    row['conversation_id'] = ''

    data = row['data']
    if not data:
        return

    # A payload that is not JSON has nothing to extract.
    try:
        details = json.loads(data)
    except ValueError:
        return

    # Only the user message events carry a conversation - a receipt refers to one through
    # the message id it echoes.
    if conversation_id := details.get('conversation_id'):
        row['conversation_id'] = conversation_id

# ################################################################################################################################

# Per-source row enrichment - a source with columns extracted out of the event data registers itself here
_source_row_enrich = {
    'as2': _enrich_as2_row,
    'as4': _enrich_as4_row,
}

# ################################################################################################################################

def _get_resubmit_labels(source:'str') -> 'anydict':
    """ Returns the per-event-type labels of this source's resubmit actions,
    which is what tells the frontend which rows get an action link at all.
    """

    # Our response to produce
    out:'anydict' = {}

    if actions := _source_resubmit.get(source):
        for event_type, action in actions.items():
            out[event_type] = action['label']

    return out

# ################################################################################################################################

# ################################################################################################################################

def _render_hl7_parsed(data:'str') -> 'str':
    """ Renders the parsed view of an HL7 payload - the display tree as indented text.
    A payload that does not parse simply has no parsed view.
    """

    # A resubmitted event stores its payload wrapped in JSON, the resubmit convention -
    # the message inside is what parses.
    if data.startswith('{'):
        try:
            wrapper = json.loads(data)
        except ValueError:
            wrapper = {}

        if isinstance(wrapper, dict):
            if payload := wrapper.get('payload'):
                data = payload

    out = parse_and_render(data)
    return out

# ################################################################################################################################

# What each screen a view can happen from is called - a screen the map does not
# know is named by its own code
_screen_label = {
    'audit-log-browser': 'Audit log',
}

# ################################################################################################################################

def _view_source_label(source:'str') -> 'str':
    """ What the viewed event's source is called - by its human name when the catalog
    knows it, by its own code when the log is ahead of this application.
    """
    if source in _source_event_label:
        out = _source_event_label[source]
    else:
        out = source

    return out

# ################################################################################################################################

def render_view_record(engine:'any_', data:'str', event_time_iso:'str') -> 'str':
    """ Renders a view record of the access log as the answer it exists to give - who viewed
    what and when, in business terms. The viewed event is resolved against the event table
    at render time, so the record reads by the message's own coordinates rather than by
    a bare database id. Any other config payload simply has no parsed view.
    """
    try:
        payload = json.loads(data)
    except ValueError:
        return ''

    if not isinstance(payload, dict):
        return ''

    # Only the view records read this way - a config change keeps its raw payload
    if 'viewed_event_id' not in payload:
        return ''

    # What the viewed event calls itself - its object, its source and its own message id
    viewed_query = select(
        event_table.c.object_name, event_table.c.source, event_table.c.msg_id).where(
        event_table.c.id == payload['viewed_event_id'])

    with engine.connect() as connection:
        result = connection.execute(viewed_query)
        viewed_row = result.fetchone()

    lines = []

    # A record written before the payload carried the viewer has no actor in it -
    # the payload is read out of a database older code may have written to
    if 'actor' in payload:
        lines.append(f'Viewed by:  {payload["actor"]}')

    # The viewed event answers for itself while it exists ..
    if viewed_row is not None:
        lines.append(f'Viewed:     {viewed_row[0]} ({_view_source_label(viewed_row[1])})')

        # A message id the viewed event never had is not a line to show
        if viewed_row[2]:
            lines.append(f'Message:    {viewed_row[2]}')

    # .. and one pruned since reads by the coordinates written down at view time
    elif payload['viewed_object_name']:
        viewed_source_label = _view_source_label(payload['viewed_source'])
        lines.append(f'Viewed:     {payload["viewed_object_name"]} ({viewed_source_label})')

    screen = payload['screen']

    if screen in _screen_label:
        screen = _screen_label[screen]

    lines.append(f'Screen:     {screen}')

    # When the reading happened is the view event's own moment - trimmed of its
    # microseconds and offset, and last, the way time reads everywhere on the page
    when = event_time_iso.replace('T', ' ').split('.')[0]
    lines.append(f'When:       {when} UTC')

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

# Per-source parsed renderers - the default is the EDI renderer, which returns
# an empty string for payloads that do not embed an EDI document. The config source
# is not here - its view records resolve against the database and the details view
# calls render_view_record for them itself.
_source_parse = {
    'hl7': _render_hl7_parsed,
}

# ################################################################################################################################
# ################################################################################################################################
