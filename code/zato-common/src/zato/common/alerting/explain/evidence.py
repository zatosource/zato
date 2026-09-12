# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The evidence document one alert is explained from - four sections a skill teaches the LLM
# to read. Alert says what fired and what it measured against what, Object describes the
# connection without its secrets, Failures lists the rows the measure was counted from,
# grouped by identical error text and fitted to a budget, and Baseline says how the object
# fared around them. The document is plain markdown so the skill's instructions can name
# its sections and a person can read what the LLM read.

from __future__ import annotations

# stdlib
from datetime import timedelta

# Zato
from zato.common.alerting.collectors.common import response_event_type_by_source, Window_Seconds_By_Measure_Key
from zato.common.audit_log.common import get_source_label
from zato.common.util.api import pluralize

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import anylist, dictlist, stranydict, strlist, strtuple
    anylist = anylist
    datetime = datetime
    dictlist = dictlist
    stranydict = stranydict
    strlist = strlist
    strtuple = strtuple

# ################################################################################################################################
# ################################################################################################################################

# How long the whole document may be - the Failures section is what gives way when it would be longer.
Evidence_Budget_Chars = 12000

# What is kept of an error text when the texts have to be trimmed - its head and its tail,
# because the beginning names the error and the end often names the path or the host.
Error_Text_Head_Chars = 400
Error_Text_Tail_Chars = 200

# How many files a group lists in full before it lists only its first and last ones.
Max_Files_Per_Group = 6

# How long a single error text may be when it is first read - anything past this is noise.
Error_Text_Max_Chars = 2000

# What joins the head and the tail of a trimmed text.
_trim_marker = ' ... '

# What a group's names are called - a file transfer's rows name files, a channel's rows name the services
# that answered and the callers that asked.
Label_File = 'File'
Label_Files = 'Files'
Label_Service = 'Service'
Label_Services = 'Services'
Label_Caller = 'Caller'
Label_Callers = 'Callers'

# What joins a channel row's status line and its error text into one group key.
_status_separator = ' - '

# The section headings, in the order the skill reads them.
Heading_Evidence = '# Evidence'
Heading_Alert    = '## Alert'
Heading_Object   = '## Object'
Heading_Failures = '## Failures'
Heading_Baseline = '## Baseline'

# What the Failures section says of itself before its groups.
_failures_intro = 'Newest first. Identical errors are grouped, the count says how many times each occurred in the window.'

# What the Failures section says when there is nothing in it.
_no_failures = 'No failed events in the window.'

# The fact's keys that name the object or the window rather than measure anything.
_non_measure_keys = ('source', 'object_name', 'window_seconds', 'last_error_event_id', 'is_resubmittable',
    Window_Seconds_By_Measure_Key)

# ################################################################################################################################
# ################################################################################################################################

def is_channel_source(source:'str') -> 'bool':
    """ Whether a source's rows are the calls a channel received - their names are services and callers, not files.
    """
    out = source in response_event_type_by_source
    return out

# ################################################################################################################################

def _error_text(row:'stranydict') -> 'str':
    """ What a row says went wrong - its data when it has any, its status otherwise,
    its event type when it has neither.
    """
    if row['data']:
        out = row['data']
    elif row['status']:
        out = row['status']
    else:
        out = row['event_type']

    out = out.strip()

    if len(out) > Error_Text_Max_Chars:
        out = out[:Error_Text_Max_Chars]

    return out

# ################################################################################################################################

def _channel_error_text(row:'stranydict') -> 'str':
    """ What a channel's row says went wrong - its status line first, because a 401 and a 500 with one
    text are two different failures, and its error text after it when it has one of its own.
    """
    out = _error_text(row)

    if row['status']:
        if out != row['status']:
            out = row['status'] + _status_separator + out

    return out

# ################################################################################################################################

def _add_once(names:'strlist', name:'str') -> 'None':
    """ Adds a name to a list unless it is empty or already there.
    """
    if not name:
        return

    if name in names:
        return

    names.append(name)

# ################################################################################################################################

def group_failures(rows:'dictlist', source:'str'='') -> 'dictlist':
    """ The rows grouped by identical error text - each group with its count, the time of its
    first and its last row and the files or endpoints it touched, the groups in the order of
    their newest rows, newest first, which is the order the rows arrive in. A channel's rows
    are grouped by their status line and error text together, and each group also collects
    the callers whose calls it holds, each caller once.
    """
    by_text:'dict[str, stranydict]' = {}
    is_channel = is_channel_source(source)

    for row in rows:

        if is_channel:
            text = _channel_error_text(row)
        else:
            text = _error_text(row)

        if text not in by_text:
            by_text[text] = {
                'text': text,
                'count': 0,
                'first_iso': row['event_time_iso'],
                'last_iso': row['event_time_iso'],
                'files': [],
                'files_total': 0,
                'callers': [],
            }

        group = by_text[text]
        group['count'] += 1

        # The rows arrive newest first, so the first row seen is the newest and every later one is older
        group['first_iso'] = row['event_time_iso']

        # A file is named each time it failed, a service and a caller once each
        if is_channel:
            _add_once(group['files'], row['endpoint'])
            _add_once(group['callers'], row['ext_client_id'])
            group['files_total'] = len(group['files'])

        elif row['endpoint']:
            group['files'].append(row['endpoint'])
            group['files_total'] += 1

    # Our response to produce
    out = list(by_text.values())

    return out

