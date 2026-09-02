# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import Immunization, MedicationAdministration, MedicationDispense, MedicationRequest
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.datatypes import dtm_to_date, dtm_to_datetime, ei_to_identifier
from zato.hl7.mappings.fields import component_value
from zato.hl7.mappings.segments.common import Default_Administration_Status, Default_Immunization_Status, \
    Medication_Dispense_Status, Medication_Give_Intent, Medication_Order_Intent, Medication_Original_Order_Intent, \
    Medication_Request_Status, Unknown_Code, add_named_organization, add_practitioner, preserve_unmapped, preserve_value
from zato.hl7.mappings.segments.observations import _quantity_from_units
from zato.hl7.mappings.segments.orders import ORC_Handled_Immunization

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strnone
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# Which field positions each mapper consumes - anything else that carries data is preserved as an extension.
_RXA_Immunization_Handled = frozenset({1, 2, 3, 5, 6, 7, 9, 10, 15, 16, 17, 20})
_RXA_Administration_Handled = frozenset({1, 2, 3, 4, 5, 6, 7, 9, 10, 20})
_RXD_Handled = frozenset({1, 2, 3, 4, 5, 7})
_RXE_Handled = frozenset({2, 3, 4, 5})
_RXO_Handled = frozenset({1, 2, 3, 4, 6, 7, 11, 12, 13})
_RXG_Handled = frozenset({3, 4, 5, 7})
_RXR_Handled = frozenset({1, 2})

# Which component of a TQ quantity/timing field carries the start time
_TQ_Start_Component = 4

# ################################################################################################################################
# ################################################################################################################################

def _dose_quantity(
    accessor:'SegmentAccessor',
    amount_position:'int',
    units_position:'int',
    context:'ConversionContext',
    target:'any_',
    ) -> 'stranydict | None':
    """ Builds a dose Quantity from an amount field and its units field.
    Amounts that fail to parse as numbers are preserved on the target resource.
    """
    config = context.config

    amount = accessor.value(amount_position)
    if not amount:
        return None

    units_repetition = accessor.first(units_position)
    units = cwe_to_codeable_concept(units_repetition, config)

    try:
        out = _quantity_from_units(amount, units)
    except ValueError:

        # The whole field is preserved - medication codes can arrive in amount
        # slots and those carry more components than the number alone.
        serialized_amount = accessor.serialize(amount_position)
        preserve_value(target, context, accessor.segment_id, amount_position, serialized_amount)
        return None

    return out

# ################################################################################################################################

def _order_identifiers(orc_accessor:'SegmentAccessor | None', context:'ConversionContext') -> 'anylist':
    """ Collects the placer and filler order numbers from an ORC as identifiers.
    """

    # Our response to produce
    out:'anylist' = []

    if orc_accessor:
        for position in (2, 3):
            order_number_repetition = orc_accessor.first(position)

            if identifier := ei_to_identifier(order_number_repetition, context.config):
                if identifier not in out:
                    out.append(identifier)

    return out

# ################################################################################################################################

def map_rxa(
    accessor:'SegmentAccessor',
    orc_accessor:'SegmentAccessor | None',
    context:'ConversionContext',
    ) -> 'Immunization':
    """ Converts RXA - with its optional ORC - to an Immunization.
    """
    config = context.config

    # Our response to produce
    out = Immunization()

    if context.patient_reference:
        out.patient = context.patient_reference

    # The completion status is required, unknown codes map to the default
    # and are preserved as-is ..
    status_code = accessor.value(20)

    if status := lookup('completion_status', status_code, config):
        out.status = status['code']
    else:
        out.status = Default_Immunization_Status

        if status_code:
            preserve_value(out, context, 'RXA', 20, status_code)

    # .. the administered code is the vaccine ..
    vaccine_repetition = accessor.first(5)

    if vaccine_code := cwe_to_codeable_concept(vaccine_repetition, config):
        out.vaccineCode = vaccine_code

    # .. the administration time is required by FHIR ..
    occurrence_value = accessor.value(3)
    occurrence = dtm_to_datetime(occurrence_value, config)

    if occurrence:
        out.occurrenceDateTime = occurrence

    # .. the administered amount and units make the dose ..
    if dose := _dose_quantity(accessor, 6, 7, context, out):
        out.doseQuantity = dose

    # .. the administration notes become notes ..
    notes:'anylist' = []

    for repetition in accessor.repetitions(9):
        note_text = component_value(repetition, 2)
        if not note_text:
            note_text = component_value(repetition, 1)

        if note_text:
            notes.append({'text': note_text})

    if notes:
        out.note = notes

    # .. the administering provider performs the immunization ..
    provider_repetition = accessor.first(10)

    if performer := add_practitioner(provider_repetition, context):
        out.performer = [{'actor': performer}]

    # .. the lot number and expiration date carry over directly ..
    lot_number = accessor.value(15)
    if lot_number:
        out.lotNumber = lot_number

    expiration_value = accessor.value(16)
    expiration_date = dtm_to_date(expiration_value)

    if expiration_date:
        out.expirationDate = expiration_date

    # .. and the manufacturer becomes an Organization.
    manufacturer_name = accessor.component(17, 2)
    if not manufacturer_name:
        manufacturer_name = accessor.component(17, 1)

    if manufacturer_name:
        out.manufacturer = add_named_organization(manufacturer_name, context)

    # The placer and filler order numbers identify the immunization.
    if identifiers := _order_identifiers(orc_accessor, context):
        out.identifier = identifiers

    if orc_accessor:
        preserve_unmapped(orc_accessor, ORC_Handled_Immunization, out, context)

    preserve_unmapped(accessor, _RXA_Immunization_Handled, out, context)

    return out

