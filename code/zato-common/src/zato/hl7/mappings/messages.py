# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings.config import load_mapping_config
from zato.hl7.mappings.context import ConversionContext
from zato.hl7.mappings.datatypes import dtm_to_datetime
from zato.hl7.mappings.fields import SegmentAccessor
from zato.hl7.mappings.segments import Text_Value_Types, aig_participant, ail_participant, aip_participant, \
    append_to_list_field, enrich_ais, enrich_pd1, enrich_pv2, enrich_rxr, gather_obx_text, map_al1, map_dg1, map_in1, \
    map_msh, map_nk1, map_obr_to_diagnostic_report, map_obx, map_orc_obr_to_service_request, map_pid, map_pr1, map_pv1, \
    map_rxa, map_sch, map_spm, map_txa, map_z_segment, mark_evn_handled, nte_text, set_document_text

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strnone
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# Message families whose ORC/OBR groups turn into ServiceRequests and, for results, DiagnosticReports
_order_families = ('orders', 'results')

# Segments that only group other segments and carry no data of their own
_grouping_segments = ('RGS',)

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

    if structure_id.startswith('ORU'):
        return 'results'

    if structure_id.startswith(('ORM', 'OML', 'OMG')):
        return 'orders'

    if structure_id.startswith('SIU'):
        return 'scheduling'

    if structure_id.startswith('VXU'):
        return 'immunization'

    if structure_id.startswith('MDM'):
        return 'documents'

    return 'generic'

# ################################################################################################################################
# ################################################################################################################################

class _WalkState:
    """ What the segment walk accumulates as it moves through the message in document order.
    """

    def __init__(self) -> 'None':
        self.message_header:'any_' = None
        self.patient:'any_' = None
        self.encounter:'any_' = None
        self.appointment:'any_' = None
        self.appointment_participants:'anylist' = []
        self.document:'any_' = None
        self.document_text_parts:'anylist' = []
        self.pending_orc:'any_' = None
        self.pending_notes:'anylist' = []
        self.current_service_request:'any_' = None
        self.current_report:'any_' = None
        self.current_observation:'any_' = None
        self.current_immunization:'any_' = None
        self.message_datetime:'strnone' = None
        self.control_id:'strnone' = None

# ################################################################################################################################
# ################################################################################################################################

def _attach_pending_notes(state:'_WalkState', service_request:'any_') -> 'None':
    """ Moves the notes held back for a pending ORC onto the ServiceRequest it became.
    """
    for note in state.pending_notes:
        append_to_list_field(service_request, 'note', note)

    state.pending_notes = []

# ################################################################################################################################

def _flush_pending_orc(state:'_WalkState', context:'ConversionContext') -> 'None':
    """ Turns an ORC that never met its OBR into a ServiceRequest of its own.
    """
    if state.pending_orc:
        service_request = map_orc_obr_to_service_request(state.pending_orc, None, context)
        reference = context.add(service_request)

        state.current_service_request = service_request
        _ = reference

        state.pending_orc = None
        _attach_pending_notes(state, service_request)

# ################################################################################################################################

def _handle_msh(accessor:'SegmentAccessor', state:'_WalkState', context:'ConversionContext') -> 'None':

    state.message_header = map_msh(accessor, context)
    _ = context.add(state.message_header)

    # The bundle itself will carry the message time and control ID
    state.message_datetime = dtm_to_datetime(accessor.value(7), context.config)
    state.control_id = accessor.value(10)

# ################################################################################################################################

def _handle_pid(accessor:'SegmentAccessor', state:'_WalkState', context:'ConversionContext') -> 'None':

    state.patient = map_pid(accessor, context)
    context.patient_reference = context.add(state.patient)

    # The message header points at the patient it is about
    if state.message_header:
        state.message_header.focus = [context.patient_reference]

# ################################################################################################################################

def _handle_pv1(accessor:'SegmentAccessor', state:'_WalkState', context:'ConversionContext') -> 'None':

    state.encounter = map_pv1(accessor, context)
    context.encounter_reference = context.add(state.encounter)

# ################################################################################################################################

