# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from dataclasses import dataclass

# Zato
from zato.common.b2b.ebms2.common import Actor, EbMS2Exception, Error_Code_Context, ErrorCode, MessageStatus, NS, \
    Severity
from zato.common.b2b.ebms2.header import HeaderParty, parse_header_party
from zato.common.b2b.ebms2.xml_ import add_body_element, add_description, add_eb, add_header_block, check_extension, \
    find_all_eb, find_eb, get_eb_attribute, location, optional_eb_text, parse_timestamp, require_eb_attribute, \
    require_eb_text, set_eb_attribute, SOAP_Actor, XML_Lang
from zato.common.util.xml_.core import qname, to_timestamp

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import any_, anylist, dtnone
    any_ = any_
    anylist = anylist
    datetime = datetime
    dtnone = dtnone

# ################################################################################################################################
# ################################################################################################################################

_ds_reference = qname(NS.DS, 'Reference')

_severities = {Severity.Warning, Severity.Error}

_message_statuses = {
    MessageStatus.Unauthorized,
    MessageStatus.Not_Recognized,
    MessageStatus.Received,
    MessageStatus.Processed,
    MessageStatus.Forwarded,
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Acknowledgment:
    timestamp:         'datetime'
    ref_to_message_id: str
    from_party:        'HeaderParty | None' = None
    actor:             str = Actor.To_Party_MSH

    # Copies of the ds:Reference elements of the signature of the acknowledged message.
    references: 'anylist'

    def __init__(self) -> 'None':
        self.references = []

# ################################################################################################################################

@dataclass(init=False)
class MessageError:
    """ One eb:Error of an eb:ErrorList.
    """
    error_code:   str
    severity:     str = Severity.Error
    location:     str = ''
    description:  str = ''
    code_context: str = Error_Code_Context
    error_id:     str = ''

message_error_list = list[MessageError]

# ################################################################################################################################

@dataclass(init=False)
class ErrorList:
    errors: 'message_error_list'

    def __init__(self) -> 'None':
        self.errors = []

    @property
    def highest_severity(self) -> 'str':
        for error in self.errors:
            if error.severity == Severity.Error:
                out = Severity.Error
                break
        else:
            out = Severity.Warning

        return out

# ################################################################################################################################

@dataclass(init=False)
class StatusRequest:
    ref_to_message_id: str

# ################################################################################################################################

@dataclass(init=False)
class StatusResponse:
    ref_to_message_id: str
    message_status:    str
    timestamp:         'dtnone' = None

# ################################################################################################################################
# ################################################################################################################################

def new_error_list(error_code:'str', detail:'str', error_location:'str'='', severity:'str'=Severity.Error) -> 'ErrorList':
    """ Returns an error list with a single error.
    """
    error = MessageError()
    error.error_code = error_code
    error.severity = severity
    error.location = error_location
    error.description = detail

    out = ErrorList()
    out.errors.append(error)

    return out

# ################################################################################################################################
# ################################################################################################################################

def add_acknowledgment(soap_header:'any_', acknowledgment:'Acknowledgment') -> 'None':

    element = add_header_block(soap_header, 'Acknowledgment')
    element.set(SOAP_Actor, acknowledgment.actor)

    timestamp = to_timestamp(acknowledgment.timestamp)

    _ = add_eb(element, 'Timestamp', timestamp)
    _ = add_eb(element, 'RefToMessageId', acknowledgment.ref_to_message_id)

    if from_party := acknowledgment.from_party:

        from_element = add_eb(element, 'From')

        for party_id in from_party.party_ids:
            party_id_element = add_eb(from_element, 'PartyId', party_id.value)
            set_eb_attribute(party_id_element, 'type', party_id.id_type)

        if from_party.role:
            _ = add_eb(from_element, 'Role', from_party.role)

    for reference in acknowledgment.references:
        reference_copy = deepcopy(reference)
        element.append(reference_copy)

# ################################################################################################################################

def add_error_list(soap_header:'any_', error_list:'ErrorList') -> 'None':

    element = add_header_block(soap_header, 'ErrorList')
    set_eb_attribute(element, 'highestSeverity', error_list.highest_severity)

    for error in error_list.errors:

        error_element = add_eb(element, 'Error')
        set_eb_attribute(error_element, 'id', error.error_id)
        set_eb_attribute(error_element, 'codeContext', error.code_context)
        set_eb_attribute(error_element, 'errorCode', error.error_code)
        set_eb_attribute(error_element, 'severity', error.severity)
        set_eb_attribute(error_element, 'location', error.location)

        if error.description:
            add_description(error_element, error.description)

# ################################################################################################################################

def add_status_request(soap_body:'any_', status_request:'StatusRequest') -> 'None':
    element = add_body_element(soap_body, 'StatusRequest')
    _ = add_eb(element, 'RefToMessageId', status_request.ref_to_message_id)

# ################################################################################################################################

def add_status_response(soap_body:'any_', status_response:'StatusResponse') -> 'None':

    element = add_body_element(soap_body, 'StatusResponse')
    set_eb_attribute(element, 'messageStatus', status_response.message_status)

    _ = add_eb(element, 'RefToMessageId', status_response.ref_to_message_id)

    if status_response.timestamp:
        timestamp = to_timestamp(status_response.timestamp)
        _ = add_eb(element, 'Timestamp', timestamp)

# ################################################################################################################################
# ################################################################################################################################

def parse_acknowledgment(element:'any_') -> 'Acknowledgment':

    where = location('Acknowledgment')
    check_extension(element, where, is_header=True)

    timestamp = require_eb_text(element, 'Timestamp', where)

    out = Acknowledgment()
    out.timestamp = parse_timestamp(timestamp, where)
    out.ref_to_message_id = require_eb_text(element, 'RefToMessageId', where)

    if actor := element.get(SOAP_Actor):
        out.actor = actor

    if (from_element := find_eb(element, 'From')) is not None:
        from_where = location('Acknowledgment', 'From')
        out.from_party = parse_header_party(from_element, from_where)

    for reference in element.iter(_ds_reference):
        out.references.append(reference)

    return out

# ################################################################################################################################

def parse_error_list(element:'any_') -> 'ErrorList':

    where = location('ErrorList')
    check_extension(element, where, is_header=True)

    out = ErrorList()

    for error_element in find_all_eb(element, 'Error'):

        error_where = location('ErrorList', 'Error')

        error = MessageError()
        error.error_code = require_eb_attribute(error_element, 'errorCode', error_where)
        error.severity = require_eb_attribute(error_element, 'severity', error_where)

        if error.severity not in _severities:
            raise EbMS2Exception(ErrorCode.Inconsistent, f'Unknown severity `{error.severity}`', error_where)

        if (error_location := get_eb_attribute(error_element, 'location')) is not None:
            error.location = error_location

        if (code_context := get_eb_attribute(error_element, 'codeContext')) is not None:
            error.code_context = code_context

        if (error_id := get_eb_attribute(error_element, 'id')) is not None:
            error.error_id = error_id

        if (description := find_eb(error_element, 'Description')) is not None:
            if description.text:
                error.description = description.text.strip()
            if description.get(XML_Lang) is None:
                raise EbMS2Exception(ErrorCode.Inconsistent, 'Attribute `xml:lang` is missing', error_where)

        out.errors.append(error)

    if not out.errors:
        raise EbMS2Exception(ErrorCode.Inconsistent, 'Element `Error` is missing', where)

    return out

# ################################################################################################################################

def parse_status_request(element:'any_') -> 'StatusRequest':

    where = location('StatusRequest')
    check_extension(element, where, is_header=False)

    out = StatusRequest()
    out.ref_to_message_id = require_eb_text(element, 'RefToMessageId', where)

    return out

# ################################################################################################################################

def parse_status_response(element:'any_') -> 'StatusResponse':

    where = location('StatusResponse')
    check_extension(element, where, is_header=False)

    out = StatusResponse()
    out.ref_to_message_id = require_eb_text(element, 'RefToMessageId', where)
    out.message_status = require_eb_attribute(element, 'messageStatus', where)

    if out.message_status not in _message_statuses:
        raise EbMS2Exception(ErrorCode.Inconsistent, f'Unknown message status `{out.message_status}`', where)

    if timestamp := optional_eb_text(element, 'Timestamp', where):
        out.timestamp = parse_timestamp(timestamp, where)

    return out

# ################################################################################################################################
# ################################################################################################################################