# ################################################################################################################################

def map_rxa_to_administration(
    accessor:'SegmentAccessor',
    orc_accessor:'SegmentAccessor | None',
    context:'ConversionContext',
    default_effective:'strnone',
    ) -> 'MedicationAdministration':
    """ Converts RXA - with its optional ORC - to a MedicationAdministration.
    The message time backs the required effective time up when RXA-3 is empty.
    """
    config = context.config

    # Our response to produce
    out = MedicationAdministration()

    if context.patient_reference:
        out.subject = context.patient_reference

    if context.encounter_reference:
        out.context = context.encounter_reference

    # The completion status is required, unknown codes map to the default
    # and are preserved as-is ..
    status_code = accessor.value(20)

    if status := lookup('completion_status', status_code, config):
        out.status = status['code']
    else:
        out.status = Default_Administration_Status

        if status_code:
            preserve_value(out, context, 'RXA', 20, status_code)

    # .. the administered code is the medication, which FHIR requires ..
    medication_repetition = accessor.first(5)

    if medication := cwe_to_codeable_concept(medication_repetition, config):
        out.medicationCodeableConcept = medication
    else:
        out.medicationCodeableConcept = Unknown_Code

    # .. the administration start and end times make the required effective time or period ..
    start_value = accessor.value(3)
    start_time = dtm_to_datetime(start_value, config)

    end_value = accessor.value(4)
    end_time = dtm_to_datetime(end_value, config)

    if start_time:
        if end_time:
            out.effectivePeriod = {'start': start_time, 'end': end_time}
        else:
            out.effectiveDateTime = start_time
    else:
        out.effectiveDateTime = default_effective

    # .. the administered amount and units make the dose ..
    dosage:'stranydict' = {}

    if dose := _dose_quantity(accessor, 6, 7, context, out):
        dosage['dose'] = dose

    if dosage:
        out.dosage = dosage

    # .. the administration notes become notes ..
    notes:'anylist' = []

    for repetition in accessor.repetitions(9):
        note_text = component_value(repetition, 2)
        if not note_text:
            note_text = component_value(repetition, 1)

        if note_text:
            notes.append({'text': note_text})

    if notes:
        out.note = notes

    # .. and the administering provider performs the administration.
    provider_repetition = accessor.first(10)

    if performer := add_practitioner(provider_repetition, context):
        out.performer = [{'actor': performer}]

    # The placer and filler order numbers identify the administration.
    if identifiers := _order_identifiers(orc_accessor, context):
        out.identifier = identifiers

    if orc_accessor:
        preserve_unmapped(orc_accessor, ORC_Handled_Immunization, out, context)

    preserve_unmapped(accessor, _RXA_Administration_Handled, out, context)

    return out

# ################################################################################################################################

def map_rxd(
    accessor:'SegmentAccessor',
    orc_accessor:'SegmentAccessor | None',
    context:'ConversionContext',
    ) -> 'MedicationDispense':
    """ Converts RXD - a pharmacy dispense - to a MedicationDispense.
    """
    config = context.config

    # Our response to produce
    out = MedicationDispense()

    out.status = Medication_Dispense_Status

    if context.patient_reference:
        out.subject = context.patient_reference

    if context.encounter_reference:
        out.context = context.encounter_reference

    # The dispense code is the medication, which FHIR requires ..
    medication_repetition = accessor.first(2)

    if medication := cwe_to_codeable_concept(medication_repetition, config):
        out.medicationCodeableConcept = medication
    else:
        out.medicationCodeableConcept = Unknown_Code

    # .. the dispense time is when the medication was handed over ..
    handed_over_value = accessor.value(3)
    handed_over = dtm_to_datetime(handed_over_value, config)

    if handed_over:
        out.whenHandedOver = handed_over

    # .. and the dispensed amount and units make the quantity.
    if quantity := _dose_quantity(accessor, 4, 5, context, out):
        out.quantity = quantity

    # The prescription number and the placer and filler order numbers identify the dispense.
    identifiers:'anylist' = []

    prescription_repetition = accessor.first(7)

    if prescription := ei_to_identifier(prescription_repetition, config):
        identifiers.append(prescription)

    for identifier in _order_identifiers(orc_accessor, context):
        if identifier not in identifiers:
            identifiers.append(identifier)

    if orc_accessor:
        preserve_unmapped(orc_accessor, ORC_Handled_Immunization, out, context)

    if identifiers:
        out.identifier = identifiers

    preserve_unmapped(accessor, _RXD_Handled, out, context)

    return out

