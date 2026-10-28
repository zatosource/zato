# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from json import dumps
from urllib.parse import quote

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, callable_, dictlist, strdict, strlist
    anylist = anylist
    callable_ = callable_
    dictlist = dictlist
    strdict = strdict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class Tone:
    """ The colors a chip may be drawn in.
    """
    Green  = 'green'
    Red    = 'red'
    Amber  = 'amber'
    Blue   = 'blue'
    Indigo = 'indigo'
    Teal   = 'teal'
    Grey   = 'grey'

# ################################################################################################################################

# Every word a chip may show, with the color it is drawn in
State_Tones = {

    # Trading partners, registrations and agreements
    'Active':        Tone.Green,
    'Onboarding':    Tone.Blue,
    'Suspended':     Tone.Amber,
    'Terminated':    Tone.Grey,
    'Draft':         Tone.Grey,
    'Submitted':     Tone.Blue,
    'In review':     Tone.Indigo,
    'Approved':      Tone.Teal,
    'Rejected':      Tone.Red,
    'Expired':       Tone.Grey,
    'Proposed':      Tone.Indigo,
    'Agreed':        Tone.Teal,
    'Expiring':      Tone.Amber,

    # Certificates
    'Valid':         Tone.Green,
    'Expires soon':  Tone.Amber,

    # Messages
    'Delivered':     Tone.Green,
    'Received':      Tone.Green,
    'Retrying':      Tone.Amber,
    'Waiting':       Tone.Grey,
    'Failed':        Tone.Red,
    'Refused':       Tone.Red,
    'Duplicate':     Tone.Grey,

    # Business transactions
    'Sent':          Tone.Grey,
    'Acknowledged':  Tone.Grey,
    'Receipted':     Tone.Grey,
    'Answered':      Tone.Green,
    'Pending':       Tone.Grey,

    # Alerts and alert rules
    'Error':         Tone.Red,
    'Warning':       Tone.Amber,
    'Information':   Tone.Grey,
    'Open':          Tone.Indigo,
    'Enabled':       Tone.Green,
    'Disabled':      Tone.Grey,

    # Yes and no answers
    'Yes':           Tone.Green,
    'No':            Tone.Grey,
    'Required':      Tone.Indigo,
    'Not required':  Tone.Grey,
    'Signed':        Tone.Teal,
    'Unsigned':      Tone.Grey,
    'Verified':      Tone.Green,
    'Not verified':  Tone.Red,
}

# The words a chip in an editable block may be changed to, each group holding the words that replace one another
Choice_Groups = [
    ['Yes', 'No'],
    ['Required', 'Not required'],
    ['Signed', 'Unsigned'],
    ['Verified', 'Not verified'],
    ['Valid', 'Expires soon', 'Expired'],
    ['Error', 'Warning', 'Information'],
]

# ################################################################################################################################

def _choices_by_word() -> 'strdict':
    """ Each word of a group mapped to all the words of its group, each one with its tone, as in 'Yes:green|No:grey'.
    """
    out:'strdict' = {}

    for group in Choice_Groups:

        choices:'strlist' = []

        for word in group:
            choices.append(f'{word}:{State_Tones[word]}')

        for word in group:
            out[word] = '|'.join(choices)

    return out

# ################################################################################################################################

Choices_By_Word = _choices_by_word()

# ################################################################################################################################

# The paths of the sections
Path_Messages      = '/'
Path_Alerts        = '/alerts'
Path_Partners      = '/partners'
Path_Registrations = '/registrations'
Path_Agreements    = '/agreements'

# ################################################################################################################################
# ################################################################################################################################

Timestamp_Format = '%Y-%m-%d %H:%M:%S'
Date_Format      = '%Y-%m-%d'
Envelope_Format  = '%Y-%m-%dT%H:%M:%S'
Message_ID_Format = '%Y%m%d%H%M%S'

# The moment all sample times are counted back from
Now = datetime.now(tz=timezone.utc).replace(microsecond=0)

# ################################################################################################################################
# ################################################################################################################################

def minutes_ago(minutes:'int') -> 'datetime':
    out = Now - timedelta(minutes=minutes)
    return out

# ################################################################################################################################

def days_from_now(days:'int') -> 'str':
    moment = Now + timedelta(days=days)
    out = moment.strftime(Date_Format)
    return out

