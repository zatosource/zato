# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings.segments import Encapsulated_Value_Type, Mother_Link_Type, OBR_Handled_Order_Only, \
    OBR_Handled_Specimen, OBR_Handled_With_Report, Text_Value_Types, add_document_attachment, \
    add_order_provenance, aig_participant, ail_participant, aip_participant, append_to_list_field, apply_bpo, \
    apply_in2, apply_ipc, apply_mfi, apply_mrg, apply_msa, apply_pda, apply_pra, apply_prd, apply_prt, apply_rol, \
    apply_sac, apply_tq1, apply_zbe, apply_zds, enrich_ais, enrich_pd1, enrich_pv2, enrich_rxr, \
    enrich_service_request_with_orc, enrich_sft, gather_obx_text, map_al1, map_arq, map_dg1, map_err, map_ft1, \
    map_gt1, map_iam, map_in1, map_msh, map_nk1, map_obr_to_diagnostic_report, map_obx, \
    map_orc_obr_to_service_request, map_pid, map_pid_mother, map_pr1, map_pv1, map_rf1, map_sch, map_spm, map_stf, \
    map_txa, nte_text, merge_obr_specimen, obr_matches_orc, obx_attachment, orc_matches_service_request, \
    preserve_unmapped, preserve_value
from zato.hl7.mappings.walk import add_basic, apply_pending_mfe, apply_pending_rol, apply_pending_tq1, \
    apply_tq1_to_medication, attach_pending_notes, flush_pending_mfe, flush_pending_orc, flush_pending_specimen
