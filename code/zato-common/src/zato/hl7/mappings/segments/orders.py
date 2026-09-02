# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import DiagnosticReport, Practitioner, ServiceRequest
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.datatypes import dtm_to_datetime, ei_to_identifier
from zato.hl7.mappings.fields import subcomponent_value
from zato.hl7.mappings.segments.common import Default_Order_Status, Default_Report_Status, Unknown_Code, \
    absent_subject_reference, add_practitioner, preserve_unmapped, preserve_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
dictnone = 'stranydict | None'

# Which field positions each mapper consumes - anything else that carries data is preserved as an extension.
_ORC_Handled = frozenset({1, 2, 3, 4, 5, 7, 9, 12})

# What the ServiceRequest consumes of an OBR when there is no DiagnosticReport
OBR_Handled_Order_Only = frozenset({1, 2, 3, 4, 13, 16, 27, 31})

# What the ServiceRequest and the DiagnosticReport together consume of an OBR
OBR_Handled_With_Report = frozenset({1, 2, 3, 4, 7, 8, 13, 16, 22, 24, 25, 27, 31, 32})

# Which ORC fields the Immunization mapper consumes - the filler order number and the control code
ORC_Handled_Immunization = frozenset({1, 2, 3})

# Which TQ1 field positions apply_tq1 consumes
_TQ1_Handled = frozenset({1, 7, 8, 9})

# Which TQ components carry the interval, the start time, the end time and the priority
_TQ_Interval_Component = 2
_TQ_Start_Component = 4
_TQ_End_Component = 5
_TQ_Priority_Component = 6

# ################################################################################################################################
# ################################################################################################################################

def _apply_tq_timing(
    accessor:'SegmentAccessor',
    position:'int',
    service_request:'ServiceRequest',
    context:'ConversionContext',
    ) -> 'None':
    """ Applies one TQ - quantity/timing - field to a ServiceRequest, the start and end
    times becoming the occurrence and the priority component the request priority.
    """
    config = context.config

    start_value = accessor.component(position, _TQ_Start_Component)
    start_time = dtm_to_datetime(start_value, config)

    end_value = accessor.component(position, _TQ_End_Component)
    end_time = dtm_to_datetime(end_value, config)

    if start_time:
        if end_time:
            service_request.occurrencePeriod = {'start': start_time, 'end': end_time}
        else:
            service_request.occurrenceDateTime = start_time

    priority_code = accessor.component(position, _TQ_Priority_Component)

    # The priority word can arrive in the interval component instead.
    if not priority_code:
        priority_code = accessor.component(position, _TQ_Interval_Component)

    if priority := lookup('order_priority', priority_code, config):
        service_request.priority = priority['code']
    else:
        if priority_code:
            preserve_value(service_request, context, accessor.segment_id, position, priority_code)

# ################################################################################################################################

def map_orc_obr_to_service_request(
    orc_accessor:'SegmentAccessor | None',
    obr_accessor:'SegmentAccessor | None',
    context:'ConversionContext',
    ) -> 'ServiceRequest':
    """ Converts an ORC/OBR pair - either may be absent - to a ServiceRequest.
    """
    config = context.config

    # Our response to produce
    out = ServiceRequest()

    out.intent = 'order'

    if context.patient_reference:
        out.subject = context.patient_reference
    else:
        # FHIR requires a subject - order responses like ORL carry no PID,
        # so the absence of the patient is stated explicitly.
        out.subject = absent_subject_reference()

    if context.encounter_reference:
        out.encounter = context.encounter_reference

    # The order status comes from ORC-5 first, the order control code second,
    # unknown codes map to the default and are preserved as-is ..
    state_code = None
    control_code = None

    if orc_accessor:
        state_code = orc_accessor.value(5)
        control_code = orc_accessor.value(1)

    if status := lookup('order_state', state_code, config):
        out.status = status['code']
    elif status := lookup('order_status', control_code, config):
        out.status = status['code']

        if state_code:
            preserve_value(out, context, 'ORC', 5, state_code)
    else:
        out.status = Default_Order_Status

        if state_code:
            preserve_value(out, context, 'ORC', 5, state_code)

        if control_code:
            preserve_value(out, context, 'ORC', 1, control_code)

    # .. placer and filler order numbers and the placer group number become identifiers, wherever they appear ..
    identifiers:'anylist' = []

    for source_accessor, position in \
        ((orc_accessor, 2), (orc_accessor, 3), (orc_accessor, 4), (obr_accessor, 2), (obr_accessor, 3)):

        if source_accessor:
            order_number_repetition = source_accessor.first(position)

            if identifier := ei_to_identifier(order_number_repetition, config):
                if identifier not in identifiers:
                    identifiers.append(identifier)

    if identifiers:
        out.identifier = identifiers

    # .. the universal service identifier is the requested code ..
    if obr_accessor:
        service_repetition = obr_accessor.first(4)

        if code := cwe_to_codeable_concept(service_repetition, config):
            out.code = code

    # .. the relevant clinical information becomes a note and the reason for study the reason ..
    if obr_accessor:
        clinical_information = obr_accessor.value(13)
        if clinical_information:
            out.note = [{'text': clinical_information}]

        reason_repetition = obr_accessor.first(31)

        if reason := cwe_to_codeable_concept(reason_repetition, config):
            out.reasonCode = [reason]

    # .. the transaction time is when the order was authored - other values
    # can arrive in this slot and those are preserved as-is ..
    if orc_accessor:
        authored_value = orc_accessor.value(9)
        authored = dtm_to_datetime(authored_value, config)

        if authored:
            out.authoredOn = authored
        elif authored_value:
            serialized_authored = orc_accessor.serialize(9)
            preserve_value(out, context, 'ORC', 9, serialized_authored)

        # .. the quantity/timing field carries the occurrence and the priority ..
        _apply_tq_timing(orc_accessor, 7, out, context)

        # .. and the ordering provider is the requester.
        provider_repetition = orc_accessor.first(12)

        if requester := add_practitioner(provider_repetition, context):
            out.requester = requester

        preserve_unmapped(orc_accessor, _ORC_Handled, out, context)

    # Without an ORC, the ordering provider and the timing come from the OBR itself.
    if obr_accessor:
        if not orc_accessor:
            provider_repetition = obr_accessor.first(16)

            if requester := add_practitioner(provider_repetition, context):
                out.requester = requester

        _apply_tq_timing(obr_accessor, 27, out, context)

    return out

