# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.fhir import MessageHeader, OperationOutcome
from zato.hl7.mappings.codes import lookup
from zato.hl7.mappings.concepts import cwe_to_codeable_concept
from zato.hl7.mappings.datatypes import hd_to_system
from zato.hl7.mappings.segments.common import Default_Issue_Severity, Default_Issue_Type, Default_Message_Endpoint, \
    Message_Event_System, No_Consumed_Fields, add_hd_organization, preserve_unmapped, preserve_value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    from zato.hl7.mappings.context import ConversionContext
    from zato.hl7.mappings.fields import SegmentAccessor
    ConversionContext = ConversionContext
    SegmentAccessor = SegmentAccessor

# ################################################################################################################################
# ################################################################################################################################

# Which field positions each mapper consumes - anything else that carries data is preserved as an extension.
# MSH-7, 10 and 11 are consumed at the bundle level - the timestamp, the identifier and the meta tag.
_MSH_Handled = frozenset({1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12})
_SFT_Handled = frozenset({2, 3})
_MSA_Handled = frozenset({1, 2})
_ERR_Handled = frozenset({3, 4})

# ################################################################################################################################
# ################################################################################################################################

def map_msh(accessor:'SegmentAccessor', context:'ConversionContext') -> 'MessageHeader':
    """ Converts MSH to a MessageHeader with the sending and receiving systems and facilities.
    """
    config = context.config

    # Our response to produce
    out = MessageHeader()

    # The trigger event identifies what kind of message this is ..
    event_code = accessor.component(9, 2)
    if not event_code:
        event_code = accessor.component(9, 1)

    event_coding:'stranydict' = {'system': Message_Event_System}
    if event_code:
        event_coding['code'] = event_code

    out.eventCoding = event_coding

    # .. the sending application and facility become the source ..
    source:'stranydict' = {}

    sending_application = accessor.component(3, 1)
    sending_universal_id = accessor.component(3, 2)
    sending_universal_id_type = accessor.component(3, 3)

    if sending_application:
        source['name'] = sending_application

    source_endpoint = hd_to_system(sending_application, sending_universal_id, sending_universal_id_type, config)
    if not source_endpoint:
        source_endpoint = Default_Message_Endpoint

    source['endpoint'] = source_endpoint
    out.source = source

    # .. the sending facility becomes the sender Organization ..
    sending_facility = accessor.first(4)

    if sender := add_hd_organization(sending_facility, context):
        out.sender = sender

    # .. the receiving application and facility become the destination ..
    destination:'stranydict' = {}

    receiving_application = accessor.component(5, 1)
    receiving_universal_id = accessor.component(5, 2)
    receiving_universal_id_type = accessor.component(5, 3)

    if receiving_application:
        destination['name'] = receiving_application

    destination_endpoint = hd_to_system(
        receiving_application, receiving_universal_id, receiving_universal_id_type, config)

    if not destination_endpoint:
        destination_endpoint = Default_Message_Endpoint

    destination['endpoint'] = destination_endpoint

    # .. with the receiving facility as its receiver Organization.
    receiving_facility = accessor.first(6)

    if receiver := add_hd_organization(receiving_facility, context):
        destination['receiver'] = receiver

    out.destination = [destination]

    preserve_unmapped(accessor, _MSH_Handled, out, context)

    return out

# ################################################################################################################################

def enrich_sft(accessor:'SegmentAccessor', context:'ConversionContext', message_header:'MessageHeader') -> 'None':
    """ Adds the sending software's name and version from SFT to the MessageHeader source.
    """

    # The source is a plain dict on the typed resource, so it mutates through its serialized form.
    header_dict = message_header.to_dict()
    source = header_dict['source']

    software_name = accessor.value(3)
    if software_name:
        source['software'] = software_name

    software_version = accessor.value(2)
    if software_version:
        source['version'] = software_version

    message_header.source = source

    preserve_unmapped(accessor, _SFT_Handled, message_header, context)

# ################################################################################################################################

def apply_msa(accessor:'SegmentAccessor', context:'ConversionContext', message_header:'MessageHeader') -> 'None':
    """ Turns MSA into the MessageHeader's response - the acknowledged control ID and the outcome.
    """
    config = context.config

    acknowledgment = accessor.value(1)
    control_id = accessor.value(2)

    # A response needs both the control ID it acknowledges and a recognized outcome code.
    response_code = lookup('acknowledgment_code', acknowledgment, config)

    if control_id:
        if response_code:
            message_header.response = {'identifier': control_id, 'code': response_code['code']}

            preserve_unmapped(accessor, _MSA_Handled, message_header, context)
            return

    # Without them, the whole segment is preserved as-is.
    preserve_unmapped(accessor, No_Consumed_Fields, message_header, context)

# ################################################################################################################################

def map_err(
    accessor:'SegmentAccessor',
    context:'ConversionContext',
    message_header:'MessageHeader',
    ) -> 'OperationOutcome':
    """ Converts ERR to an OperationOutcome the MessageHeader's response points at.
    """
    config = context.config

    # Our response to produce
    out = OperationOutcome()

    issue:'stranydict' = {}

    # The severity comes from ERR-4, with a constant default ..
    severity_code = accessor.value(4)

    if severity := lookup('error_severity', severity_code, config):
        issue['severity'] = severity['code']
    else:
        issue['severity'] = Default_Issue_Severity

        if severity_code:
            preserve_value(out, context, 'ERR', 4, severity_code)

    # .. the HL7 error code from ERR-3 decides the issue type and its details.
    error_code = accessor.value(3)

    if issue_type := lookup('error_code', error_code, config):
        issue['code'] = issue_type['code']
    else:
        issue['code'] = Default_Issue_Type

    error_repetition = accessor.first(3)

    if details := cwe_to_codeable_concept(error_repetition, config):
        issue['details'] = details

    out.issue = [issue]

    preserve_unmapped(accessor, _ERR_Handled, out, context)

    # The response, when MSA created one, points at this outcome.
    outcome_reference = context.add(out)
    header_dict = message_header.to_dict()

    if response := header_dict.get('response'):
        response['details'] = outcome_reference
        message_header.response = response

    return out

# ################################################################################################################################
# ################################################################################################################################
