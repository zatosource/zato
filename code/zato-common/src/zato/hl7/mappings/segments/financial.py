# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import ChargeItem, Coverage, Organization, RelatedPerson
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.config import Insurer_Authority_Systems
from zato.hl7.mappings.concepts import cwe_to_codeable_concept, parse_number, tag_coding_systems
from zato.hl7.mappings.datatypes import cx_to_identifier, ei_to_identifier, xad_to_address, xpn_to_human_name, \
    xtn_to_contact_points
from zato.hl7.mappings.fields import subcomponent_value
from zato.hl7.mappings.segments.common import Coverage_Class_System, Coverage_Status, Default_Charge_Status, \
    No_Consumed_Fields, Self_Relationship_Codes, absent_value, add_financial_class_extension, add_practitioner, \
    patient_or_absent_reference, preserve_inexact_number, preserve_unmapped, preserve_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict, strnone
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor

# ################################################################################################################################
# ################################################################################################################################

# Which field positions each mapper consumes - anything else that carries data is preserved as an extension.
_IN1_Handled = frozenset({1, 2, 3, 4, 5, 7, 8, 9, 12, 13, 15, 16, 17, 18, 19, 36, 43})
_FT1_Handled = frozenset({1, 2, 3, 4, 6, 7, 10, 20})

# ################################################################################################################################
# ################################################################################################################################

def _map_insured(
    accessor:'SegmentAccessor',
    context:'ConversionContext',
    relationship_code:'strnone',
    ) -> 'RelatedPerson | None':
    """ Builds the RelatedPerson the insured is from the name, date of birth, address and sex in IN1 -
    None when IN1 names no one, an insured's sex that is not a known code is preserved on the person.
    """
    # Our response to produce
    out = RelatedPerson()

    config = context.config

    names:'anylist' = []

    for repetition in accessor.repetitions(16):
        if name := xpn_to_human_name(repetition, config):
            names.append(name)

    # An IN1 with no name in it names no insured.
    if not names:
        return None

    out.patient = patient_or_absent_reference(context)
    out.name = names

    # The insured's relationship to the patient is the person's relationship, when it is a known code ..
    if relationship_code:
        if relationship := lookup('personal_relationship', relationship_code, config):
            coding = {'system': relationship['system'], 'code': relationship['code']}
            out.relationship = [{'coding': [coding]}]

    # .. the date of birth carries over when it reads as a date, otherwise it is preserved as-is ..
    birth_date = accessor.value(18)
    birth = context.date(birth_date, 'IN1', 18)

    if birth:
        out.birthDate = birth
    elif birth_date:
        preserve_value(out, context, 'IN1', 18, birth_date)

    addresses:'anylist' = []

    for repetition in accessor.repetitions(19):
        if address := xad_to_address(repetition, config):
            addresses.append(address)

    if addresses:
        out.address = addresses

    # .. and the administrative sex maps to the gender code, unknown codes are preserved as-is.
    sex_code = accessor.value(43)

    if sex_code:
        if gender := lookup('administrative_sex', sex_code, config):
            out.gender = gender['code']
        else:
            preserve_value(out, context, 'IN1', 43, sex_code)

    return out

# ################################################################################################################################

