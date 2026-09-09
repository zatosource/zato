# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_body_table, event_table
from zato.common.audit_log.common import AuditBody, AuditEvent
from zato.common.audit_log.file_transfer_run import Run_Status_Unchanged, Skip_Reason_Label
from zato.common.audit_log.file_transfer_words import entries_text, run_sentence, skips_text, Decision_Label, Run_Status_Label
from zato.common.audit_log.scheduler import format_duration_ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strlist
    any_ = any_
    anylist = anylist
    stranydict = stranydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The widths of the ledger's columns, a name wider than its column pushes its line out rather than being cut.
_ledger_name_width = 40
_ledger_size_width = 12
_ledger_when_width = 19
_ledger_decision_width = 12

# The width of the label column in a per-file event's lines.
_label_width = 14

# The keys a per-file event lists, in this order, and what each is called.
_file_event_lines = (
    ('schedule', 'Schedule'),
    ('file_name', 'File'),
    ('remote_path', 'Directory'),
    ('service', 'Service'),
    ('attempt', 'Attempt'),
    ('checksum', 'Checksum'),
    ('moved_to', 'Moved to'),
    ('deleted', 'Deleted'),
    ('quarantine_path', 'Quarantined at'),
    ('actor', 'By'),
    ('remote_size', 'Remote size'),
    ('verify_how', 'Verified by'),
    ('mismatch', 'Mismatch'),
    ('note', 'Note'),
)

# The timings a per-file event may carry, each with its word.
_file_event_timings = (
    ('read_ms', 'Read'),
    ('service_ms', 'Service'),
    ('ack_ms', 'Put away'),
    ('verify_ms', 'Verified'),
)

# ################################################################################################################################
# ################################################################################################################################

def _when(event_time_iso:'str') -> 'str':
    """ A moment without its microseconds and offset.
    """
    date_and_time = event_time_iso.replace('T', ' ')
    without_micro = date_and_time.split('.')[0]
    out = without_micro.split('+')[0]
    return out

# ################################################################################################################################

def _time_of_day(event_time_iso:'str') -> 'str':
    """ The time of day of a moment as HH:MM.
    """
    out = event_time_iso[11:16]
    return out

# ################################################################################################################################

def _labelled(label:'str', value:'any_') -> 'str':
    """ One line of a per-file event, the label padded to the label column.
    """
    label_column = f'{label}:'.ljust(_label_width)
    out = f'{label_column}{value}'
    return out

# ################################################################################################################################

def _ledger_header() -> 'str':
    """ The header line of the ledger.
    """
    name = 'Name'.ljust(_ledger_name_width)
    size = 'Size'.rjust(_ledger_size_width)
    modified = 'Modified'.ljust(_ledger_when_width)
    decision = 'Decision'.ljust(_ledger_decision_width)

    out = f'{name}{size}  {modified}  {decision}Reason'
    return out

# ################################################################################################################################

def _ledger_reason(record:'stranydict') -> 'str':
    """ The reason column of one ledger record.
    """
    reason = record['reason']

    if reason_word := Skip_Reason_Label.get(reason):
        reason = reason_word

    # A taken entry says how long it took rather than why.
    if duration_ms := record['duration_ms']:
        reason = format_duration_ms(duration_ms)

    if attempt := record['attempt']:
        reason = f'{reason}, attempt {attempt}'

    if file_cid := record['file_cid']:
        reason = f'{reason}  ({file_cid})'

    return reason

# ################################################################################################################################

def _ledger_lines(records:'anylist') -> 'strlist':
    """ The ledger as aligned columns.
    """
    out:'strlist' = []

    header = _ledger_header()
    out.append(header)

    for record in records:

        decision = record['decision']

        if decision_word := Decision_Label.get(decision):
            decision = decision_word

        reason = _ledger_reason(record)

        name = record['name'].ljust(_ledger_name_width)
        size = str(record['size']).rjust(_ledger_size_width)
        modified = _when(record['last_modified_iso']).ljust(_ledger_when_width)
        decision = decision.ljust(_ledger_decision_width)

        line = f'{name}{size}  {modified}  {decision}{reason}'
        out.append(line.rstrip())

    return out

# ################################################################################################################################

def _run_header(details:'stranydict', duration_ms:'any_') -> 'str':
    """ The header line of a run.
    """
    schedule = details['schedule']
    directory = details['remote_path']
    current_run = details['current_run']

    out = f'Run {current_run} of {schedule} on {directory}'

    if duration_ms is not None:
        duration = format_duration_ms(duration_ms)
        out = f'{out}, {duration}'

    if (entries := details.get('entries')) is not None:
        entries_word = entries_text(entries)
        out = f'{out}, {entries_word}'

    if (taken := details.get('taken')) is not None:
        out = f'{out}, {taken} taken'

    return out

# ################################################################################################################################