# ################################################################################################################################

def obr_matches_orc(accessor:'SegmentAccessor', orc_accessor:'SegmentAccessor') -> 'bool':
    """ Tells whether an OBR carries the same order numbers as an ORC, which means the OBR
    belongs to the order group that ORC opened.
    """
    obr_placer = accessor.component(2, 1)
    obr_filler = accessor.component(3, 1)

    orc_placer = orc_accessor.component(2, 1)
    orc_filler = orc_accessor.component(3, 1)

    # The placer order numbers match ..
    if obr_placer:
        if obr_placer == orc_placer:
            return True

    # .. or the filler ones do.
    if obr_filler:
        if obr_filler == orc_filler:
            return True

    return False

# ################################################################################################################################

def orc_matches_service_request(accessor:'SegmentAccessor', service_request:'ServiceRequest') -> 'bool':
    """ Tells whether an ORC carries the same order numbers as an existing ServiceRequest,
    which means it belongs to the order group the request was already built from.
    """
    current = service_request.to_dict()

    identifier_list = current.get('identifier')
    if not identifier_list:
        return False

    known_values = set()

    for identifier in identifier_list:
        known_values.add(identifier['value'])

    placer_number = accessor.component(2, 1)
    filler_number = accessor.component(3, 1)

    if placer_number:
        if placer_number in known_values:
            return True

    if filler_number:
        if filler_number in known_values:
            return True

    return False

# ################################################################################################################################

def enrich_service_request_with_orc(
    accessor:'SegmentAccessor',
    context:'ConversionContext',
    service_request:'ServiceRequest',
    ) -> 'None':
    """ Applies an ORC that follows the OBR of its own order group - the OUL layout -
    to the ServiceRequest the OBR already produced.
    """
    config = context.config
    current = service_request.to_dict()

    # The order status upgrades from the default once the ORC spells one out.
    state_code = accessor.value(5)
    control_code = accessor.value(1)

    if current['status'] == Default_Order_Status:
        if status := lookup('order_state', state_code, config):
            service_request.status = status['code']
        elif status := lookup('order_status', control_code, config):
            service_request.status = status['code']

    # Order numbers the request does not carry yet join its identifiers.
    identifiers = []

    if existing_identifiers := current.get('identifier'):
        identifiers.extend(existing_identifiers)

    for position in (2, 3, 4):
        order_number_repetition = accessor.first(position)

        if identifier := ei_to_identifier(order_number_repetition, config):
            if identifier not in identifiers:
                identifiers.append(identifier)

    if identifiers:
        service_request.identifier = identifiers

    # The transaction time fills in the authored time when the OBR provided none -
    # other values can arrive in this slot and those are preserved as-is.
    if 'authoredOn' not in current:
        authored_value = accessor.value(9)

        if authored := dtm_to_datetime(authored_value, config):
            service_request.authoredOn = authored
        elif authored_value:
            serialized_authored = accessor.serialize(9)
            preserve_value(service_request, context, 'ORC', 9, serialized_authored)

    # The ordering provider fills in the requester when the OBR provided none.
    if 'requester' not in current:
        provider_repetition = accessor.first(12)

        if requester := add_practitioner(provider_repetition, context):
            service_request.requester = requester

    preserve_unmapped(accessor, _ORC_Handled, service_request, context)

