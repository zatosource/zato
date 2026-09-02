# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import ChargeItem, Coverage, Organization
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.config import Insurer_Authority_Systems
from zato.hl7.mappings.concepts import cwe_to_codeable_concept, tag_coding_systems
from zato.hl7.mappings.datatypes import cx_to_identifier, dtm_to_date, dtm_to_datetime, ei_to_identifier, \
    xad_to_address, xtn_to_contact_points
from zato.hl7.mappings.fields import subcomponent_value
from zato.hl7.mappings.segments.common import Coverage_Class_System, Coverage_Status, Default_Charge_Status, \
    No_Consumed_Fields, Self_Relationship_Codes, Unknown_Code, Unknown_Payor_Name, add_practitioner, \
    preserve_unmapped, preserve_value

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

# Which field positions each mapper consumes - anything else that carries data is preserved as an extension.
_IN1_Handled = frozenset({1, 2, 3, 4, 5, 7, 8, 9, 12, 13, 15, 16, 17, 36})
_FT1_Handled = frozenset({1, 2, 3, 4, 6, 7, 10, 20})

# ################################################################################################################################
# ################################################################################################################################

def map_in1(accessor:'SegmentAccessor', context:'ConversionContext') -> 'Coverage':
    """ Converts IN1 to a Coverage with its payor Organization.
    """
    config = context.config

    # Our response to produce
    out = Coverage()

    out.status = Coverage_Status

    if context.patient_reference:
        out.beneficiary = context.patient_reference

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

    # .. FHIR requires a payor even when IN1 does not identify the insurance company.
    if not has_organization:
        organization.name = Unknown_Payor_Name

    payor_reference = context.add(organization)
    out.payor = [payor_reference]

    # The plan type maps to the coverage type ..
    plan_type_repetition = accessor.first(15)

    if coverage_type := cwe_to_codeable_concept(plan_type_repetition, config):
        out.type_ = coverage_type

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
    effective_date = dtm_to_date(effective_value)

    if effective_date:
        period['start'] = effective_date

    expiration_value = accessor.value(13)
    expiration_date = dtm_to_date(expiration_value)

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

    if is_self:
        if context.patient_reference:
            out.subscriber = context.patient_reference

    # .. the insured's name repeats the patient's when the insured is the patient,
    # .. anyone else is preserved as-is ..
    insured_name = accessor.component(16, 1)
    if insured_name:
        if not is_self:
            serialized_name = accessor.serialize(16)
            preserve_value(out, context, 'IN1', 16, serialized_name)

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

    if context.patient_reference:
        out.subject = context.patient_reference

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

    # .. the transaction code is the charge code, which FHIR requires ..
    code_repetition = accessor.first(7)

    if code := cwe_to_codeable_concept(code_repetition, config):
        out.code = code
    else:
        out.code = Unknown_Code

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
    transaction_time = dtm_to_datetime(transaction_value, config)

    if transaction_time:
        out.occurrenceDateTime = transaction_time
    elif transaction_value:
        preserve_value(out, context, 'FT1', 4, transaction_value)

    # .. the transaction quantity carries over when it is a number ..
    quantity = accessor.value(10)
    if quantity:
        try:
            out.quantity = {'value': float(quantity)}
        except ValueError:
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