# ################################################################################################################################

def map_rxe(
    accessor:'SegmentAccessor',
    orc_accessor:'SegmentAccessor | None',
    context:'ConversionContext',
    ) -> 'MedicationRequest':
    """ Converts RXE - a pharmacy encoded order - to a MedicationRequest.
    """
    config = context.config

    # Our response to produce
    out = MedicationRequest()

    out.status = Medication_Request_Status
    out.intent = Medication_Order_Intent

    if context.patient_reference:
        out.subject = context.patient_reference

    if context.encounter_reference:
        out.encounter = context.encounter_reference

    # The give code is the medication, which FHIR requires ..
    medication_repetition = accessor.first(2)

    if medication := cwe_to_codeable_concept(medication_repetition, config):
        out.medicationCodeableConcept = medication
    else:
        out.medicationCodeableConcept = Unknown_Code

    # .. the give amounts and units make the dose - a range when both bounds are present,
    # a plain quantity when only the minimum arrived and a high-only range when only
    # the maximum did.
    minimum = _dose_quantity(accessor, 3, 5, context, out)
    maximum = _dose_quantity(accessor, 4, 5, context, out)

    if minimum:
        if maximum:
            dose = {'doseRange': {'low': minimum, 'high': maximum}}
        else:
            dose = {'doseQuantity': minimum}
    elif maximum:
        dose = {'doseRange': {'high': maximum}}
    else:
        dose = None

    if dose:
        out.dosageInstruction = [{'doseAndRate': [dose]}]

    # The placer and filler order numbers identify the request.
    if identifiers := _order_identifiers(orc_accessor, context):
        out.identifier = identifiers

    if orc_accessor:
        preserve_unmapped(orc_accessor, ORC_Handled_Immunization, out, context)

    preserve_unmapped(accessor, _RXE_Handled, out, context)

    return out

# ################################################################################################################################

def map_rxo(
    accessor:'SegmentAccessor',
    orc_accessor:'SegmentAccessor | None',
    context:'ConversionContext',
    ) -> 'MedicationRequest':
    """ Converts RXO - the prescriber's original pharmacy order - to a MedicationRequest.
    """
    config = context.config

    # Our response to produce
    out = MedicationRequest()

    out.status = Medication_Request_Status
    out.intent = Medication_Original_Order_Intent

    if context.patient_reference:
        out.subject = context.patient_reference

    if context.encounter_reference:
        out.encounter = context.encounter_reference

    # The requested give code is the medication, which FHIR requires ..
    medication_repetition = accessor.first(1)

    if medication := cwe_to_codeable_concept(medication_repetition, config):
        out.medicationCodeableConcept = medication
    else:
        out.medicationCodeableConcept = Unknown_Code

    # .. the requested give amounts and units make the dose - a range when both bounds
    # are present, a plain quantity when only the minimum arrived and a high-only range
    # when only the maximum did ..
    minimum = _dose_quantity(accessor, 2, 4, context, out)
    maximum = _dose_quantity(accessor, 3, 4, context, out)

    if minimum:
        if maximum:
            dose = {'doseRange': {'low': minimum, 'high': maximum}}
        else:
            dose = {'doseQuantity': minimum}
    elif maximum:
        dose = {'doseRange': {'high': maximum}}
    else:
        dose = None

    dosage:'stranydict' = {}

    if dose:
        dosage['doseAndRate'] = [dose]

    # .. the provider's administration instructions spell the dosage out in words ..
    instruction_parts:'anylist' = []

    for repetition in accessor.repetitions(7):
        instruction_text = component_value(repetition, 2)
        if not instruction_text:
            instruction_text = component_value(repetition, 1)

        if instruction_text:
            instruction_parts.append(instruction_text)

    if instruction_parts:
        dosage['text'] = '; '.join(instruction_parts)

    if dosage:
        out.dosageInstruction = [dosage]

    # .. the provider's pharmacy instructions become notes ..
    notes:'anylist' = []

    for repetition in accessor.repetitions(6):
        note_text = component_value(repetition, 2)
        if not note_text:
            note_text = component_value(repetition, 1)

        if note_text:
            notes.append({'text': note_text})

    if notes:
        out.note = notes

    # .. and the requested dispense amount, units and refills make the dispense request.
    dispense_request:'stranydict' = {}

    if quantity := _dose_quantity(accessor, 11, 12, context, out):
        dispense_request['quantity'] = quantity

    refills = accessor.value(13)
    if refills:
        if refills.isdigit():
            dispense_request['numberOfRepeatsAllowed'] = int(refills)
        else:
            preserve_value(out, context, 'RXO', 13, refills)

    if dispense_request:
        out.dispenseRequest = dispense_request

    # The placer and filler order numbers identify the request.
    if identifiers := _order_identifiers(orc_accessor, context):
        out.identifier = identifiers

    if orc_accessor:
        preserve_unmapped(orc_accessor, ORC_Handled_Immunization, out, context)

    # The units fields only count as consumed when an amount arrived to pair them with -
    # senders shift other values into unit slots and those must not be lost.
    handled = set(_RXO_Handled)

    if not minimum:
        if not maximum:
            handled.discard(4)

    if 'quantity' not in dispense_request:
        handled.discard(12)

    preserve_unmapped(accessor, frozenset(handled), out, context)

    return out

