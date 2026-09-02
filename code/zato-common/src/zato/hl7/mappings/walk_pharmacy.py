# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings.segments import map_rxa, map_rxa_to_administration, map_rxd, map_rxe, map_rxg, map_rxo
from zato.hl7.mappings.walk import attach_pending_notes, preserve_pending_tq1

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

def _pharmacy_orc(state:'WalkState') -> 'SegmentAccessor | None':
    """ The ORC a pharmacy segment belongs to - the pending one
    or the one the same group's RXO already consumed.
    """
    out = state.pending_orc

    if not out:
        out = state.current_pharmacy_orc

    return out

# ################################################################################################################################

def handle_rxa(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    orc = _pharmacy_orc(state)

    # In an immunization message an RXA is an Immunization, anywhere else it records a medication administration.
    if family == 'immunization':
        state.current_medication = map_rxa(accessor, orc, context)
    else:
        state.current_medication = map_rxa_to_administration(
            accessor, orc, context, state.message_datetime)

    _ = context.add(state.current_medication)

    state.pending_orc = None

    # Notes and timing held back for the ORC belong to the resource it turned into.
    attach_pending_notes(state, state.current_medication)
    preserve_pending_tq1(state, context, state.current_medication)

# ################################################################################################################################

def handle_rxd(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    orc = _pharmacy_orc(state)

    state.current_medication = map_rxd(accessor, orc, context)
    _ = context.add(state.current_medication)

    state.pending_orc = None
    attach_pending_notes(state, state.current_medication)
    preserve_pending_tq1(state, context, state.current_medication)

# ################################################################################################################################

def handle_rxe(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    orc = _pharmacy_orc(state)

    state.current_medication = map_rxe(accessor, orc, context)
    _ = context.add(state.current_medication)

    state.pending_orc = None
    attach_pending_notes(state, state.current_medication)
    preserve_pending_tq1(state, context, state.current_medication)

# ################################################################################################################################

def handle_rxg(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    orc = _pharmacy_orc(state)

    state.current_medication = map_rxg(accessor, orc, context)
    _ = context.add(state.current_medication)

    state.pending_orc = None
    attach_pending_notes(state, state.current_medication)
    preserve_pending_tq1(state, context, state.current_medication)

# ################################################################################################################################

def handle_rxo(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    orc = _pharmacy_orc(state)

    state.current_medication = map_rxo(accessor, orc, context)
    _ = context.add(state.current_medication)

    # The ORC stays around for the RXE, RXD, RXG or RXA of the same order group.
    state.current_pharmacy_orc = orc
    state.pending_orc = None

    attach_pending_notes(state, state.current_medication)
    preserve_pending_tq1(state, context, state.current_medication)

# ################################################################################################################################
# ################################################################################################################################