# ################################################################################################################################

def timestamp(moment:'datetime') -> 'str':
    out = moment.strftime(Timestamp_Format)
    return out

# ################################################################################################################################

def envelope_timestamp(moment:'datetime') -> 'str':
    out = moment.strftime(Envelope_Format) + '.000Z'
    return out

# ################################################################################################################################
# ################################################################################################################################

def href(section_path:'str', item_id:'str') -> 'str':
    """ The address of one item of a section, which its listing opens with the item selected.
    """
    item_id = quote(item_id, safe='')
    out = f'{section_path}?id={item_id}'
    return out

# ################################################################################################################################

def size_text(size:'int') -> 'str':
    kilobytes = size / 1024
    out = f'{kilobytes:.1f} KB'
    return out

# ################################################################################################################################
# ################################################################################################################################

def cell(text:'str', tone:'str'='', *, mono:'bool'=False, href:'str'='', tip:'str'='', role:'str'='') -> 'anydict':
    """ One value of a listing or of a detail block - plain text, a chip when it has a tone,
    a link when it has an address, with a tooltip when it has more to say than fits.
    """
    out = {
        'text': text,
        'tone': tone,
        'mono': mono,
        'href': href,
        'tip': tip,
        'role': role,
        'choices': '',
        'direction': '',
        'is_aside': False,
        'is_fixed': False,
        'edit': '',
        'is_narrow': False,
        'is_editable': False,
    }
    return out

# ################################################################################################################################

def chip(text:'str', *, tip:'str'='', role:'str'='') -> 'anydict':
    """ A value drawn as a chip, in the color its word is given in State_Tones.
    """
    tone = State_Tones[text]
    out = cell(text, tone, tip=tip, role=role)

    if text in Choices_By_Word:
        out['choices'] = Choices_By_Word[text]

    return out

# ################################################################################################################################

def directed(value:'anydict', direction:'str') -> 'anydict':
    """ A value led by a triangle that points in the direction a message goes, right if inbound, left if outbound.
    """
    value['direction'] = direction.lower()
    return value

# ################################################################################################################################
def direction_cell(direction:'str') -> 'anydict':
    """ The word Inbound or Outbound, led by its triangle.
    """
    out = directed(cell(direction), direction)
    return out

# ################################################################################################################################
def aside(text:'str') -> 'anydict':
    """ A value that qualifies the one before it in the same field, drawn more faintly than it.
    """
    out = cell(text)
    out['is_aside'] = True
    return out

# ################################################################################################################################

def mono(text:'str', *, href:'str'='', tip:'str'='') -> 'anydict':
    out = cell(text, mono=True, href=href, tip=tip)
    return out

# ################################################################################################################################

def link(text:'str', href:'str', *, is_mono:'bool'=False) -> 'anydict':
    out = cell(text, mono=is_mono, href=href)
    return out

# ################################################################################################################################

def yes_no(value:'bool') -> 'anydict':
    text = 'Yes' if value else 'No'
    out = chip(text)
    return out

# ################################################################################################################################
# ################################################################################################################################

# The units a duration is entered in, from the smallest, each with the word for one of it and its length in seconds
Duration_Units:'anylist' = [
    {'value': 'seconds', 'label': 'seconds', 'one': 'second', 'seconds': 1},
    {'value': 'minutes', 'label': 'minutes', 'one': 'minute', 'seconds': 60},
    {'value': 'hours',   'label': 'hours',   'one': 'hour',   'seconds': 3600},
    {'value': 'days',    'label': 'days',    'one': 'day',    'seconds': 86400},
]

# What a duration of zero reads as
None_Label = 'None'

# ################################################################################################################################

def counted(amount:'int', one:'str', many:'str') -> 'str':
    """ An amount with the word for what it counts, in the singular for one and in the plural for any other amount.
    """
    word = one if amount == 1 else many
    out = f'{amount} {word}'
    return out

# ################################################################################################################################

# What a delta reads as when there is no earlier moment to measure it from
No_Delta = '---'

# ################################################################################################################################