# ################################################################################################################################

def _ndl_practitioner(repetition:'anylist', context:'ConversionContext') -> 'dictnone':
    """ Builds a Practitioner from an NDL - name with date and location - repetition,
    whose first component packs the ID, family and given names as subcomponents.
    """
    id_number = subcomponent_value(repetition, 1, 1)
    family = subcomponent_value(repetition, 1, 2)
    given = subcomponent_value(repetition, 1, 3)

    if not id_number:
        if not family:
            return None

    practitioner = Practitioner()

    if id_number:
        practitioner.identifier = [{'value': id_number}]

    name:'stranydict' = {}

    if family:
        name['family'] = family

    if given:
        name['given'] = [given]

    if name:
        practitioner.name = [name]

    out = context.add(practitioner)
    return out

# ################################################################################################################################

def map_obr_to_diagnostic_report(
    obr_accessor:'SegmentAccessor',
    context:'ConversionContext',
    service_request_reference:'dictnone',
    ) -> 'DiagnosticReport':
    """ Converts OBR to a DiagnosticReport that the following observations attach to.
    """
    config = context.config

    # Our response to produce
    out = DiagnosticReport()

    if context.patient_reference:
        out.subject = context.patient_reference

    if context.encounter_reference:
        out.encounter = context.encounter_reference

    if service_request_reference:
        out.basedOn = [service_request_reference]

    # The result status is required, unknown codes map to the default and are preserved as-is ..
    status_code = obr_accessor.value(25)

    if status := lookup('result_status', status_code, config):
        out.status = status['code']
    else:
        out.status = Default_Report_Status

        if status_code:
            preserve_value(out, context, 'OBR', 25, status_code)

    # .. the universal service identifier is the report code, which FHIR requires ..
    service_repetition = obr_accessor.first(4)

    if code := cwe_to_codeable_concept(service_repetition, config):
        out.code = code
    else:
        out.code = Unknown_Code

    # .. the diagnostic service section is the report category ..
    section_repetition = obr_accessor.first(24)

    if category := cwe_to_codeable_concept(section_repetition, config):
        out.category = [category]

    # .. placer and filler order numbers become identifiers ..
    identifiers:'anylist' = []

    for position in (2, 3):
        order_number_repetition = obr_accessor.first(position)

        if identifier := ei_to_identifier(order_number_repetition, config):
            identifiers.append(identifier)

    if identifiers:
        out.identifier = identifiers

    # .. the observation start and end times make the effective time or period ..
    effective_value = obr_accessor.value(7)
    effective_time = dtm_to_datetime(effective_value, config)

    end_value = obr_accessor.value(8)
    end_time = dtm_to_datetime(end_value, config)

    if effective_time:
        if end_time:
            out.effectivePeriod = {'start': effective_time, 'end': end_time}
        else:
            out.effectiveDateTime = effective_time

    # .. the results-reported time is when the report was issued - other values
    # can arrive in this slot and those are preserved as-is ..
    issued_value = obr_accessor.value(22)
    issued = dtm_to_datetime(issued_value, config)

    if issued:
        out.issued = issued
    elif issued_value:
        preserve_value(out, context, 'OBR', 22, issued_value)

    # .. and the principal result interpreter completes the picture.
    interpreter_repetition = obr_accessor.first(32)

    if interpreter := _ndl_practitioner(interpreter_repetition, context):
        out.resultsInterpreter = [interpreter]

    return out

# ################################################################################################################################

def apply_tq1(accessor:'SegmentAccessor', context:'ConversionContext', service_request:'ServiceRequest') -> 'None':
    """ Applies TQ1 to a ServiceRequest - the start and end times become the occurrence,
    the priority maps through the standard table.
    """
    config = context.config

    start_value = accessor.value(7)
    start_time = dtm_to_datetime(start_value, config)

    end_value = accessor.value(8)
    end_time = dtm_to_datetime(end_value, config)

    # TQ1 is the authoritative timing, so it replaces whatever ORC or OBR provided.
    if start_time:
        if end_time:
            service_request.occurrenceDateTime = None
            service_request.occurrencePeriod = {'start': start_time, 'end': end_time}
        else:
            service_request.occurrencePeriod = None
            service_request.occurrenceDateTime = start_time

    # The priority maps through the standard table, unknown codes are preserved as-is.
    priority_code = accessor.component(9, 1)

    if priority := lookup('order_priority', priority_code, config):
        service_request.priority = priority['code']
    else:
        if priority_code:
            preserve_value(service_request, context, 'TQ1', 9, priority_code)

    preserve_unmapped(accessor, _TQ1_Handled, service_request, context)

# ################################################################################################################################
# ################################################################################################################################