# ################################################################################################################################

def _trim_text(text:'str') -> 'str':
    """ The head and the tail of a text that is longer than both together.
    """
    if len(text) <= Error_Text_Head_Chars + Error_Text_Tail_Chars:
        return text

    out = text[:Error_Text_Head_Chars] + _trim_marker + text[-Error_Text_Tail_Chars:]
    return out

# ################################################################################################################################

def _format_names(names:'strlist', names_total:'int', is_collapsed:'bool', one:'str', many:'str') -> 'str':
    """ The names of a group as one line - all of them when there are few, the first and
    the last ones with the count when there are many or when the budget said so.
    """
    if not names:
        return ''

    if is_collapsed or len(names) > Max_Files_Per_Group:
        newest = names[0]
        oldest = names[-1]
        out = f'{one}: {newest} ... {one}: {oldest} ({names_total} in all)'
        return out

    label = one if len(names) == 1 else many
    out = f'{label}: ' + ', '.join(names)

    return out

# ################################################################################################################################

def _render_group(number:'int', group:'stranydict', is_collapsed:'bool', is_trimmed:'bool', is_channel:'bool') -> 'str':
    """ One group of the Failures section.
    """
    text = group['text']

    if is_trimmed:
        text = _trim_text(text)

    lines = [f'{number}. {text}']

    if group['count'] == 1:
        lines.append(f'   Count: 1, at {group["last_iso"]}')
    else:
        lines.append(f'   Count: {group["count"]}, first {group["first_iso"]}, last {group["last_iso"]}')

    if is_channel:
        names_line = _format_names(group['files'], group['files_total'], is_collapsed, Label_Service, Label_Services)
        callers_line = _format_names(group['callers'], len(group['callers']), is_collapsed, Label_Caller, Label_Callers)
    else:
        names_line = _format_names(group['files'], group['files_total'], is_collapsed, Label_File, Label_Files)
        callers_line = ''

    if names_line:
        lines.append('   ' + names_line)

    if callers_line:
        lines.append('   ' + callers_line)

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def render_failures(
    groups:'dictlist',
    *,
    source:'str' = '',
    is_collapsed:'bool' = False,
    is_trimmed:'bool' = False,
    left_out:'str' = '',
    ) -> 'str':
    """ The Failures section - the intro, the groups and the line saying what was left out, if anything was.
    """
    lines = [Heading_Failures, '']
    is_channel = is_channel_source(source)

    if not groups:
        lines.append(_no_failures)
    else:
        lines.append(_failures_intro)
        lines.append('')

        for index, group in enumerate(groups, 1):
            lines.append(_render_group(index, group, is_collapsed, is_trimmed, is_channel))
            lines.append('')

        # The blank line after the last group is what the left-out line follows, so it stays
        if left_out:
            lines.append(left_out)
        else:
            lines.pop()

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def fit_to_budget(groups:'dictlist', budget_chars:'int', source:'str'='') -> 'str':
    """ The Failures section fitted to the given number of characters - the oldest groups go
    first, then the file lists shrink to their first and last entries, then the error texts
    are trimmed to their heads and tails, and a trailing line says what was left out.
    """
    kept = list(groups)
    dropped_count = 0
    is_collapsed = False
    is_trimmed = False

    while True:

        left_out = _left_out_line(dropped_count, is_collapsed, source)
        section = render_failures(kept, source=source, is_collapsed=is_collapsed, is_trimmed=is_trimmed, left_out=left_out)

        if len(section) <= budget_chars:
            return section

        # More than one group - the oldest one goes ..
        if len(kept) > 1:
            kept.pop()
            dropped_count += 1
            continue

        # .. then the file lists ..
        if not is_collapsed:
            is_collapsed = True
            continue

        # .. then the texts.
        if not is_trimmed:
            is_trimmed = True
            continue

        # Nothing left to cut - one trimmed group is the least the section can say
        return section

# ################################################################################################################################

def _left_out_line(dropped_count:'int', is_collapsed:'bool', source:'str'='') -> 'str':
    """ What the Failures section says about what it does not show.
    """
    parts:'strlist' = []

    if dropped_count:
        parts.append(f'{pluralize(dropped_count, "older group")} left out to fit')

    if is_collapsed:
        if is_channel_source(source):
            parts.append('service and caller lists shortened to their first and last entries')
        else:
            parts.append('file lists shortened to their first and last entries')

    out = ', '.join(parts)

    if out:
        out = 'Left out: ' + out + '.'

    return out

# ################################################################################################################################
# ################################################################################################################################

def _format_value(value:'object') -> 'str':
    """ A measure or a threshold as it reads in a line.
    """
    if isinstance(value, float):
        out = f'{value:g}'
    else:
        out = str(value)

    return out

# ################################################################################################################################

