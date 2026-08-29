# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

What one source can do with its own events - which exchanges of it are open, which of its events
can be resubmitted and by what, and the columns and parsed views it renders out of a payload.
"""

# stdlib
import json

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.admin.web.views.audit_log.columns import _source_event_label
from zato.common.as2.mdn import describe_disposition
from zato.common.audit_log.api import event_table
from zato.common.audit_log.common import event_attr_table, event_body_table
from zato.common.audit_log.query import source_outstanding
from zato.common.audit_log.resubmit import source_resubmit_actions
from zato.common.audit_log.scheduler import format_duration_ms, Attr_Current_Run, Attr_Delay_Ms, Log_Kinds
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

# The sources whose pages carry the outstanding filter pill
_source_outstanding = source_outstanding

# ################################################################################################################################
# ################################################################################################################################

# The shared catalog of per-source resubmit actions - this page renders
# its per-row actions out of it.
_source_resubmit = source_resubmit_actions

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

def get_resubmit_labels() -> 'anydict':
    """ Returns the per-event-type labels of every source's resubmit actions, keyed by source,
    which is what tells the frontend which rows get an action link at all.
    """

    # Our response to produce
    out:'anydict' = {}

    for source, actions in _source_resubmit.items():
        labels:'anydict' = {}

        for event_type, action in actions.items():
            labels[event_type] = action['label']

        out[source] = labels

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
    """ Renders a log access view record as the answer it exists to give - who viewed
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

def render_scheduler_record(engine:'any_', event_id:'int') -> 'str':
    """ Renders a scheduler run as the story it tells - which job ran what service, how it went
    and what the run said while it was going. The run's own row carries the outcome, duration
    and error, its attrs the run number and delay, and the log lines captured during the run
    are its event body rows, so everything renders here, where the engine is at hand.
    """

    # The run's own row - what ran, when, and how it ended
    run_query = select(
        event_table.c.object_name, event_table.c.endpoint, event_table.c.outcome,
        event_table.c.duration_ms, event_table.c.event_time_iso, event_table.c.data).where(
        event_table.c.id == event_id)

    # The run number and delay ride in the attrs
    attr_query = select(event_attr_table.c.name, event_attr_table.c.value).where(
        event_attr_table.c.event_id == event_id).where(
        event_attr_table.c.name.in_([Attr_Current_Run, Attr_Delay_Ms]))

    # The log lines the run emitted, in the order they were written
    log_query = select(event_body_table.c.data).where(
        event_body_table.c.event_id == event_id).where(
        event_body_table.c.kind.in_(Log_Kinds)).order_by(
        event_body_table.c.id)

    with engine.connect() as connection:
        run_row = connection.execute(run_query).fetchone()
        attr_rows = connection.execute(attr_query).fetchall()
        log_rows = connection.execute(log_query).fetchall()

    if run_row is None:
        return ''

    object_name, endpoint, outcome, duration_ms, event_time_iso, error = run_row

    attrs = {}

    for name, value in attr_rows:
        attrs[name] = value

    lines = []

    lines.append(f'Job:        {object_name}')
    lines.append(f'Service:    {endpoint}')
    lines.append(f'Outcome:    {outcome}')

    if Attr_Current_Run in attrs:
        lines.append(f'Run:        {attrs[Attr_Current_Run]}')

    # A run still going has no duration yet, so the line only shows once there is one
    if duration_ms is not None:
        duration_human = format_duration_ms(duration_ms)
        lines.append(f'Duration:   {duration_human}')

    if Attr_Delay_Ms in attrs:
        delay_ms = int(attrs[Attr_Delay_Ms])
        delay_human = format_duration_ms(delay_ms)
        lines.append(f'Delay:      {delay_human}')

    # When the run started is the event's own moment - trimmed of its microseconds
    # and offset, the way time reads everywhere on the page
    started = event_time_iso.replace('T', ' ').split('.')[0]
    lines.append(f'Started:    {started} UTC')

    # An error the run ended with reads in full, traceback and all
    if error:
        lines.append('')
        lines.append('Error:')
        lines.append(error)

    # The captured log lines follow, one per line, each with its level and moment
    if log_rows:
        lines.append('')
        lines.append('Log:')

        for (log_data,) in log_rows:
            entry = json.loads(log_data)
            when = entry['timestamp_iso'].replace('T', ' ').split('.')[0]
            lines.append(f'{when} {entry["level"]:8} {entry["message"]}')

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

# Per-source parsed renderers - the default is the EDI renderer, which returns
# an empty string for payloads that do not embed an EDI document. The config source
# is not here - its view records resolve against the database and the details view
# calls render_view_record for them itself.
_source_parse = {
    'mllp-channel': _render_hl7_parsed,
    'mllp-outgoing': _render_hl7_parsed,
}

# ################################################################################################################################
# ################################################################################################################################