def _handle_orc(accessor:'SegmentAccessor', state:'_WalkState', context:'ConversionContext', family:'str') -> 'None':

    # In order and immunization messages the ORC waits for the segments that follow it ..
    if family in _order_families or family == 'immunization':
        _flush_pending_orc(state, context)
        state.pending_orc = accessor

    # .. anywhere else it has nothing to attach to.
    else:
        context.warn('ORC segment not mapped')

# ################################################################################################################################

def _handle_obr(accessor:'SegmentAccessor', state:'_WalkState', context:'ConversionContext', family:'str') -> 'None':

    if family not in _order_families:
        context.warn('OBR segment not mapped')
        return

    # The OBR and any pending ORC make one ServiceRequest ..
    service_request = map_orc_obr_to_service_request(state.pending_orc, accessor, context)
    service_request_reference = context.add(service_request)

    state.current_service_request = service_request
    state.pending_orc = None
    state.current_observation = None

    _attach_pending_notes(state, service_request)

    # .. and in result messages the OBR also opens a DiagnosticReport
    # .. that the observations which follow will attach to.
    if family == 'results':
        state.current_report = map_obr_to_diagnostic_report(accessor, context, service_request_reference)
        _ = context.add(state.current_report)

# ################################################################################################################################

def _handle_obx(accessor:'SegmentAccessor', state:'_WalkState', context:'ConversionContext', family:'str') -> 'None':

    # In document messages, text OBX segments carry the document body ..
    if family == 'documents':
        value_type = accessor.value(2)
        if value_type in Text_Value_Types:
            if text := gather_obx_text(accessor, context):
                state.document_text_parts.append(text)
            return

    # .. everywhere else an OBX is an Observation.
    observation = map_obx(accessor, context)
    observation_reference = context.add(observation)

    state.current_observation = observation

    # A report in progress collects the observation as one of its results
    if state.current_report:
        append_to_list_field(state.current_report, 'result', observation_reference)

# ################################################################################################################################

def _handle_nte(accessor:'SegmentAccessor', state:'_WalkState', context:'ConversionContext') -> 'None':

    text = nte_text(accessor)
    if not text:
        return

    note = {'text': text}

    # A note that follows an ORC still waiting for its OBR belongs to that order,
    # so it is held back until the order becomes a ServiceRequest.
    if state.pending_orc:
        if not state.current_observation:
            state.pending_notes.append(note)
            return

    # The note attaches to the nearest thing that can carry it - the observation
    # right above it, the current order or the appointment being built.
    if state.current_observation:
        append_to_list_field(state.current_observation, 'note', note)

    elif state.current_service_request:
        append_to_list_field(state.current_service_request, 'note', note)

    elif state.appointment:
        state.appointment.comment = text

    else:
        context.warn('NTE segment not attached to any resource')

# ################################################################################################################################

def _handle_spm(accessor:'SegmentAccessor', state:'_WalkState', context:'ConversionContext') -> 'None':

    specimen = map_spm(accessor, context)
    specimen_reference = context.add(specimen)

    # A report in progress records what specimen it was made from
    if state.current_report:
        append_to_list_field(state.current_report, 'specimen', specimen_reference)

# ################################################################################################################################

def _handle_rxa(accessor:'SegmentAccessor', state:'_WalkState', context:'ConversionContext') -> 'None':

    state.current_immunization = map_rxa(accessor, state.pending_orc, context)
    _ = context.add(state.current_immunization)

    state.pending_orc = None

    # Notes held back for the ORC belong to the immunization it turned into
    for note in state.pending_notes:
        append_to_list_field(state.current_immunization, 'note', note)

    state.pending_notes = []

# ################################################################################################################################

def _handle_txa(accessor:'SegmentAccessor', state:'_WalkState', context:'ConversionContext') -> 'None':

    state.document = map_txa(accessor, context)
    _ = context.add(state.document)

# ################################################################################################################################