def _run_lines(details:'stranydict', status:'str', duration_ms:'any_', event_time_iso:'str', ledger:'anylist') -> 'strlist':
    """ A run as its header, sentence, skips and ledger.
    """
    out:'strlist' = []

    header = _run_header(details, duration_ms)
    out.append(header)

    status_word = status

    if status_label := Run_Status_Label.get(status):
        status_word = status_label

    # An unchanged run says which earlier run it repeats.
    since_text = ''

    if status == Run_Status_Unchanged:
        since_text = _time_of_day(details['unchanged_since_iso'])

    sentence = run_sentence(details, status, since_text)
    started = _when(event_time_iso)

    out.append(f'Status:     {status_word}')
    out.append(f'Summary:    {sentence}')
    out.append(f'Started:    {started} UTC')

    if status == Run_Status_Unchanged:
        since_event_id = details['unchanged_since_event_id']
        since_when = _when(details['unchanged_since_iso'])
        out.append(f'Repeats:    run event {since_event_id}, listed at {since_when} UTC')

    if skip_reasons := details.get('skip_reasons'):
        skips = skips_text(skip_reasons)
        out.append(f'Skipped:    {skips}')

    if note := details.get('note'):
        out.append(f'Note:       {note}')

    if error := details.get('error'):
        out.append('')
        out.append('Error:')
        out.append(error)

    if ledger:
        out.append('')
        out.append('Ledger:')
        out.extend(_ledger_lines(ledger))

        if ledger_overflow := details.get('ledger_overflow'):
            overflow_word = entries_text(ledger_overflow)
            out.append(f'.. and {overflow_word} more')

    return out

# ################################################################################################################################

def _file_lines(details:'stranydict', event_type:'str', outcome:'str', status:'str', duration_ms:'any_', event_time_iso:'str') -> 'strlist':
    """ A per-file event as its file, place, timings and outcome.
    """
    out:'strlist' = []

    for key, label in _file_event_lines:
        if (value := details.get(key, '')) != '':
            out.append(_labelled(label, value))

    out.append(_labelled('Event', event_type))

    if outcome:
        out.append(_labelled('Outcome', outcome))

    if status:
        out.append(_labelled('Status', status))

    if duration_ms is not None:
        duration = format_duration_ms(duration_ms)
        out.append(_labelled('Duration', duration))

    for key, label in _file_event_timings:
        if timing_ms := details.get(key):
            timing = format_duration_ms(timing_ms)
            out.append(_labelled(label, timing))

    if seen_before_event_id := details.get('seen_before_event_id'):
        seen_when = _when(details['seen_before_iso'])
        seen_name = details['seen_before_file_name']
        seen_before = f'the same content was delivered at {seen_when} UTC as {seen_name} (event {seen_before_event_id})'
        out.append(_labelled('Seen before', seen_before))

    if (attempts := details.get('attempts')) is not None:
        out.append(_labelled('Attempts', attempts))

    when = _when(event_time_iso)
    out.append(_labelled('When', f'{when} UTC'))

    if error := details.get('error'):
        out.append('')
        out.append('Error:')
        out.append(error)

    return out

# ################################################################################################################################

def _read_event(engine:'any_', event_id:'int') -> 'tuple':
    """ The event's columns and its most recent ledger body row.
    """
    is_event = event_table.c.id == event_id

    event_query = select(
        event_table.c.event_type,
        event_table.c.outcome,
        event_table.c.status,
        event_table.c.duration_ms,
        event_table.c.event_time_iso,
        event_table.c.data,
    )
    event_query = event_query.where(is_event)

    is_ledger_of_event = event_body_table.c.event_id == event_id
    is_ledger = event_body_table.c.kind == AuditBody.Run_Ledger
    newest_first = event_body_table.c.id.desc()

    ledger_query = select(event_body_table.c.data)
    ledger_query = ledger_query.where(is_ledger_of_event)
    ledger_query = ledger_query.where(is_ledger)
    ledger_query = ledger_query.order_by(newest_first)
    ledger_query = ledger_query.limit(1)

    with engine.connect() as connection:
        event_row = connection.execute(event_query).fetchone()
        ledger_row = connection.execute(ledger_query).fetchone()

    return event_row, ledger_row

# ################################################################################################################################

def render_file_transfer_record(engine:'any_', event_id:'int') -> 'str':
    """ Renders a file transfer event, a run with its ledger or a single file with its timings.
    """
    event_row, ledger_row = _read_event(engine, event_id)

    if not event_row:
        return ''

    event_type, outcome, status, duration_ms, event_time_iso, data = event_row

    if not data:
        return ''

    details = json.loads(data)

    ledger:'anylist' = []

    if ledger_row:
        ledger = json.loads(ledger_row[0])

    if event_type == AuditEvent.Run_Completed:
        lines = _run_lines(details, status, duration_ms, event_time_iso, ledger)
    else:
        lines = _file_lines(details, event_type, outcome, status, duration_ms, event_time_iso)

    out = '\n'.join(lines)
    return out

# ################################################################################################################################
# ################################################################################################################################
