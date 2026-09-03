# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import Practitioner, ServiceRequest
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.datatypes import ei_to_identifier, xad_to_address, xpn_to_human_name, xtn_to_contact_points
from zato.hl7.mappings.fields import component_value
from zato.hl7.mappings.segments.common import Default_Order_Status, absent_subject_reference, append_to_list_field, \
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
_RF1_Handled = frozenset({1, 2, 3, 6, 7, 8, 9, 10, 11})
_PRD_Handled = frozenset({1, 2, 3, 5, 7})

# The provider roles of table HL70286 that wire a referral's practitioners up -
# the referring provider requested the referral and the referred-to one will perform it.
_Referring_Provider = 'RP'
_Referred_To_Provider = 'RT'

# ################################################################################################################################
# ################################################################################################################################

def map_rf1(accessor:'SegmentAccessor', context:'ConversionContext') -> 'ServiceRequest':
    """ Converts RF1 - referral information - to the ServiceRequest that carries the referral.
    """
    config = context.config

    # Our response to produce
    out = ServiceRequest()

    out.intent = 'order'

    # In a referral message the RF1 precedes the PID, so the subject starts out
    # explicitly absent and the end of the walk fills the patient in.
    if context.patient_reference:
        out.subject = context.patient_reference
    else:
        out.subject = absent_subject_reference()

    # The referral status is required, unknown codes map to the default and are preserved as-is ..
    status_code = accessor.value(1)

    if status := lookup('referral_status', status_code, config):
        out.status = status['code']
    else:
        out.status = Default_Order_Status

        if status_code:
            preserve_value(out, context, 'RF1', 1, status_code)

    # .. the referral priority maps through the standard table ..
    priority_code = accessor.value(2)

    if priority := lookup('order_priority', priority_code, config):
        out.priority = priority['code']
    else:
        if priority_code:
            preserve_value(out, context, 'RF1', 2, priority_code)

    # .. the referral type is the requested code ..
    type_repetition = accessor.first(3)

    if code := cwe_to_codeable_concept(type_repetition, config):
        out.code = code

    # .. the originating and external referral identifiers all become identifiers ..
    identifiers:'anylist' = []

    originating_repetition = accessor.first(6)

    if identifier := ei_to_identifier(originating_repetition, config):
        identifiers.append(identifier)

    for repetition in accessor.repetitions(11):
        if identifier := ei_to_identifier(repetition, config):
            if identifier not in identifiers:
                identifiers.append(identifier)

    if identifiers:
        out.identifier = identifiers

    # .. the effective and expiration dates make the occurrence time or period ..
    effective_value = accessor.value(7)
    effective_time = context.datetime(effective_value, 'RF1', 7)

    expiration_value = accessor.value(8)
    expiration_time = context.datetime(expiration_value, 'RF1', 8)

    if effective_time:
        if expiration_time:
            out.occurrencePeriod = {'start': effective_time, 'end': expiration_time}
        else:
            out.occurrenceDateTime = effective_time
    elif expiration_time:
        out.occurrencePeriod = {'end': expiration_time}

    # .. the process date is when the referral was authored ..
    authored_value = accessor.value(9)
    authored = context.datetime(authored_value, 'RF1', 9)

    if authored:
        out.authoredOn = authored

    # .. and each referral reason completes the picture.
    reasons:'anylist' = []

    for repetition in accessor.repetitions(10):
        if reason := cwe_to_codeable_concept(repetition, config):
            reasons.append(reason)

    if reasons:
        out.reasonCode = reasons

    preserve_unmapped(accessor, _RF1_Handled, out, context)

    return out

# ################################################################################################################################

def _prd_practitioner(accessor:'SegmentAccessor', context:'ConversionContext') -> 'Practitioner | None':
    """ Builds a Practitioner from the name, address, telecom and identifier fields of a PRD.
    """
    config = context.config

    # Our response to produce
    out = Practitioner()

    is_populated = False

    # Every repetition of the name field becomes a HumanName ..
    names:'anylist' = []

    for repetition in accessor.repetitions(2):
        if name := xpn_to_human_name(repetition, config):
            names.append(name)

    if names:
        out.name = names
        is_populated = True

    # .. the addresses follow ..
    addresses:'anylist' = []

    for repetition in accessor.repetitions(3):
        if address := xad_to_address(repetition, config):
            addresses.append(address)

    if addresses:
        out.address = addresses
        is_populated = True

    # .. so does the contact information ..
    telecoms:'anylist' = []

    for repetition in accessor.repetitions(5):
        for telecom in xtn_to_contact_points(repetition, config, default_use='work'):
            telecoms.append(telecom)

    if telecoms:
        out.telecom = telecoms
        is_populated = True

    # .. and each provider identifier becomes an identifier, its type spelled out when given.
    identifiers:'anylist' = []

    for repetition in accessor.repetitions(7):
        id_number = component_value(repetition, 1)
        if id_number:
            identifier:'stranydict' = {'value': id_number}

            id_type = component_value(repetition, 2)
            if id_type:
                identifier['type'] = {'text': id_type}

            identifiers.append(identifier)

    if identifiers:
        out.identifier = identifiers
        is_populated = True

    if not is_populated:
        return None

    return out

# ################################################################################################################################

def apply_prd(
    accessor:'SegmentAccessor',
    context:'ConversionContext',
    service_request:'ServiceRequest | None',
    ) -> 'None':
    """ Converts PRD - provider data from a referral - to a Practitioner, wiring the referring
    provider up as the referral's requester and the referred-to one as its performer.
    """
    practitioner = _prd_practitioner(accessor, context)
    if not practitioner:
        return

    role_code = accessor.component(1, 1)

    # A role outside the two the referral consumes stays on the practitioner as-is.
    if role_code not in (_Referring_Provider, _Referred_To_Provider):
        if role_code:
            preserve_value(practitioner, context, 'PRD', 1, role_code)

    reference = context.add(practitioner)

    preserve_unmapped(accessor, _PRD_Handled, practitioner, context)

    if not service_request:
        return

    # The referring provider requested the referral ..
    if role_code == _Referring_Provider:
        service_request.requester = reference

    # .. and the referred-to provider is asked to perform it.
    elif role_code == _Referred_To_Provider:
        append_to_list_field(service_request, 'performer', reference)

# ################################################################################################################################
# ################################################################################################################################
