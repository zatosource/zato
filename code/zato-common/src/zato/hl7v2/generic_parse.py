# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from types import SimpleNamespace

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strlist
    any_ = any_
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The standard encoding characters, used when the payload has no MSH of its own
_default_component    = '^'
_default_repetition   = '~'
_default_subcomponent = '&'
_default_field        = '|'

# Indexes into MSH-2 for the three separators the default path reads
_MSH2_Component    = 0
_MSH2_Repetition   = 1
_MSH2_Subcomponent = 3

# How many MSH fields sit before MSH-9 in the rust field list
_MSH9_Index = 7

# How many characters an MSH line needs before MSH-2 can be sliced
_MSH2_Min_Length = 8

# ################################################################################################################################
# ################################################################################################################################

def _split_field(field_text:'str', component:'str', subcomponent:'str') -> 'anylist':
    """ Splits one repetition of a field into components, each a list of subcomponents.
    """
    out:'anylist' = []

    for component_text in field_text.split(component):
        out.append(component_text.split(subcomponent))

    return out

# ################################################################################################################################

def _parse_fields(field_texts:'strlist', repetition:'str', component:'str', subcomponent:'str') -> 'anylist':
    """ Builds the rust field shape - field, then repetition, then component, then subcomponent.
    """
    out:'anylist' = []

    for field_text in field_texts:
        repetitions:'anylist' = []

        for repetition_text in field_text.split(repetition):
            repetitions.append(_split_field(repetition_text, component, subcomponent))

        out.append(repetitions)

    return out

# ################################################################################################################################

def _structure_id(msh_fields:'anylist') -> 'str':
    """ Reads MSH-9 - rust index 7 - into the structure the sender declared.
    """

    # Our response to produce
    out = ''

    # Read MSH-9 ..
    field_count = len(msh_fields)
    has_msh9 = field_count > _MSH9_Index

    if has_msh9:
        msh9 = msh_fields[_MSH9_Index]
        first_repetition = msh9[0]
        component_count = len(first_repetition)

        first_component = first_repetition[0]
        message_code = first_component[0]

        trigger = ''
        structure = ''

        # .. take the structure component when present ..
        has_trigger = component_count > 1
        if has_trigger:
            trigger_component = first_repetition[1]
            trigger = trigger_component[0]

        has_structure = component_count > 2
        if has_structure:
            structure_component = first_repetition[2]
            structure = structure_component[0]

        if structure:
            out = structure

        # .. otherwise join the message code and trigger.
        elif trigger:
            out = message_code + '_' + trigger

        else:
            out = message_code

    return out

# ################################################################################################################################

def parse_generic(raw:'str') -> 'any_':
    """ Tokenizes an ER7 payload with no typed structure.
    """

    # Our response to produce
    out = SimpleNamespace(structure_id='', items=[], extra_segments=[])

    # Take the default separators ..
    field_sep    = _default_field
    component    = _default_component
    repetition   = _default_repetition
    subcomponent = _default_subcomponent

    # .. replace them from MSH-2 when an MSH is present ..
    if raw.startswith('MSH'):
        raw_length = len(raw)
        has_msh2 = raw_length >= _MSH2_Min_Length

        if has_msh2:
            field_sep = raw[3]
            msh2 = raw[4:8]
            component    = msh2[_MSH2_Component]
            repetition   = msh2[_MSH2_Repetition]
            subcomponent = msh2[_MSH2_Subcomponent]

    # .. then walk each segment.
    for line in raw.split('\r'):
        if not line:
            continue

        parts = line.split(field_sep)
        segment_id = parts[0]
        field_texts = parts[1:]
        fields = _parse_fields(field_texts, repetition, component, subcomponent)

        segment = SimpleNamespace(segment_id=segment_id, fields=fields)
        out.items.append(segment)

        if segment_id == 'MSH':
            out.structure_id = _structure_id(fields)

    return out

# ################################################################################################################################
# ################################################################################################################################