def map_in1(accessor:'SegmentAccessor', context:'ConversionContext') -> 'Coverage':
    """ Converts IN1 to a Coverage with its payor Organization.
    """
    config = context.config

    # Our response to produce
    out = Coverage()

    out.status = Coverage_Status

    # The patient the coverage benefits, or the statement that none is known.
    out.beneficiary = patient_or_absent_reference(context)

    # The insurance company becomes the payor Organization ..
    organization = Organization()
    has_organization = False

    company_name_repetition = accessor.first(4)
    company_name = subcomponent_value(company_name_repetition, 1, 1)

    if company_name:
        organization.name = company_name
        has_organization = True

    company_identifiers:'anylist' = []

    # The company IDs identify an insurer, so insurer-registry authorities apply.
    for repetition in accessor.repetitions(3):
        if identifier := cx_to_identifier(repetition, config, Insurer_Authority_Systems):
            company_identifiers.append(identifier)

    if company_identifiers:
        organization.identifier = company_identifiers
        has_organization = True

    # .. with its address and telecoms ..
    company_addresses:'anylist' = []

    for repetition in accessor.repetitions(5):
        if address := xad_to_address(repetition, config):
            company_addresses.append(address)

    if company_addresses:
        organization.address = company_addresses
        has_organization = True

    company_telecoms:'anylist' = []

    for repetition in accessor.repetitions(7):
        for telecom in xtn_to_contact_points(repetition, config, default_use='work'):
            company_telecoms.append(telecom)

    if company_telecoms:
        organization.telecom = company_telecoms
        has_organization = True

    # .. an IN1 that does not identify the insurance company states the payor's absence.
    if has_organization:
        payor_reference = context.add(organization)
    else:
        payor_reference = absent_value()

    out.payor = [payor_reference]

    # The plan type maps to the coverage type, or the visit's financial class does when there is no plan type -
    # .. a financial class next to a plan type becomes an extension ..
    plan_type_repetition = accessor.first(15)
    coverage_type = cwe_to_codeable_concept(plan_type_repetition, config)

    if coverage_type:
        out.type_ = coverage_type

    if financial_class := context.financial_class:
        if coverage_type:
            add_financial_class_extension(out, context, financial_class)
        else:
            out.type_ = financial_class

    # .. the plan itself and the group become class entries ..
    classes:'anylist' = []

    plan_id = accessor.value(2)
    if plan_id:
        plan_class = {
            'type': {'coding': [{'system': Coverage_Class_System, 'code': 'plan'}]},
            'value': plan_id,
        }
        classes.append(plan_class)

    group_number = accessor.value(8)
    group_name = accessor.component(9, 1)

    if group_number:
        group_class = {
            'type': {'coding': [{'system': Coverage_Class_System, 'code': 'group'}]},
            'value': group_number,
        }

        if group_name:
            group_class['name'] = group_name

        classes.append(group_class)

    elif group_name:
        group_class = {
            'type': {'coding': [{'system': Coverage_Class_System, 'code': 'group'}]},
            'value': group_name,
        }
        classes.append(group_class)

    if classes:
        out.class_ = classes

    # .. the plan dates bound the coverage period ..
    period:'stranydict' = {}

    effective_value = accessor.value(12)
    effective_date = context.date(effective_value, 'IN1', 12)

    if effective_date:
        period['start'] = effective_date

    expiration_value = accessor.value(13)
    expiration_date = context.date(expiration_value, 'IN1', 13)

    if expiration_date:
        period['end'] = expiration_date

    if period:
        out.period = period

    # .. the insured's relationship decides who the subscriber is,
    # .. with standard table codes translating to subscriber-relationship ..
    relationship_code = accessor.value(17)
    relationship_repetition = accessor.first(17)

    if relationship := cwe_to_codeable_concept(relationship_repetition, config):
        tag_coding_systems(relationship, 'subscriber_relationship', config)
        out.relationship = relationship

    is_self = False

    if relationship_code:
        if relationship_code.upper() in Self_Relationship_Codes:
            is_self = True

    # .. the patient is their own subscriber - the insured's details repeat the patient's -
    # .. and anyone else becomes a RelatedPerson ..
    if is_self:
        if context.patient_reference:
            out.subscriber = context.patient_reference

    elif subscriber := _map_insured(accessor, context, relationship_code):
        out.subscriber = context.add(subscriber)

    # .. and the policy number doubles as the identifier and the subscriber ID.
    policy_number = accessor.value(36)
    if policy_number:
        out.identifier = [{'value': policy_number}]
        out.subscriberId = policy_number

    preserve_unmapped(accessor, _IN1_Handled, out, context)

    return out

# ################################################################################################################################

def apply_in2(accessor:'SegmentAccessor', context:'ConversionContext', coverage:'Coverage') -> 'None':
    """ Preserves everything IN2 - additional insurance data - carries on the Coverage.
    """
    preserve_unmapped(accessor, No_Consumed_Fields, coverage, context)

# ################################################################################################################################

def map_ft1(accessor:'SegmentAccessor', context:'ConversionContext') -> 'ChargeItem':
    """ Converts FT1 - a financial transaction - to a ChargeItem.
    """
    config = context.config

    # Our response to produce
    out = ChargeItem()

    # The patient the charge concerns, or the statement that none is known.
    out.subject = patient_or_absent_reference(context)

    if context.encounter_reference:
        out.context = context.encounter_reference

    # The transaction type decides the status, unknown codes map to the default
    # and are preserved as-is ..
    type_code = accessor.value(6)

    if status := lookup('transaction_type', type_code, config):
        out.status = status['code']
    else:
        out.status = Default_Charge_Status

        if type_code:
            # The slot can carry a full coded value, so all its components survive.
            serialized_type = accessor.serialize(6)
            preserve_value(out, context, 'FT1', 6, serialized_type)

    # .. the transaction code is the charge code, or the statement that none is known ..
    code_repetition = accessor.first(7)

    if code := cwe_to_codeable_concept(code_repetition, config):
        out.code = code
    else:
        out.code = absent_value()

    # .. the transaction and batch IDs become identifiers ..
    identifiers:'anylist' = []

    for position in (2, 3):
        identifier_repetition = accessor.first(position)

        if identifier := ei_to_identifier(identifier_repetition, config):
            identifiers.append(identifier)

    if identifiers:
        out.identifier = identifiers

    # .. the transaction date is when the charge occurred, values that are
    # .. not dates at all are preserved as-is ..
    transaction_value = accessor.value(4)
    transaction_time = context.datetime(transaction_value, 'FT1', 4)

    if transaction_time:
        out.occurrenceDateTime = transaction_time
    elif transaction_value:
        preserve_value(out, context, 'FT1', 4, transaction_value)

    # .. the transaction quantity carries over when it is a number, keeping its digits
    # .. as an extension when the float cannot carry them exactly ..
    quantity = accessor.value(10)

    if quantity:
        if number := parse_number(quantity):
            out.quantity = {'value': number.value}

            if not number.is_exact:
                preserve_inexact_number(out, context, 'FT1', 10, quantity)
        else:
            preserve_value(out, context, 'FT1', 10, quantity)

    # .. and the performing practitioners complete the picture.
    performers:'anylist' = []

    for repetition in accessor.repetitions(20):
        if reference := add_practitioner(repetition, context):
            performers.append({'actor': reference})

    if performers:
        out.performer = performers

    preserve_unmapped(accessor, _FT1_Handled, out, context)

    return out

# ################################################################################################################################
# ################################################################################################################################
