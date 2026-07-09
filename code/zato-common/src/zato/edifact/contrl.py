# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The CONTRL syntax and service report message - the EDIFACT acknowledgment.
# UCI answers for the whole interchange, one UCM answers for each message
# and UCS/UCD carry the segment and element level detail of a rejection.

from __future__ import annotations

# stdlib
from datetime import datetime, timezone
from typing import cast as cast_

# Zato
from zato.edifact.base import EDIComponent, EDIComposite, EDIElement, EDIGroup, EDIGroupAttr, EDIMessage, \
     EDIRepeatableList, EDISegment, EDISegmentAttr, Usage
from zato.edifact.envelope import EDIEnvelopeError, EDIInterchange
from zato.edifact.service import DateTimeOfPreparation, MessageIdentifier, UNB, UNH, UNT, UNZ
from zato.edifact.syntax import RawSegment

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Any  # noqa: F401

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
any_    = 'Any'
anylist = list['Any']
strlist = list[str]

contrl_error_list      = list['ContrlError']
contrl_error_dict      = dict[str, contrl_error_list]
contrl_error_dict_none = 'contrl_error_dict | None'

# ################################################################################################################################
# ################################################################################################################################

# The 0083 action codes - the interchange or message was acknowledged or rejected.
Action_Acknowledged = '7'
Action_Rejected     = '4'

# The control reference a built CONTRL interchange uses for itself.
Default_Control_Reference = '1'

# The wire formats of the UNB preparation date and time.
UNB_Date_Format = '%y%m%d'
UNB_Time_Format = '%H%M'

# ################################################################################################################################
# ################################################################################################################################

