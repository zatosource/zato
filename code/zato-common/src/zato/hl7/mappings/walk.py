# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.hl7.mappings.segments import No_Consumed_Fields, append_to_list_field, apply_rol, apply_tq1, \
    map_orc_obr_to_service_request, map_segment_to_basic, preserve_unmapped

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strnone
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class WalkState:
    """ What the segment walk accumulates as it moves through the message in document order.
    """

    # The resources the header, patient and visit segments produced
    message_header: 'any_'
    patient:        'any_'
    encounter:      'any_'

    # Every Patient the message carried with its reference, in document order -
    # link messages tie the first two together
    patients:           'anylist'
    patient_references: 'anylist'

    # The EVN segment waits until the walk ends to enrich the Encounter
    evn_accessor: 'SegmentAccessor | None'

    # The appointment the scheduling segments build up
    appointment:              'any_'
    appointment_participants: 'anylist'

    # The document the TXA and OBX segments build up
    document:            'any_'
    document_text_parts: 'anylist'

    # An ORC waits for the segments that follow it, together with what arrived meanwhile
    pending_orc:   'any_'
    pending_notes: 'anylist'
    pending_tq1:   'anylist'
    pending_rol:   'anylist'

    # The ORC the last order group consumed - further OBRs with the same order numbers reuse it
    current_orc: 'any_'

    # The ORC an RXO consumed - the RXE, RXD, RXG or RXA of the same order group reuses it
    current_pharmacy_orc: 'any_'

    # The referral its RF1 produced - the PID and PV1 that follow it fill in the subject and encounter
    referral_request: 'any_'

    # The most recent resource of each kind that later segments may attach to
    current_service_request: 'any_'
    current_report:          'any_'
    current_observation:     'any_'
    current_medication:      'any_'
    current_specimen:        'any_'
    current_coverage:        'any_'
    current_practitioner:    'any_'

    # The message metadata the bundle itself will carry
    message_datetime: 'strnone'
    control_id:       'strnone'
    processing_id:    'strnone'

# ################################################################################################################################

def new_walk_state() -> 'WalkState':
    """ Builds an empty walk state.
    """
    out = WalkState()

    out.message_header = None
    out.patient        = None
    out.encounter      = None

    out.patients           = []
    out.patient_references = []

    out.evn_accessor = None

    out.appointment              = None
    out.appointment_participants = []

    out.document            = None
    out.document_text_parts = []

    out.pending_orc   = None
    out.pending_notes = []
    out.pending_tq1   = []
    out.pending_rol   = []

    out.current_orc = None
    out.current_pharmacy_orc = None

    out.referral_request = None

    out.current_service_request = None
    out.current_report          = None
    out.current_observation     = None
    out.current_medication      = None
    out.current_specimen        = None
    out.current_coverage        = None
    out.current_practitioner    = None

    out.message_datetime = None
    out.control_id       = None
    out.processing_id    = None

    return out

# ################################################################################################################################
# ################################################################################################################################

def add_basic(accessor:'SegmentAccessor', context:'ConversionContext') -> 'None':
    """ Preserves a whole segment as a Basic resource.
    """
    if basic := map_segment_to_basic(accessor.raw_segment, context):
        _ = context.add(basic)

# ################################################################################################################################

def attach_pending_notes(state:'WalkState', resource:'any_') -> 'None':
    """ Moves the notes held back for a pending ORC onto the resource it became.
    """
    for note in state.pending_notes:
        append_to_list_field(resource, 'note', note)

    state.pending_notes = []

# ################################################################################################################################

def apply_pending_tq1(state:'WalkState', context:'ConversionContext', service_request:'any_') -> 'None':
    """ Applies the TQ1 segments held back for a pending ORC to the ServiceRequest it became.
    """
    for tq1_accessor in state.pending_tq1:
        apply_tq1(tq1_accessor, context, service_request)

    state.pending_tq1 = []

# ################################################################################################################################

def preserve_pending_tq1(state:'WalkState', context:'ConversionContext', resource:'any_') -> 'None':
    """ Preserves the TQ1 segments held back for a pending ORC on the pharmacy resource it became.
    """
    for tq1_accessor in state.pending_tq1:
        preserve_unmapped(tq1_accessor, No_Consumed_Fields, resource, context)

    state.pending_tq1 = []

# ################################################################################################################################

def flush_pending_orc(state:'WalkState', context:'ConversionContext') -> 'None':
    """ Turns an ORC that never met the segments it waited for into a ServiceRequest of its own.
    """
    if state.pending_orc:
        service_request = map_orc_obr_to_service_request(state.pending_orc, None, context)
        _ = context.add(service_request)

        state.current_service_request = service_request

        state.pending_orc = None
        attach_pending_notes(state, service_request)
        apply_pending_tq1(state, context, service_request)

# ################################################################################################################################

def apply_pending_rol(state:'WalkState', context:'ConversionContext') -> 'None':
    """ Applies the ROL segments held back until an Encounter existed to attach them to.
    """
    for rol_accessor in state.pending_rol:
        apply_rol(rol_accessor, context, state.encounter, state.message_header)

    state.pending_rol = []

# ################################################################################################################################
# ################################################################################################################################