def delta(moment:'datetime', previous:'datetime | None') -> 'anydict':
    """ The time from the previous moment to this one in words, as in 2 minutes 5 seconds, or --- for the first moment.
    """
    if previous is None:
        out = cell(No_Delta)
        return out

    seconds = int((moment - previous).total_seconds())
    parts:'strlist' = []

    for unit in reversed(Duration_Units):

        amount = seconds // unit['seconds']

        if amount:
            parts.append(counted(amount, unit['one'], unit['label']))
            seconds -= amount * unit['seconds']

        # Two units say enough of any span of time
        if len(parts) == 2:
            break

    if not parts:
        parts.append(f'0 {Duration_Units[0]["label"]}')

    out = cell(' '.join(parts))
    return out

# ################################################################################################################################

def _with_editor(value:'anydict', editor:'anydict') -> 'anydict':
    """ A value whose micro-form edits it as the editor describes rather than as free text.
    """
    value['edit'] = dumps(editor)
    return value

# ################################################################################################################################

def _options(values:'strlist') -> 'anylist':
    out:'anylist' = []

    for value in values:
        out.append({'value': value, 'label': value})

    return out

# ################################################################################################################################

def duration_value(amount:'int', unit:'str') -> 'anydict':
    """ A duration, edited as a number and the unit it is counted in.
    """
    if amount == 0:
        text = None_Label
    else:
        for each in Duration_Units:
            if each['value'] == unit:
                text = counted(amount, each['one'], each['label'])
                break
        else:
            raise Exception(f'Unknown unit `{unit}`')

    editor = {'kind': 'duration', 'value': {'amount': amount, 'unit': unit}, 'units': Duration_Units}

    out = _with_editor(cell(text), editor)
    return out

# ################################################################################################################################