def _element_value(raw_segment:'RawSegment', position:'int') -> 'str':
    """ Returns the first component of the element at the given 1-based position,
    or an empty string when the element is absent from the wire data.
    """
    index = position - 1
    element_count = len(raw_segment.elements)

    if index >= element_count:
        return ''

    components = raw_segment.elements[index]
    if not components:
        return ''

    out = components[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class DataElementIdentification(EDIComposite):
    """ S011 - where in a segment an element error sits, the element position
    with an optional component position.
    """
    element_position   = EDIComponent[str](position=1, usage=Usage.REQUIRED, format='n..3')
    component_position = EDIComponent[str](position=2, usage=Usage.OPTIONAL, format='n..3')

# ################################################################################################################################
# ################################################################################################################################

class UCI(EDISegment):
    """ Interchange response - the disposition of the whole acknowledged interchange,
    echoing its control reference, sender and recipient.
    """
    _segment_tag = 'UCI'

    control_reference = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..14')
    sender            = EDIElement[any_](position=2, usage=Usage.REQUIRED, composite='InterchangeParty')
    recipient         = EDIElement[any_](position=3, usage=Usage.REQUIRED, composite='InterchangeParty')
    action_code       = EDIElement[str](position=4, usage=Usage.REQUIRED, format='an..3')
    error_code        = EDIElement[str](position=5, usage=Usage.OPTIONAL, format='an..3')

# ################################################################################################################################

class UCM(EDISegment):
    """ Message response - the disposition of one acknowledged message,
    echoing its reference number and message identifier.
    """
    _segment_tag = 'UCM'

    message_reference = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..14')
    identifier        = EDIElement[MessageIdentifier](position=2, usage=Usage.REQUIRED, composite='MessageIdentifier')
    action_code       = EDIElement[str](position=3, usage=Usage.REQUIRED, format='an..3')
    error_code        = EDIElement[str](position=4, usage=Usage.OPTIONAL, format='an..3')

# ################################################################################################################################

class UCS(EDISegment):
    """ Segment error indication - which segment of the acknowledged message was in error.
    """
    _segment_tag = 'UCS'

    segment_position = EDIElement[str](position=1, usage=Usage.REQUIRED, format='n..6')
    error_code       = EDIElement[str](position=2, usage=Usage.OPTIONAL, format='an..3')

# ################################################################################################################################

class UCD(EDISegment):
    """ Data element error indication - which element of the segment in error
    the error code applies to.
    """
    _segment_tag = 'UCD'

    error_code = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..3')
    position   = EDIElement[DataElementIdentification](position=2, usage=Usage.REQUIRED,
        composite='DataElementIdentification')

# ################################################################################################################################
# ################################################################################################################################

class ContrlSegmentError(EDIGroup):
    """ One UCS loop of a CONTRL - a segment error with its element-level details.
    """
    _leader_tag = 'UCS'

    ucs            = EDISegmentAttr[UCS](UCS)
    element_errors = EDISegmentAttr[EDIRepeatableList](UCD, optional=True, repeatable=True)

# ################################################################################################################################

class ContrlMessageResponse(EDIGroup):
    """ One UCM loop of a CONTRL - the response to one message with any error detail.
    """
    _leader_tag = 'UCM'

    ucm            = EDISegmentAttr[UCM](UCM)
    segment_errors = EDIGroupAttr[EDIRepeatableList](ContrlSegmentError, optional=True)

# ################################################################################################################################

class Contrl(EDIMessage):
    """ The CONTRL syntax and service report message - one UCI for the interchange
    and one UCM loop per acknowledged message.
    """
    _message_type = 'CONTRL'

    unh               = EDISegmentAttr[UNH](UNH)
    uci               = EDISegmentAttr[UCI](UCI)
    message_responses = EDIGroupAttr[EDIRepeatableList](ContrlMessageResponse, optional=True)
    unt               = EDISegmentAttr[UNT](UNT)

# ################################################################################################################################
# ################################################################################################################################

class ContrlError:
    """ One segment or element error of a rejected message - what build_contrl takes in
    and what parse_contrl gives back.
    """

    def __init__(
        self,
        segment_position:'int',
        error_code:'str',
        element_position:'int' = 0,
        component_position:'int' = 0,
        ) -> 'None':
        self.segment_position = segment_position
        self.error_code = error_code
        self.element_position = element_position
        self.component_position = component_position

# ################################################################################################################################

class ContrlMessageResult:
    """ The parsed response to one message of an acknowledged interchange.
    """

    def __init__(self) -> 'None':
        self.message_reference:'str' = ''
        self.message_type:'str' = ''
        self.action_code:'str' = ''
        self.error_code:'str' = ''
        self.errors:'contrl_error_list' = []

# ################################################################################################################################

    @property
    def is_accepted(self) -> 'bool':
        out = self.action_code == Action_Acknowledged
        return out

# ################################################################################################################################

class ContrlResult:
    """ A parsed CONTRL - the interchange-level outcome with the per-message results.
    """

    def __init__(self) -> 'None':
        self.interchange_reference:'str' = ''
        self.action_code:'str' = ''
        self.message_results:'list[ContrlMessageResult]' = []

# ################################################################################################################################

    @property
    def is_accepted(self) -> 'bool':
        out = self.action_code == Action_Acknowledged
        return out

# ################################################################################################################################
# ################################################################################################################################

def build_contrl(interchange:'EDIInterchange', message_errors:'contrl_error_dict_none'=None) -> 'EDIInterchange':
    """ Builds a CONTRL acknowledgment for a parsed interchange. The optional errors map
    message reference numbers to their segment and element errors - a message with errors
    is rejected (action 4), everything else is acknowledged (action 7).
    """
    received_header = interchange.header
    if received_header is None:
        raise EDIEnvelopeError('Cannot build a CONTRL for an interchange without a UNB header')

    if message_errors is None:
        message_errors = {}

    now = datetime.now(timezone.utc)

    # Our response to produce
    out = EDIInterchange()
    out.separators = interchange.separators

    # The UNB addresses the acknowledgment back at the sender ..
    header = UNB()
    header.syntax = received_header.syntax
    header.sender = received_header.recipient
    header.recipient = received_header.sender

    prepared_at = DateTimeOfPreparation()
    prepared_at.date = now.strftime(UNB_Date_Format)
    prepared_at.time = now.strftime(UNB_Time_Format)
    header.prepared_at = prepared_at

    header.control_reference = Default_Control_Reference
    out.header = header

    # .. the CONTRL message itself starts with its UNH ..
    message = Contrl()

    identifier = MessageIdentifier()
    identifier.message_type = 'CONTRL'
    identifier.version = 'D'
    identifier.release = '3'
    identifier.controlling_agency = 'UN'

    unh = UNH()
    unh.reference_number = Default_Control_Reference
    unh.identifier = identifier
    message.unh = unh

    # .. the UCI echoes the acknowledged interchange's identity ..
    all_rejected = True

    for received_message in interchange.messages:
        reference = _element_value(received_message._raw_segments[0], 1)
        if reference not in message_errors:
            all_rejected = False
            break

    if interchange.messages:
        if all_rejected:
            interchange_action = Action_Rejected
        else:
            interchange_action = Action_Acknowledged
    else:
        interchange_action = Action_Acknowledged

    uci = UCI()
    uci.control_reference = received_header.control_reference
    uci.sender = received_header.sender
    uci.recipient = received_header.recipient
    uci.action_code = interchange_action
    message.uci = uci

    # .. one UCM answers for each received message ..
    responses:'anylist' = []

    for received_message in interchange.messages:

        unh_segment = received_message._raw_segments[0]
        reference = _element_value(unh_segment, 1)

        received_identifier = MessageIdentifier()
        received_identifier._raw_components = unh_segment.elements[1]

        errors = message_errors.get(reference)

        ucm = UCM()
        ucm.message_reference = reference
        ucm.identifier = received_identifier

        response = ContrlMessageResponse()

        if errors:
            ucm.action_code = Action_Rejected
            ucm.error_code = errors[0].error_code

            # Each error becomes a UCS with an optional UCD element detail
            error_groups:'anylist' = []

            for error in errors:
                ucs = UCS()
                ucs.segment_position = str(error.segment_position)
                ucs.error_code = error.error_code

                error_group = ContrlSegmentError()
                error_group.ucs = ucs

                if error.element_position:
                    position = DataElementIdentification()
                    position.element_position = str(error.element_position)

                    if error.component_position:
                        position.component_position = str(error.component_position)

                    ucd = UCD()
                    ucd.error_code = error.error_code
                    ucd.position = position

                    error_group.element_errors = EDIRepeatableList([ucd])

                error_groups.append(error_group)

            response.segment_errors = error_groups

        else:
            ucm.action_code = Action_Acknowledged

        response.ucm = ucm
        responses.append(response)

    message.message_responses = responses

    # .. the UNT counts every segment of the message, itself included ..
    body = message.serialize(out.separators)
    segment_count = body.count('\n') + 1 + 1

    unt = UNT()
    unt.segment_count = str(segment_count)
    unt.reference_number = Default_Control_Reference
    message.unt = unt

    out.messages.append(message)

    # .. and the UNZ concludes the interchange.
    trailer = UNZ()
    trailer.message_count = '1'
    trailer.control_reference = Default_Control_Reference
    out.trailer = trailer

    return out

# ################################################################################################################################

def parse_contrl(interchange:'EDIInterchange') -> 'ContrlResult':
    """ Parses the CONTRL of an interchange back into a result object.
    """
    message = None

    for candidate in interchange.messages:
        raw_unh = candidate._raw_segments[0]
        message_type = _element_value(raw_unh, 2)

        if message_type == 'CONTRL':
            message = candidate
            break

    if message is None:
        raise EDIEnvelopeError('No CONTRL message found in interchange')

    message = cast_('Contrl', message)

    # Our response to produce
    out = ContrlResult()

    uci = message.uci
    out.interchange_reference = uci.control_reference
    out.action_code = uci.action_code

    for response in message.message_responses:
        ucm = response.ucm

        message_result = ContrlMessageResult()
        message_result.message_reference = ucm.message_reference
        message_result.message_type = ucm.identifier.message_type
        message_result.action_code = ucm.action_code

        if ucm.error_code:
            message_result.error_code = ucm.error_code

        for error_group in response.segment_errors:
            ucs = error_group.ucs
            segment_position = int(ucs.segment_position)

            element_errors = error_group.element_errors

            # The element detail is preferred when present, otherwise the UCS stands alone
            if element_errors:
                for ucd in element_errors:
                    element_position = int(ucd.position.element_position)

                    component_position = 0
                    if ucd.position.component_position:
                        component_position = int(ucd.position.component_position)

                    error = ContrlError(segment_position, ucd.error_code, element_position, component_position)
                    message_result.errors.append(error)
            else:
                error = ContrlError(segment_position, ucs.error_code)
                message_result.errors.append(error)

        out.message_results.append(message_result)

    return out

# ################################################################################################################################
# ################################################################################################################################
