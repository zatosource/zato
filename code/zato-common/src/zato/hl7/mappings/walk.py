# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.hl7.mappings.segments import No_Consumed_Fields, add_order_provenance, append_to_list_field, apply_mfe, \
    apply_rol, apply_tq1, apply_tq1_to_dosage, map_orc_obr_to_service_request, map_segment_to_basic, \
    preserve_unmapped, specimen_from_obr

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

# The pharmacy resources whose dosage instructions a TQ1 can go into
Dosage_Instruction_Types = frozenset({'MedicationRequest', 'MedicationDispense'})

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

    # The MFE - master file entry - waiting for the resource its group builds
    pending_mfe: 'SegmentAccessor | None'

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

    # An OBR that named its specimen source waits for an SPM to describe the same specimen -
    # when none arrives, the OBR's own description becomes a Specimen of the owner's
    pending_specimen_obr:   'any_'
    pending_specimen_owner: 'any_'

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

    # The compound Medication the RXC segments of the current pharmacy resource build up, and that resource
    current_compound:       'any_'
    current_compound_owner: 'any_'

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
    out.pending_mfe  = None

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

    out.pending_specimen_obr   = None
    out.pending_specimen_owner = None

    out.referral_request = None

    out.current_service_request = None
    out.current_report          = None
    out.current_observation     = None
    out.current_medication      = None
    out.current_specimen        = None
    out.current_coverage        = None
    out.current_practitioner    = None

    out.current_compound       = None
    out.current_compound_owner = None

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

def apply_pending_mfe(state:'WalkState', context:'ConversionContext', resource:'any_') -> 'None':
    """ Moves the master file entry held back for its group onto the resource the group built.
    """
    if state.pending_mfe:
        apply_mfe(state.pending_mfe, context, resource)
        state.pending_mfe = None

# ################################################################################################################################

def flush_pending_mfe(state:'WalkState', context:'ConversionContext') -> 'None':
    """ Preserves whole a master file entry whose group built no resource to carry it.
    """
    if state.pending_mfe:
        add_basic(state.pending_mfe, context)
        state.pending_mfe = None

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

def apply_tq1_to_medication(accessor:'SegmentAccessor', context:'ConversionContext', medication:'any_') -> 'None':
    """ Applies a TQ1 to the pharmacy resource it follows - a MedicationRequest and a MedicationDispense
    carry dosage instructions the timing goes into, anything else preserves it whole.
    """
    current = medication.to_dict()
    resource_type = current['resourceType']

    if resource_type in Dosage_Instruction_Types:
        apply_tq1_to_dosage(accessor, context, medication)
    else:
        preserve_unmapped(accessor, No_Consumed_Fields, medication, context)

# ################################################################################################################################

def apply_pending_tq1_to_medication(state:'WalkState', context:'ConversionContext', resource:'any_') -> 'None':
    """ Applies the TQ1 segments held back for a pending ORC to the pharmacy resource it became.
    """
    for tq1_accessor in state.pending_tq1:
        apply_tq1_to_medication(tq1_accessor, context, resource)

    state.pending_tq1 = []

# ################################################################################################################################

def flush_pending_specimen(state:'WalkState', context:'ConversionContext') -> 'None':
    """ Turns the specimen description of an OBR that never met an SPM into a Specimen of its own,
    recorded on the report or the order the OBR produced.
    """
    if state.pending_specimen_obr:
        if specimen := specimen_from_obr(state.pending_specimen_obr, context):
            specimen_reference = context.add(specimen)
            append_to_list_field(state.pending_specimen_owner, 'specimen', specimen_reference)

            state.current_specimen = specimen

        state.pending_specimen_obr   = None
        state.pending_specimen_owner = None

# ################################################################################################################################

def flush_pending_orc(state:'WalkState', context:'ConversionContext') -> 'None':
    """ Turns an ORC that never met the segments it waited for into a ServiceRequest of its own.
    """
    if state.pending_orc:
        service_request = map_orc_obr_to_service_request(state.pending_orc, None, context)
        _ = context.add(service_request)

        add_order_provenance(state.pending_orc, service_request, context)

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