def seconds_value(seconds:'int') -> 'anydict':
    """ A duration given in seconds, counted in the largest unit that divides it.
    """
    unit = Duration_Units[0]

    for each in Duration_Units:
        if seconds % each['seconds'] == 0:
            unit = each

    out = duration_value(seconds // unit['seconds'], unit['value'])
    return out

# ################################################################################################################################

def number_value(number:'int') -> 'anydict':
    out = _with_editor(cell(str(number)), {'kind': 'number', 'value': number, 'unit': '', 'one': '', 'many': ''})
    return out

# ################################################################################################################################

def choice(text:'str', values:'strlist', *, is_mono:'bool'=False) -> 'anydict':
    """ A value picked from a fixed list.
    """
    editor = {'kind': 'select', 'value': text, 'options': _options(values)}

    out = _with_editor(cell(text, mono=is_mono), editor)
    return out

# ################################################################################################################################

def choices(picked:'strlist', values:'strlist') -> 'anydict':
    """ Any number of values picked from a fixed list.
    """
    editor = {'kind': 'chips', 'value': picked, 'options': _options(values)}

    out = _with_editor(cell(', '.join(picked)), editor)
    return out

# ################################################################################################################################

def typed(text:'str', input_type:'str', *, is_mono:'bool'=False) -> 'anydict':
    """ A value entered in a field of the given HTML input type, such as a date, an address or a URL.
    """
    editor = {'kind': 'text', 'value': text, 'input_type': input_type}

    out = _with_editor(cell(text, mono=is_mono), editor)
    return out

# ################################################################################################################################

def fixed(value:'anydict | str') -> 'anydict':
    """ A value of an editable block that records what happened and is never edited.
    """
    if not isinstance(value, dict):
        value = cell(value)

    value['is_fixed'] = True
    return value

# ################################################################################################################################
def _can_edit(value:'anydict') -> 'bool':
    """ Whether a value of an editable block opens a micro-form - links lead elsewhere, a state is changed
    by the buttons of the item, and a chip is changed only to one of the words of its group.
    """
    if value['href']:
        return False

    if value['role'] == 'state':
        return False

    if value['direction']:
        return False

    if value['is_fixed']:
        return False

    if value['tone']:
        out = bool(value['choices'])
        return out

    return True

# ################################################################################################################################

def fields(title:'str', rows:'anylist', *, is_editable:'bool'=False) -> 'anydict':
    """ A block of labeled values, each row a pair of a label and either a cell, plain text or a list of cells
    that the field shows one after another.
    """
    out_rows:'anylist' = []

    for label, value in rows:

        if not isinstance(value, list):
            value = [value]

        cells:'anylist' = []

        for each in value:
            if not isinstance(each, dict):
                each = cell(each)
            if is_editable:
                each['is_editable'] = _can_edit(each)
            cells.append(each)

        out_rows.append({'label': label, 'cells': cells})

    out = {'kind': 'fields', 'title': title, 'rows': out_rows, 'is_editable': is_editable}
    return out

# ################################################################################################################################

def id_column(label:'str') -> 'anydict':
    """ A column of a table holding identifiers, which is as wide as the longest of them so that none is cut.
    """
    out = {'label': label, 'is_id': True}
    return out

# ################################################################################################################################
def table(title:'str', columns:'anylist', rows:'anylist', *, is_editable:'bool'=False) -> 'anydict':
    """ A block holding a table, each column a label or an identifier column, each row a list of cells or plain texts.
    """
    out_columns:'anylist' = []

    for column in columns:
        if not isinstance(column, dict):
            column = {'label': column, 'is_id': False}
        out_columns.append(column)

    out_rows:'anylist' = []

    for row in rows:
        out_row:'anylist' = []
        for value in row:
            if not isinstance(value, dict):
                value = cell(value)
            if is_editable:
                value['is_editable'] = _can_edit(value)
            out_row.append(value)
        out_rows.append(out_row)

    out = {'kind': 'table', 'title': title, 'columns': out_columns, 'rows': out_rows, 'is_editable': is_editable}
    return out

# ################################################################################################################################

def code(title:'str', text:'str') -> 'anydict':
    out = {'kind': 'code', 'title': title, 'text': text}
    return out

# ################################################################################################################################

def tab(key:'str', label:'str', blocks:'anylist') -> 'anydict':
    out = {'key': key, 'label': label, 'blocks': blocks}
    return out

# ################################################################################################################################

def action(label:'str', *, state:'str'='', text:'str'='', is_remove:'bool'=False, is_primary:'bool'=False) -> 'anydict':
    """ A button of the detail pane - it either moves the item to a new state or removes it from the listing.
    """
    tone = State_Tones[state] if state else ''
    kind = 'remove' if is_remove else 'set-state'

    out = {
        'label': label,
        'kind': kind,
        'state': state,
        'text': text if text else state,
        'tone': tone,
        'is_primary': is_primary,
        'is_danger': is_remove,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

def column(label:'str', *, is_narrow:'bool'=False) -> 'anydict':
    out = {'label': label, 'is_narrow': is_narrow}
    return out

# ################################################################################################################################

def item(
    item_id:'str',
    *,
    title:'str',
    cells:'anylist',
    attributes:'strdict',
    search:'strlist',
    tabs:'anylist',
    ) -> 'anydict':
    """ One row of a listing together with everything its detail pane shows.
    """
    out = {
        'id': item_id,
        'title': title,
        'cells': cells,
        'attributes': attributes,
        'search': ' '.join(search).lower(),
        'tabs': tabs,
        'details_label': '',
        'details': [],
    }
    return out

# ################################################################################################################################

def transitions(actions_of:'callable_', states:'strlist') -> 'anydict':
    """ The actions an item can take in each state it can be in, starting from the states the items are in
    and following each action to the state it leads to.
    """
    out:'anydict' = {}
    pending = list(states)

    while pending:

        state = pending.pop()

        if state in out:
            continue

        out[state] = actions_of(state)

        for each in out[state]:
            if each['state']:
                pending.append(each['state'])

    return out

# ################################################################################################################################

def section(
    *,
    slug:'str',
    path:'str',
    title:'str',
    columns:'anylist',
    items:'dictlist',
    actions_of:'callable_',
    is_bulk:'bool'=True,
    ) -> 'anydict':
    """ One listing of the portal. Its rows can be checked to act on many at once, unless is_bulk is False
    because what its items can do is not done to many of them together.
    """

    # A narrow column is centered, which each of its cells needs to know of
    for each in items:
        for index, value in enumerate(each['cells']):
            value['is_narrow'] = columns[index]['is_narrow']

    out = {
        'slug': slug,
        'path': path,
        'title': title,
        'columns': columns,
        'items': items,
        'search': None,
        'wizard': None,
        'toggle': None,
        'is_bulk': is_bulk,
        'transitions': transitions(actions_of, [each['attributes']['state'] for each in items]),
    }
    return out

# ################################################################################################################################
# ################################################################################################################################
