# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

# What every message this suite sends says about where it came from and where it is going
_Sending_Application  = 'ZATO'
_Sending_Facility     = 'ZATO_TEST'
_Receiving_Application = 'RECV'
_Receiving_Facility    = 'RECV_FACILITY'

# The timestamp every message here carries. It is fixed rather than taken off the clock because
# nothing about these tests depends on it, and a fixed one keeps a message reproducible.
_Timestamp = '20260801120000'

# The version of the standard the messages speak, which is the one HAPI's v2.5 structures parse
_Version = '2.5'

# What MSH-11 says, a message of a test run being a test message
_Processing_Id = 'P'

# What MSH-18 says when a message names its encoding. Everything Zato sends goes onto the wire as
# UTF-8, so this is what a receiving parser has to be told for it to read the message back whole.
Utf8_Encoding = 'UNICODE UTF-8'

# The marker the send service replaces with a control id of its own, used where one invocation
# sends several messages and each of them needs an id nothing else in the run carries.
Control_Id_Marker = '@control_id@'

# How many observation segments the repeating-segments message carries - enough for the message to
# be a realistic results report rather than a single reading
_Observation_Count = 20

# ################################################################################################################################
# ################################################################################################################################

def build_msh(
    control_id:'str',
    message_type:'str',
    trigger_event:'str',
    encoding:'str'='',
) -> 'str':
    """ Builds the MSH line every message here starts with. Where an encoding is named it goes into
    MSH-18, which is the field a receiving parser reads the message's character set out of.
    """
    fields = [
        'MSH',
        '^~\\&',
        _Sending_Application,
        _Sending_Facility,
        _Receiving_Application,
        _Receiving_Facility,
        _Timestamp,
        '',
        f'{message_type}^{trigger_event}^{message_type}_{trigger_event}',
        control_id,
        _Processing_Id,
        _Version,

        # MSH-13 through MSH-17 are not used by anything here and are left empty so that the
        # encoding lands in MSH-18 rather than wherever the count of fields put it
        '', '', '', '', '',
        encoding,
    ]

    out = '|'.join(fields)
    return out

# ################################################################################################################################

def build_adt_a01(control_id:'str', family_name:'str'='Doe', given_name:'str'='John', encoding:'str'='') -> 'str':
    """ Builds an admission message, the one every interface in the field handles first.
    """
    segments = [
        build_msh(control_id, 'ADT', 'A01', encoding),
        f'EVN|A01|{_Timestamp}',
        f'PID|||12345^^^MRN||{family_name}^{given_name}||19800101|M',
        'PV1||I|ICU^Room1^Bed1',
    ]

    out = '\r'.join(segments)
    return out

# ################################################################################################################################

def build_oru_r01(control_id:'str', observation_count:'int'=_Observation_Count, encoding:'str'='') -> 'str':
    """ Builds a results message carrying a repeating observation segment, which is where a parser
    that only ever saw one of everything parts company with one that did not.
    """
    segments = [
        build_msh(control_id, 'ORU', 'R01', encoding),
        'PID|||67890^^^MRN||Smith^Jane||19750202|F',
        'OBR|1||LAB-001|CBC^Complete Blood Count',
    ]

    for index in range(1, observation_count + 1):
        segments.append(f'OBX|{index}|NM|WBC{index}^White Blood Cells {index}||7.{index}|10*9/L|4.0-11.0|N|||F')

    out = '\r'.join(segments)
    return out

# ################################################################################################################################

def build_orm_o01(control_id:'str', encoding:'str'='') -> 'str':
    """ Builds an order message, the third of the three types an interface is asked for by name.
    """
    segments = [
        build_msh(control_id, 'ORM', 'O01', encoding),
        'PID|||24680^^^MRN||Brown^Alice||19900303|F',
        'ORC|NW|ORD-001|||||^^^20260801120000',
        'OBR|1|ORD-001||CHEM7^Basic Metabolic Panel',
    ]

    out = '\r'.join(segments)
    return out

# ################################################################################################################################

def build_oru_of_size(control_id:'str', target_size:'int', encoding:'str'='') -> 'str':
    """ Builds a results message of at least the size asked for, by giving it as many observations
    as it takes to get there. Size is what the bounds on a connection are expressed in, so a test
    of those bounds needs a message built to a size rather than to a segment count.
    """
    message = build_oru_r01(control_id, 1, encoding)

    # One observation is added at a time until the message is large enough, each of them padded so
    # that the count needed stays in the hundreds rather than in the hundreds of thousands
    padding = 'X' * 1000
    index = 1

    segments = [message]
    current_size = len(message)

    while current_size < target_size:
        index += 1
        segment = f'OBX|{index}|ST|NOTE{index}^Note {index}||{padding}||||||F'
        segments.append(segment)
        current_size += len(segment) + 1

    out = '\r'.join(segments)
    return out

# ################################################################################################################################

def get_msh_field(message:'str', field_index:'int') -> 'str':
    """ Returns one field of a message's MSH line, counted the way the standard counts them, so
    that MSH-10 is asked for as 10 rather than as the offset it happens to sit at.
    """
    msh_line = message.split('\r')[0]
    fields = msh_line.split('|')

    # The field separator is itself MSH-1, so everything after it is one place further along the
    # split than its number says
    position = field_index - 1

    # A parser that re-encodes a message drops the empty fields off the end of a segment, so a
    # field the message never filled in is one the line may not reach at all. Either way it is
    # empty, which is what the standard says an absent field is.
    if position >= len(fields):
        return ''

    out = fields[position]
    return out

# ################################################################################################################################

def get_segment(message:'str', prefix:'str') -> 'str':
    """ Returns the first segment of a message whose name is the one asked for, or an empty string
    where the message has none.
    """
    out = ''

    for segment in message.split('\r'):
        if segment.startswith(prefix + '|'):
            out = segment
            break

    return out

# ################################################################################################################################
# ################################################################################################################################
