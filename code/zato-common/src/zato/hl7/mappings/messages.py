# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings.config import load_mapping_config
from zato.hl7.mappings.context import ConversionContext
from zato.hl7.mappings.fields import SegmentAccessor
from zato.hl7.mappings.segments import apply_evn, set_document_text
from zato.hl7.mappings.walk import WalkState, add_basic, apply_pending_rol, flush_pending_orc, new_walk_state, \
    segment_handlers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strnone
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# Segments that only group other segments and carry no data of their own
_grouping_segments = ('RGS',)

# The system of the bundle's processing-mode tag from MSH-11
_processing_id_system = 'http://terminology.hl7.org/CodeSystem/v2-0103'

# ################################################################################################################################
# ################################################################################################################################

def _collect_segments(items:'any_', out:'anylist') -> 'anylist':
    """ Flattens raw message items into a segment list in document order, descending into groups.
    """
    for item in items:
        if hasattr(item, 'segment_id'):
            out.append(item)
        else:
            _ = _collect_segments(item.items, out)

    return out

# ################################################################################################################################

def _family_for_structure(structure_id:'strnone') -> 'str':
    """ Decides which conversion family a message structure belongs to.
    """
    if not structure_id:
        return 'generic'

    if structure_id.startswith(('ORU', 'OUL')):
        return 'results'

    if structure_id.startswith(('ORM', 'OML', 'OMG')):
        return 'orders'

    if structure_id.startswith(('SIU', 'SRM', 'SRR')):
        return 'scheduling'

    if structure_id.startswith('VXU'):
        return 'immunization'

    if structure_id.startswith(('RAS', 'RGV', 'RDE', 'RDS', 'OMP')):
        return 'medication'

    if structure_id.startswith('MDM'):
        return 'documents'

    return 'generic'

# ################################################################################################################################
# ################################################################################################################################

def _walk(raw_segments:'anylist', context:'ConversionContext', family:'str') -> 'WalkState':
    """ Converts every segment in document order, keeping track of what attaches to what.
    """

    # Our response to produce
    out = new_walk_state()

    for raw_segment in raw_segments:
        segment_id = raw_segment.segment_id

        # Grouping segments carry no data of their own.
        if segment_id in _grouping_segments:
            continue

        accessor = SegmentAccessor(raw_segment)

        # Each segment goes to its own handler - anything without one,
        # a Z-segment or a segment with no FHIR mapping of its own,
        # is preserved whole as a Basic resource.
        if handler := segment_handlers.get(segment_id):
            handler(accessor, out, context, family)
        else:
            add_basic(accessor, context)

    return out

# ################################################################################################################################

def _finish(state:'WalkState', context:'ConversionContext') -> 'None':
    """ Ties up everything that could only be resolved once the whole message was walked.
    """

    # An ORC with no order or pharmacy segment after it still becomes a ServiceRequest.
    flush_pending_orc(state, context)

    # A ROL whose PV1 never arrived is preserved on the message header.
    apply_pending_rol(state, context)

    # EVN backs the Encounter period up and preserves whatever else it carries.
    if state.evn_accessor:
        apply_evn(state.evn_accessor, context, state.encounter, state.message_header)

    # The message header points at the patient and the encounter the message is about.
    if state.message_header:
        focus = []

        if context.patient_reference:
            focus.append(context.patient_reference)

        if context.encounter_reference:
            focus.append(context.encounter_reference)

        if focus:
            state.message_header.focus = focus

    # The document body gathered from OBX segments enters the DocumentReference.
    if state.document:
        if state.document_text_parts:
            text = '\n'.join(state.document_text_parts)
            set_document_text(state.document, text)

    # The appointment's participants come together at the end because
    # the patient may only have appeared after the SCH segment.
    if state.appointment:
        participants = []

        if context.patient_reference:
            patient_participant = {'actor': context.patient_reference, 'status': 'accepted'}
            participants.append(patient_participant)

        participants.extend(state.appointment_participants)

        if participants:
            state.appointment.participant = participants

# ################################################################################################################################

def convert_to_fhir(msg:'any_', config:'strnone' = None) -> 'any_':
    """ Converts a parsed HL7 v2 message to a typed FHIR bundle.
    The config argument names an .ini file with site-specific overrides, or is a path to one.
    The message must carry a raw parse tree - to_fhir reparses messages built from scratch.
    """
    mapping_config = load_mapping_config(config)
    context = ConversionContext(mapping_config)

    raw_message = msg._raw_message

    # All the segments, in document order, with the unclaimed ones at the end.
    raw_segments = _collect_segments(raw_message.items, [])
    raw_segments.extend(raw_message.extra_segments)

    family = _family_for_structure(msg._structure_id)

    # Convert every segment, then resolve what had to wait for the end of the walk.
    state = _walk(raw_segments, context, family)
    _finish(state, context)

    # Wrap everything in the configured bundle type ..
    out = context.build_bundle()

    # .. the message control ID, time and processing mode carry over to the bundle itself ..
    if state.control_id:
        out.identifier = {'system': mapping_config.bundle_identifier_system, 'value': state.control_id}

    if state.message_datetime:
        out.timestamp = state.message_datetime

    if state.processing_id:
        out.meta = {'tag': [{'system': _processing_id_system, 'code': state.processing_id}]}

    # .. and the warnings ride along for get_conversion_warnings.
    out._conversion_warnings = context.warnings

    return out

# ################################################################################################################################
# ################################################################################################################################