def render_alert(alert:'stranydict', now:'datetime') -> 'str':
    """ The Alert section - the rule that fired, the measures it read against the thresholds
    in force, the window, the other numbers the sweep took at the same time and the message.
    """
    fact = alert['fact']
    measures = alert['measures']
    thresholds = alert['thresholds']

    lines = [Heading_Alert, '']

    lines.append(f'Rule: {alert["rule"]} ({alert["severity"]})')
    lines.append(f'Object: {alert["object_name"]} ({get_source_label(alert["source"])})')

    measure_parts:'strlist' = []

    for name in measures:
        measure_parts.append(f'{name} = {_format_value(fact[name])}')

    threshold_parts:'strlist' = []

    for name, value in thresholds.items():
        threshold_parts.append(f'{name} = {_format_value(value)}')

    measure_line = 'Measure: ' + ', '.join(measure_parts)

    if threshold_parts:
        measure_line += ', threshold ' + ', '.join(threshold_parts)

    lines.append(measure_line)

    window_seconds = fact['window_seconds']

    if window_seconds:
        window_start = now - timedelta(seconds=window_seconds)
        lines.append(f'Window: {window_seconds} seconds, from {window_start.isoformat()} to {now.isoformat()}')
    else:
        lines.append('Window: none, the measure is a reading taken at the time of the sweep')

    # A measure counted over a window of its own says so
    own_window_parts:'strlist' = []

    for measure, measure_window_seconds in fact[Window_Seconds_By_Measure_Key].items():
        if measure_window_seconds != window_seconds:
            own_window_parts.append(f'{measure} = {measure_window_seconds} seconds')

    if own_window_parts:
        lines.append('Windows of their own: ' + ', '.join(own_window_parts))

    # The other numbers the sweep took - only the ones that say something
    also_parts:'strlist' = []

    for name, value in fact.items():

        if name in _non_measure_keys or name in measures:
            continue

        if not value:
            continue

        also_parts.append(f'{name} = {_format_value(value)}')

    if also_parts:
        lines.append('Also measured: ' + ', '.join(also_parts))

    lines.append(f'Message: {alert["message"]}')

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def render_object(object_info:'anylist') -> 'str':
    """ The Object section - the connection's definition as label and value pairs, secrets left out.
    """
    lines = [Heading_Object, '']

    for label, value in object_info:
        lines.append(f'{label}: {value}')

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def _row_moment(row:'stranydict') -> 'str':
    """ When a row happened and what it was about, in one phrase.
    """
    out = row['event_time_iso']

    if row['endpoint']:
        out += f' ({row["endpoint"]})'

    return out

# ################################################################################################################################

def render_baseline(baseline:'stranydict') -> 'str':
    """ The Baseline section - the successes around the failures and the newest test transfer result.
    """
    lines = [Heading_Baseline, '']

    lines.append(f'OK events in the window: {baseline["ok_count"]}')

    if baseline['last_ok'] is None:
        lines.append('Last OK event: none in the window')
    else:
        lines.append(f'Last OK event: {_row_moment(baseline["last_ok"])}')

    streak_count = baseline['streak_count']

    if streak_count:
        streak_line = f'Current failure streak: {streak_count}, since {baseline["streak_start_iso"]}'

        if baseline['last_ok_before_streak'] is None:
            streak_line += ', no OK event before it on record'
        else:
            streak_line += f', last OK before it {_row_moment(baseline["last_ok_before_streak"])}'

        lines.append(streak_line)
    else:
        lines.append('Current failure streak: none, the newest event succeeded')

    if not baseline['test_transfers_on']:
        lines.append('Test transfer result: not run, test transfers are off for this connection')
    elif baseline['test_transfer'] is None:
        lines.append('Test transfer result: none on record yet')
    else:
        probe = baseline['test_transfer']
        probe_line = f'Test transfer result: {probe["outcome"]} at {probe["event_time_iso"]}'

        if probe['data']:
            probe_line += f' ({probe["data"]})'

        lines.append(probe_line)

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def build_evidence_document(
    alert:'stranydict',
    object_info:'anylist',
    groups:'dictlist',
    baseline:'stranydict',
    now:'datetime',
    ) -> 'str':
    """ The whole document - the Alert, Object and Baseline sections as they are and the Failures
    section fitted into what the budget leaves after them.
    """
    alert_section = render_alert(alert, now)
    object_section = render_object(object_info)
    baseline_section = render_baseline(baseline)

    fixed_parts = [Heading_Evidence, alert_section, object_section, baseline_section]
    fixed_length = 0

    for part in fixed_parts:
        fixed_length += len(part) + 2

    failures_section = fit_to_budget(groups, Evidence_Budget_Chars - fixed_length, alert['source'])

    parts = [Heading_Evidence, alert_section, object_section, failures_section, baseline_section]

    out = '\n\n'.join(parts)
    return out

# ################################################################################################################################

def build_prompt(instructions:'str', document:'str') -> 'str':
    """ What the LLM receives - the skill's instructions and the evidence document after them,
    the document opening with its own heading.
    """
    out = instructions.rstrip() + '\n\n' + document
    return out

# ################################################################################################################################
# ################################################################################################################################