from zato.hl7.mappings.walk_pharmacy import handle_rxa, handle_rxc, handle_rxd, handle_rxe, handle_rxg, handle_rxo

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    from zato.hl7.mappings.walk import WalkState
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    WalkState = WalkState
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def _handle_msh(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    # The MessageHeader opens the bundle, ahead of the Organizations built while mapping it.
    state.message_header = map_msh(accessor, context)
    _ = context.add(state.message_header, first=True)

    # The bundle itself will carry the message time, control ID and processing mode -
    # a message time without a time part is not an instant and stays on the header as-is.
    message_time = accessor.value(7)
    message_instant = context.instant(message_time, 'MSH', 7)

    if message_instant:
        state.message_datetime = message_instant
        context.message_instant = message_instant
    elif message_time:
        preserve_value(state.message_header, context, 'MSH', 7, message_time)

    state.control_id    = accessor.value(10)
    state.processing_id = accessor.component(11, 1)

# ################################################################################################################################

def _handle_sft(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    enrich_sft(accessor, context, state.message_header)

# ################################################################################################################################

def _handle_msa(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    apply_msa(accessor, context, state.message_header)

# ################################################################################################################################

def _handle_err(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    _ = map_err(accessor, context, state.message_header)

# ################################################################################################################################

def _handle_evn(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    state.evn_accessor = accessor

# ################################################################################################################################

def _handle_pid(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    state.patient = map_pid(accessor, context)
    context.patient_reference = context.add(state.patient)

    state.patients.append(state.patient)
    state.patient_references.append(context.patient_reference)

    # The mother's identifiers make a RelatedPerson the patient links to.
    if mother := map_pid_mother(accessor, context, state.patient):
        mother_reference = context.add(mother)
        link = {'other': mother_reference, 'type': Mother_Link_Type}
        append_to_list_field(state.patient, 'link', link)

# ################################################################################################################################

def _handle_pd1(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    if state.patient:
        enrich_pd1(accessor, context, state.patient)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_mrg(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    if state.patient:
        apply_mrg(accessor, context, state.patient)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_pda(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    # The death advice concerns its PID's Patient - without one it stays whole.
    if state.patient:
        apply_pda(accessor, context, state.patient)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_nk1(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    if related_person := map_nk1(accessor, context):
        _ = context.add(related_person)

# ################################################################################################################################

def _handle_pv1(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    state.encounter = map_pv1(accessor, context)
    context.encounter_reference = context.add(state.encounter)

    # Any ROL segments that arrived before this PV1 waited for its Encounter.
    apply_pending_rol(state, context)

# ################################################################################################################################

def _handle_pv2(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    if state.encounter:
        enrich_pv2(accessor, context, state.encounter)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_zbe(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    # The movement segment enriches its PV1's Encounter - without one it stays whole like any other Z-segment.
    if state.encounter:
        apply_zbe(accessor, context, state.encounter)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_rol(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    # A ROL that precedes its PV1 waits until that PV1's Encounter exists.
    if state.encounter:
        apply_rol(accessor, context, state.encounter, state.message_header)
    else:
        state.pending_rol.append(accessor)

# ################################################################################################################################

def _handle_orc(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    # An ORC that follows the OBR of its own order group - the OUL layout - enriches
    # the ServiceRequest that OBR already produced instead of opening a new order ..
    if state.current_service_request:
        if orc_matches_service_request(accessor, state.current_service_request):
            enrich_service_request_with_orc(accessor, context, state.current_service_request)
            add_order_provenance(accessor, state.current_service_request, context)
            return

    # .. otherwise the ORC waits for the segments that follow it - an OBR, an RXA,
    # an RXE or an RXG - and becomes a ServiceRequest of its own when none arrives.
    flush_pending_orc(state, context)
    state.pending_orc = accessor

    # A new order group starts, so the previous group's pharmacy ORC no longer applies.
    state.current_pharmacy_orc = None

# ################################################################################################################################

def _handle_obr(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    orc = state.pending_orc

    # A new OBR closes the previous one's wait for an SPM.
    flush_pending_specimen(state, context)

    # An OBR with no ORC of its own that carries the order numbers of the group's ORC
    # belongs to that group - senders put several OBRs under one shared ORC.
    if not orc:
        if state.current_orc:
            if obr_matches_orc(accessor, state.current_orc):
                orc = state.current_orc

    # The OBR and its order group's ORC make one ServiceRequest, the ORC also attesting to who entered it ..
    service_request = map_orc_obr_to_service_request(orc, accessor, context)
    service_request_reference = context.add(service_request)

    if orc:
        add_order_provenance(orc, service_request, context)

    state.current_service_request = service_request
    state.current_orc             = orc
    state.pending_orc             = None
    state.current_observation     = None

    attach_pending_notes(state, service_request)
    apply_pending_tq1(state, context, service_request)

    # .. an OBR that names its specimen source describes a Specimen ..
    specimen_source = accessor.first(15)
    has_specimen = bool(specimen_source)

    # .. in result messages the OBR also opens a DiagnosticReport
    # .. that the observations which follow will attach to ..
    if family == 'results':
        state.current_report = map_obr_to_diagnostic_report(accessor, context, service_request_reference)
        _ = context.add(state.current_report)

        handled = OBR_Handled_With_Report

        if has_specimen:
            handled = handled | OBR_Handled_Specimen

        preserve_unmapped(accessor, handled, state.current_report, context)

    else:
        handled = OBR_Handled_Order_Only

        if has_specimen:
            handled = handled | OBR_Handled_Specimen

        preserve_unmapped(accessor, handled, service_request, context)

    # .. and the group's SPM, when one follows, describes the same specimen better,
    # .. so the OBR's description waits for it.
    if has_specimen:
        state.pending_specimen_obr = accessor

        if family == 'results':
            state.pending_specimen_owner = state.current_report
        else:
            state.pending_specimen_owner = service_request

# ################################################################################################################################

def _handle_obx(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    value_type = accessor.value(2)

    # In document messages, text OBX segments carry the document body
    # and encapsulated ones carry it as an attachment ..
    if family == 'documents':
        if state.document:
            if value_type in Text_Value_Types:
                if text := gather_obx_text(accessor, context, state.document):
                    state.document_text_parts.append(text)
                return

            if value_type == Encapsulated_Value_Type:
                attachment = obx_attachment(accessor, context, state.document, 'author')
                add_document_attachment(state.document, attachment)
                return

    # .. in result messages, encapsulated OBX segments are the report's presented form ..
    if family == 'results':
        if state.current_report:
            if value_type == Encapsulated_Value_Type:
                attachment = obx_attachment(accessor, context, state.current_report, 'performer')
                append_to_list_field(state.current_report, 'presentedForm', attachment)
                return

    # .. everywhere else an OBX is an Observation.
    observation = map_obx(accessor, context)
    observation_reference = context.add(observation)

    state.current_observation = observation

    # A report in progress collects the observation as one of its results.
    if state.current_report:
        append_to_list_field(state.current_report, 'result', observation_reference)

# ################################################################################################################################

def _handle_al1(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    allergy = map_al1(accessor, context)
    _ = context.add(allergy)

# ################################################################################################################################

def _handle_iam(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    allergy = map_iam(accessor, context)
    _ = context.add(allergy)

# ################################################################################################################################

def _handle_dg1(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    _ = map_dg1(accessor, context, state.encounter)

# ################################################################################################################################

def _handle_pr1(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    procedure = map_pr1(accessor, context)
    _ = context.add(procedure)

# ################################################################################################################################

def _handle_gt1(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    guarantor = map_gt1(accessor, context)
    _ = context.add(guarantor)

# ################################################################################################################################

def _handle_in1(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    state.current_coverage = map_in1(accessor, context)
    _ = context.add(state.current_coverage)

# ################################################################################################################################

def _handle_in2(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    if state.current_coverage:
        apply_in2(accessor, context, state.current_coverage)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_ft1(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    charge = map_ft1(accessor, context)
    _ = context.add(charge)

# ################################################################################################################################

def _handle_tq1(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    # A TQ1 that follows an ORC still waiting for its OBR belongs to that order,
    # so it is held back until the order becomes a resource ..
    if state.pending_orc:
        state.pending_tq1.append(accessor)

    # .. otherwise the timing applies to the current order when there is one ..
    elif state.current_service_request:
        apply_tq1(accessor, context, state.current_service_request)

    # .. after a pharmacy segment it is the dosage timing of the medication resource ..
    elif state.current_medication:
        apply_tq1_to_medication(accessor, context, state.current_medication)

    # .. and with nothing to attach to it becomes a preserved segment of its own.
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_nte(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    text = nte_text(accessor)
    if not text:
        return

    note = {'text': text}

    # A note that follows an ORC still waiting for its OBR belongs to that order,
    # so it is held back until the order becomes a resource.
    if state.pending_orc:
        if not state.current_observation:
            state.pending_notes.append(note)
            return

    # The note attaches to the nearest thing that can carry it - the observation
    # right above it, the current order, the current medication or the appointment.
    if state.current_observation:
        append_to_list_field(state.current_observation, 'note', note)

    elif state.current_service_request:
        append_to_list_field(state.current_service_request, 'note', note)

    elif state.current_medication:
        append_to_list_field(state.current_medication, 'note', note)

    elif state.appointment:
        state.appointment.comment = text

    # With nothing else to attach to, the note is preserved on the message header.
    else:
        base_url = context.config.extension_base_url
        extension = {'url': f'{base_url}/NTE', 'valueString': text}
        append_to_list_field(state.message_header, 'extension', extension)

# ################################################################################################################################

def _handle_spm(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    specimen = map_spm(accessor, context)

    # The OBR's own description of the specimen fills in what the SPM left empty.
    if state.pending_specimen_obr:
        merge_obr_specimen(state.pending_specimen_obr, specimen, context)

        state.pending_specimen_obr   = None
        state.pending_specimen_owner = None

    specimen_reference = context.add(specimen)

    state.current_specimen = specimen

    # A report in progress records what specimen it was made from.
    if state.current_report:
        append_to_list_field(state.current_report, 'specimen', specimen_reference)

# ################################################################################################################################

def _handle_sac(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    # A container that follows an OBR with no SPM belongs to the OBR's specimen.
    flush_pending_specimen(state, context)

    if state.current_specimen:
        apply_sac(accessor, context, state.current_specimen)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_sch(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    state.appointment = map_sch(accessor, context, state.appointment_participants)
    _ = context.add(state.appointment)

# ################################################################################################################################

def _handle_arq(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    state.appointment = map_arq(accessor, context, state.appointment_participants)
    _ = context.add(state.appointment)

# ################################################################################################################################

def _handle_ais(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    if state.appointment:
        enrich_ais(accessor, context, state.appointment)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_aig(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    if state.appointment:
        if participant := aig_participant(accessor, context, state.appointment):
            state.appointment_participants.append(participant)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_ail(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    if state.appointment:
        if participant := ail_participant(accessor, context, state.appointment):
            state.appointment_participants.append(participant)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_aip(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    if state.appointment:
        if participant := aip_participant(accessor, context, state.appointment):
            state.appointment_participants.append(participant)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_rxr(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    if state.current_medication:
        enrich_rxr(accessor, context, state.current_medication)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_bpo(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    # The blood product order and its group's ORC make one ServiceRequest.
    orc = state.pending_orc

    service_request = map_orc_obr_to_service_request(orc, None, context)
    apply_bpo(accessor, context, service_request)

    _ = context.add(service_request)

    if orc:
        add_order_provenance(orc, service_request, context)

    state.current_service_request = service_request
    state.pending_orc = None

    attach_pending_notes(state, service_request)
    apply_pending_tq1(state, context, service_request)

# ################################################################################################################################

def _handle_ipc(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    # The imaging procedure control details the order it follows - without one it stays whole.
    if state.current_service_request:
        apply_ipc(accessor, context, state.current_service_request)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_zds(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    # The study UID belongs to the order it follows - without one it stays whole like any other Z-segment.
    if state.current_service_request:
        apply_zds(accessor, context, state.current_service_request)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_rf1(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    state.referral_request = map_rf1(accessor, context)
    _ = context.add(state.referral_request)

    # The PRD and NTE segments that follow attach to the referral.
    state.current_service_request = state.referral_request

# ################################################################################################################################

def _handle_prd(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    apply_prd(accessor, context, state.referral_request)

# ################################################################################################################################

def _handle_txa(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    state.document = map_txa(accessor, context)
    _ = context.add(state.document)

# ################################################################################################################################

def _handle_mfi(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    # The master file frame belongs to the message itself - without a header it stays whole.
    if state.message_header:
        apply_mfi(accessor, context, state.message_header)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _handle_mfe(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    # An entry whose group built nothing before the next one stays whole ..
    flush_pending_mfe(state, context)

    # .. and this one waits for the resource its own group builds.
    state.pending_mfe = accessor

# ################################################################################################################################

def _handle_stf(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    state.current_practitioner = map_stf(accessor, context)
    _ = context.add(state.current_practitioner)

    apply_pending_mfe(state, context, state.current_practitioner)

# ################################################################################################################################

def _handle_pra(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    if state.current_practitioner:
        apply_pra(accessor, context, state.current_practitioner)
    else:
        add_basic(accessor, context)

# ################################################################################################################################

def _prt_target(state:'WalkState') -> 'any_':
    """ The resource a PRT participation attaches to - the nearest thing
    above it that can carry a person reference.
    """
    if state.current_report:
        return state.current_report

    if state.current_service_request:
        return state.current_service_request

    if state.current_observation:
        return state.current_observation

    if state.document:
        return state.document

    return state.encounter

# ################################################################################################################################

def _handle_prt(accessor:'SegmentAccessor', state:'WalkState', context:'ConversionContext', family:'str') -> 'None':

    target = _prt_target(state)

    # A participation with no person or nothing to attach to stays whole.
    if not apply_prt(accessor, context, target):
        add_basic(accessor, context)

# ################################################################################################################################
# ################################################################################################################################

# Maps each segment ID to the handler the walk dispatches it to
segment_handlers = {
    'MSH': _handle_msh,
    'SFT': _handle_sft,
    'MSA': _handle_msa,
    'ERR': _handle_err,
    'EVN': _handle_evn,
    'PID': _handle_pid,
    'PD1': _handle_pd1,
    'MRG': _handle_mrg,
    'PDA': _handle_pda,
    'NK1': _handle_nk1,
    'PV1': _handle_pv1,
    'PV2': _handle_pv2,
    'ZBE': _handle_zbe,
    'ROL': _handle_rol,
    'OBX': _handle_obx,
    'AL1': _handle_al1,
    'IAM': _handle_iam,
    'DG1': _handle_dg1,
    'PR1': _handle_pr1,
    'GT1': _handle_gt1,
    'IN1': _handle_in1,
    'IN2': _handle_in2,
    'FT1': _handle_ft1,
    'ORC': _handle_orc,
    'OBR': _handle_obr,
    'TQ1': _handle_tq1,
    'NTE': _handle_nte,
    'SPM': _handle_spm,
    'SAC': _handle_sac,
    'SCH': _handle_sch,
    'ARQ': _handle_arq,
    'AIS': _handle_ais,
    'AIG': _handle_aig,
    'AIL': _handle_ail,
    'AIP': _handle_aip,
    'RXA': handle_rxa,
    'RXC': handle_rxc,
    'RXD': handle_rxd,
    'RXE': handle_rxe,
    'RXG': handle_rxg,
    'RXO': handle_rxo,
    'RXR': _handle_rxr,
    'IPC': _handle_ipc,
    'ZDS': _handle_zds,
    'BPO': _handle_bpo,
    'RF1': _handle_rf1,
    'PRD': _handle_prd,
    'TXA': _handle_txa,
    'MFI': _handle_mfi,
    'MFE': _handle_mfe,
    'STF': _handle_stf,
    'PRA': _handle_pra,
    'PRT': _handle_prt,
}

# ################################################################################################################################
# ################################################################################################################################