# ################################################################################################################################

def map_rxg(
    accessor:'SegmentAccessor',
    orc_accessor:'SegmentAccessor | None',
    context:'ConversionContext',
    ) -> 'MedicationRequest':
    """ Converts RXG - a single pharmacy give instruction - to a MedicationRequest.
    """
    config = context.config

    # Our response to produce
    out = MedicationRequest()

    out.status = Medication_Request_Status
    out.intent = Medication_Give_Intent

    if context.patient_reference:
        out.subject = context.patient_reference

    if context.encounter_reference:
        out.encounter = context.encounter_reference

    # The give code is the medication, which FHIR requires ..
    medication_repetition = accessor.first(4)

    if medication := cwe_to_codeable_concept(medication_repetition, config):
        out.medicationCodeableConcept = medication
    else:
        out.medicationCodeableConcept = Unknown_Code

    # .. the give amount and units make the dose, timed by the quantity/timing start.
    dosage:'stranydict' = {}

    if dose := _dose_quantity(accessor, 5, 7, context, out):
        dosage['doseAndRate'] = [{'doseQuantity': dose}]

    timing_value = accessor.component(3, _TQ_Start_Component)
    timing_start = dtm_to_datetime(timing_value, config)

    if timing_start:
        dosage['timing'] = {'event': [timing_start]}

    if dosage:
        out.dosageInstruction = [dosage]

    # The placer and filler order numbers identify the request.
    if identifiers := _order_identifiers(orc_accessor, context):
        out.identifier = identifiers

    if orc_accessor:
        preserve_unmapped(orc_accessor, ORC_Handled_Immunization, out, context)

    preserve_unmapped(accessor, _RXG_Handled, out, context)

    return out

# ################################################################################################################################

def enrich_rxr(accessor:'SegmentAccessor', context:'ConversionContext', target:'any_') -> 'None':
    """ Adds the route and site from RXR to the resource the preceding pharmacy segment produced -
    an Immunization, a MedicationAdministration, a MedicationDispense or a MedicationRequest.
    """
    config = context.config

    route_repetition = accessor.first(1)
    route = cwe_to_codeable_concept(route_repetition, config)

    site_repetition = accessor.first(2)
    site = cwe_to_codeable_concept(site_repetition, config)

    target_dict = target.to_dict()
    resource_type = target_dict['resourceType']

    # An Immunization carries the route and site directly ..
    if resource_type == 'Immunization':
        if route:
            target.route = route

        if site:
            target.site = site

    # .. a MedicationAdministration keeps them in its dosage ..
    elif resource_type == 'MedicationAdministration':

        dosage = target_dict.get('dosage')
        if dosage is None:
            dosage = {}

        if route:
            dosage['route'] = route

        if site:
            dosage['site'] = site

        if dosage:
            target.dosage = dosage

    # .. and a MedicationDispense or a MedicationRequest keeps them in the first dosage instruction.
    else:
        instructions = target_dict.get('dosageInstruction')
        if instructions is None:
            instructions = [{}]

        first_instruction = instructions[0]

        if route:
            first_instruction['route'] = route

        if site:
            first_instruction['site'] = site

        if first_instruction:
            target.dosageInstruction = instructions

    preserve_unmapped(accessor, _RXR_Handled, target, context)

# ################################################################################################################################
# ################################################################################################################################