def _walk(raw_segments:'anylist', context:'ConversionContext', family:'str') -> '_WalkState':
    """ Converts every segment in document order, keeping track of what attaches to what.
    """

    # Our response to produce
    state = _WalkState()

    for raw_segment in raw_segments:
        segment_id = raw_segment.segment_id

        # Z-segments never have field definitions, so they go straight to extensions
        if segment_id.startswith('Z'):
            if basic := map_z_segment(raw_segment, context):
                _ = context.add(basic)
            continue

        # Grouping segments carry no data of their own
        if segment_id in _grouping_segments:
            continue

        accessor = SegmentAccessor(raw_segment)

        if segment_id == 'MSH':
            _handle_msh(accessor, state, context)

        elif segment_id == 'EVN':
            mark_evn_handled(accessor, context)

        elif segment_id == 'PID':
            _handle_pid(accessor, state, context)

        elif segment_id == 'PD1':
            if state.patient:
                enrich_pd1(accessor, context, state.patient)

        elif segment_id == 'NK1':
            if related_person := map_nk1(accessor, context):
                _ = context.add(related_person)

        elif segment_id == 'PV1':
            _handle_pv1(accessor, state, context)

        elif segment_id == 'PV2':
            if state.encounter:
                enrich_pv2(accessor, context, state.encounter)

        elif segment_id == 'OBX':
            _handle_obx(accessor, state, context, family)

        elif segment_id == 'AL1':
            allergy = map_al1(accessor, context)
            _ = context.add(allergy)

        elif segment_id == 'DG1':
            _ = map_dg1(accessor, context, state.encounter)

        elif segment_id == 'PR1':
            procedure = map_pr1(accessor, context)
            _ = context.add(procedure)

        elif segment_id == 'IN1':
            coverage = map_in1(accessor, context)
            _ = context.add(coverage)

        elif segment_id == 'ORC':
            _handle_orc(accessor, state, context, family)

        elif segment_id == 'OBR':
            _handle_obr(accessor, state, context, family)

        elif segment_id == 'NTE':
            _handle_nte(accessor, state, context)

        elif segment_id == 'SPM':
            _handle_spm(accessor, state, context)

        elif segment_id == 'SCH':
            state.appointment = map_sch(accessor, context)
            _ = context.add(state.appointment)

        elif segment_id == 'AIS':
            if state.appointment:
                enrich_ais(accessor, context, state.appointment)

        elif segment_id == 'AIG':
            if participant := aig_participant(accessor, context):
                state.appointment_participants.append(participant)

        elif segment_id == 'AIL':
            if participant := ail_participant(accessor, context):
                state.appointment_participants.append(participant)

        elif segment_id == 'AIP':
            if participant := aip_participant(accessor, context):
                state.appointment_participants.append(participant)

        elif segment_id == 'RXA':
            _handle_rxa(accessor, state, context)

        elif segment_id == 'RXR':
            if state.current_immunization:
                enrich_rxr(accessor, context, state.current_immunization)

        elif segment_id == 'TXA':
            _handle_txa(accessor, state, context)

        # Anything else is a segment we have no mapping for
        else:
            context.warn(f'{segment_id} segment not mapped')

    return state

# ################################################################################################################################

def _finish(state:'_WalkState', context:'ConversionContext') -> 'None':
    """ Ties up everything that could only be resolved once the whole message was walked.
    """

    # An ORC with no OBR after it still becomes a ServiceRequest
    _flush_pending_orc(state, context)

    # The document body gathered from OBX segments enters the DocumentReference
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
    """
    mapping_config = load_mapping_config(config)
    context = ConversionContext(mapping_config)

    # A message built from scratch has no raw parse tree yet, so it takes a round trip through the parser
    raw_message = msg._raw_message

    if raw_message is None:
        from zato.hl7v2 import parse_hl7
        serialized = msg.serialize()
        reparsed = parse_hl7(serialized, validate=False)
        raw_message = reparsed._raw_message

    # All the segments, in document order, with the unclaimed ones at the end
    raw_segments = _collect_segments(raw_message.items, [])
    raw_segments.extend(raw_message.extra_segments)

    family = _family_for_structure(msg._structure_id)

    # Convert every segment, then resolve what had to wait for the end of the walk
    state = _walk(raw_segments, context, family)
    _finish(state, context)

    # Wrap everything in the configured bundle type ..
    out = context.build_bundle()

    # .. the message control ID and time carry over to the bundle itself ..
    if state.control_id:
        out.identifier = {'value': state.control_id}

    if state.message_datetime:
        out.timestamp = state.message_datetime

    # .. and the warnings ride along for get_conversion_warnings.
    object.__setattr__(out, '_conversion_warnings', context.warnings)

    return out

# ################################################################################################################################
# ################################################################################################################################
