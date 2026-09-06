# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings.segments import aig_participant, ail_participant, aip_participant, enrich_ais, map_arq, map_sch
from zato.hl7.mappings.walk import add_basic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    from zato.hl7.mappings.walk import WalkState
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    WalkState = WalkState

# ################################################################################################################################
# ################################################################################################################################

def handle_sch(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    state.appointment = map_sch(accessor, context, state.appointment_participants)
    _ = context.add(state.appointment)

# ################################################################################################################################

def handle_arq(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    state.appointment = map_arq(accessor, context, state.appointment_participants)
    _ = context.add(state.appointment)

# ################################################################################################################################

def handle_ais(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    if state.appointment:
        enrich_ais(accessor, context, state.appointment)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def handle_aig(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    if state.appointment:
        if participant := aig_participant(accessor, context, state.appointment):
            state.appointment_participants.append(participant)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def handle_ail(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    if state.appointment:
        if participant := ail_participant(accessor, context, state.appointment):
            state.appointment_participants.append(participant)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def handle_aip(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    if state.appointment:
        if participant := aip_participant(accessor, context, state.appointment):
            state.appointment_participants.append(participant)
    else:
        add_basic(accessor, context)

# ################################################################################################################################
# ################################################################################################################################
