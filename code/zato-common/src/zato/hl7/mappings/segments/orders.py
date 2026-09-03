# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import DiagnosticReport, Practitioner, ServiceRequest
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.datatypes import ei_to_identifier, xtn_to_contact_points
from zato.hl7.mappings.fields import subcomponent_value
from zato.hl7.mappings.segments.common import Default_Order_Status, Default_Report_Status, absent_subject_reference, \
    absent_value, add_practitioner, preserve_unmapped, preserve_value
from zato.hl7.mappings.segments.timing import apply_tq_timing

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
# ORC-10, 11 and 13 are consumed by the Provenance the order's ORC produces.
_ORC_Handled = frozenset({1, 2, 3, 4, 5, 7, 9, 10, 11, 12, 13, 14, 15})

# What the ServiceRequest consumes of an OBR when there is no DiagnosticReport
OBR_Handled_Order_Only = frozenset({1, 2, 3, 4, 6, 7, 13, 16, 27, 31})

# What the ServiceRequest and the DiagnosticReport together consume of an OBR
OBR_Handled_With_Report = frozenset({1, 2, 3, 4, 6, 7, 8, 13, 16, 22, 24, 25, 27, 31, 32})

# What the Specimen an OBR describes consumes on top of that - the received time and the specimen source
OBR_Handled_Specimen = frozenset({14, 15})

# Which ORC fields the Immunization mapper consumes - the filler order number and the control code
ORC_Handled_Immunization = frozenset({1, 2, 3})

# ################################################################################################################################
# ################################################################################################################################

def _has_occurrence(current:'stranydict') -> 'bool':
    """ Tells whether a serialized ServiceRequest already says when the service takes place.
    """
    out = 'occurrenceDateTime' in current

    if 'occurrencePeriod' in current:
        out = True

    return out

# ################################################################################################################################

def _repeats_slot(current:'stranydict', key:'str', value:'str') -> 'bool':
    """ Tells whether a taken slot already holds this very value.
    """
    if key not in current:
        return False

    out = current[key] == value
    return out

# ################################################################################################################################

def _apply_orc_requester(
    accessor:'SegmentAccessor',
    service_request:'ServiceRequest',
    context:'ConversionContext',
    ) -> 'None':
    """ The ordering provider becomes the requester, with the call back number as its contact point -
    a number with no provider to belong to, or one that does not read as a contact point, is preserved as-is.
    """
    config = context.config

    # The call back numbers become the requester's contact points ..
    telecoms:'anylist' = []

    for repetition in accessor.repetitions(14):
        for telecom in xtn_to_contact_points(repetition, config, default_use='work'):
            telecoms.append(telecom)

    callback_repetition = accessor.first(14)
    has_callback        = bool(callback_repetition)
    callback_consumed   = False

    # .. the ordering provider becomes the requester and takes them along ..
    provider_repetition = accessor.first(12)

    if requester := add_practitioner(provider_repetition, context, telecoms):
        service_request.requester = requester
        callback_consumed = bool(telecoms)

    # .. and a call back number no requester took is preserved as-is.
    if has_callback:
        if not callback_consumed:
            serialized_callback = accessor.serialize(14)
            preserve_value(service_request, context, 'ORC', 14, serialized_callback)

# ################################################################################################################################

def _apply_orc_effective_time(
    accessor:'SegmentAccessor',
    service_request:'ServiceRequest',
    context:'ConversionContext',
    ) -> 'None':
    """ The order effective time fills in the occurrence when nothing else in the order group said
    when the service takes place - otherwise it is preserved as-is.
    """
    # An empty effective time says nothing about when the service takes place ..
    effective_value = accessor.value(15)

    if not effective_value:
        return

    current = service_request.to_dict()
    effective = context.datetime(effective_value, 'ORC', 15)

    # .. a time whose slot is already taken is preserved as-is, unless it merely repeats what is there ..
    if effective:
        if _has_occurrence(current):
            if not _repeats_slot(current, 'occurrenceDateTime', effective):
                preserve_value(service_request, context, 'ORC', 15, effective_value)
        else:
            service_request.occurrenceDateTime = effective

    # .. and a value that is not a date/time at all is preserved as-is too.
    else:
        preserve_value(service_request, context, 'ORC', 15, effective_value)

# ################################################################################################################################

def _apply_obr_times(
    obr_accessor:'SegmentAccessor',
    service_request:'ServiceRequest',
    context:'ConversionContext',
    ) -> 'None':
    """ Fills in the authored time from OBR-6 and the occurrence from OBR-7 when nothing
    earlier in the order group provided them - a value that finds its slot taken is preserved as-is.
    """
    current = service_request.to_dict()

    # The requested time is when the order was authored ..
    requested_value = obr_accessor.value(6)

    if requested_value:
        requested = context.datetime(requested_value, 'OBR', 6)
        has_authored = 'authoredOn' in current

        if requested:
            if has_authored:
                if not _repeats_slot(current, 'authoredOn', requested):
                    preserve_value(service_request, context, 'OBR', 6, requested_value)
            else:
                service_request.authoredOn = requested
        else:
            preserve_value(service_request, context, 'OBR', 6, requested_value)

    # .. and the observation time is when the requested service takes place.
    observation_value = obr_accessor.value(7)

    if observation_value:
        observation_time = context.datetime(observation_value, 'OBR', 7)

        if observation_time:
            if _has_occurrence(current):
                if not _repeats_slot(current, 'occurrenceDateTime', observation_time):
                    preserve_value(service_request, context, 'OBR', 7, observation_value)
            else:
                service_request.occurrenceDateTime = observation_time
        else:
            preserve_value(service_request, context, 'OBR', 7, observation_value)

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
        authored = context.datetime(authored_value, 'ORC', 9)

        if authored:
            out.authoredOn = authored
        elif authored_value:
            serialized_authored = orc_accessor.serialize(9)
            preserve_value(out, context, 'ORC', 9, serialized_authored)

        # .. the quantity/timing field carries the occurrence and the priority ..
        apply_tq_timing(orc_accessor, 7, out, context)

        # .. and the ordering provider is the requester, reachable at the call back number.
        _apply_orc_requester(orc_accessor, out, context)

        preserve_unmapped(orc_accessor, _ORC_Handled, out, context)

    # Without an ORC, the ordering provider and the timing come from the OBR itself ..
    if obr_accessor:
        if not orc_accessor:
            provider_repetition = obr_accessor.first(16)

            if requester := add_practitioner(provider_repetition, context):
                out.requester = requester

        apply_tq_timing(obr_accessor, 27, out, context)

        # .. and the OBR's own times fill in whatever the ORC and the timing fields left open.
        _apply_obr_times(obr_accessor, out, context)

    # The order effective time is the last resort for when the service takes place.
    if orc_accessor:
        _apply_orc_effective_time(orc_accessor, out, context)

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
    # a transaction time whose slot is taken, or which is not a date/time, is preserved as-is.
    authored_value = accessor.value(9)
    needs_preserving = bool(authored_value)

    if 'authoredOn' not in current:
        if authored := context.datetime(authored_value, 'ORC', 9):
            service_request.authoredOn = authored
            needs_preserving = False

    if needs_preserving:
        serialized_authored = accessor.serialize(9)
        preserve_value(service_request, context, 'ORC', 9, serialized_authored)

    # The ordering provider fills in the requester when the OBR provided none -
    # otherwise the provider and the call back number are preserved as-is.
    if 'requester' in current:
        for position in (12, 14):
            if accessor.first(position):
                serialized = accessor.serialize(position)
                preserve_value(service_request, context, 'ORC', position, serialized)
    else:
        _apply_orc_requester(accessor, service_request, context)

    # The order effective time fills in the occurrence when the OBR provided none.
    _apply_orc_effective_time(accessor, service_request, context)

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
        out.code = absent_value()

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
    effective_time = context.datetime(effective_value, 'OBR', 7)

    end_value = obr_accessor.value(8)
    end_time = context.datetime(end_value, 'OBR', 8)

    if effective_time:
        if end_time:
            out.effectivePeriod = {'start': effective_time, 'end': end_time}
        else:
            out.effectiveDateTime = effective_time
    elif end_time:
        out.effectivePeriod = {'end': end_time}

    # .. the results-reported time is when the report was issued,
    # .. a value without a time part is preserved as-is ..
    issued_value = obr_accessor.value(22)
    issued = context.instant(issued_value, 'OBR', 22)

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
# ################################################################################################################################
