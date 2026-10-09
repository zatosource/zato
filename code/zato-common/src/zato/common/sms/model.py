# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The common model of SMS traffic - one event type for every provider's callbacks and poll results
# and one result type for every provider's send response.

# stdlib
from dataclasses import asdict, dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The kinds of event a channel's service receives
Kind_Message = 'message'
Kind_Status = 'status'

# The three delivery statuses every provider's vocabulary maps onto
Status_Sent = 'sent'
Status_Delivered = 'delivered'
Status_Failed = 'failed'

Kind_List = (Kind_Message, Kind_Status)
Status_List = (Status_Sent, Status_Delivered, Status_Failed)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SMSEvent:
    """ One event an SMS channel delivers to its service - an incoming text or a delivery report.
    """

    # Kind_Message for an incoming text, Kind_Status for a delivery report
    kind: 'str'

    # The provider's ID of the message the event is about
    id: 'str'

    # The telephone number or alphanumeric sender the message is from
    from_: 'str'

    # The telephone number the message is to
    to: 'str'

    # The text of an incoming message, empty for a delivery report
    body: 'str'

    # One of Status_List for a delivery report, empty for an incoming message
    status: 'str'

    # The provider's error code of a failed delivery, empty otherwise
    error_code: 'str'

    # When the provider recorded the event, as an ISO-8601 string
    received_at: 'str'

    # The provider's own payload, with its own status word intact
    raw: 'anydict'

    def to_dict(self) -> 'stranydict':
        out = asdict(self)
        return out

# ################################################################################################################################

    @staticmethod
    def from_dict(data:'stranydict') -> 'SMSEvent':
        out = SMSEvent()
        out.kind = data['kind']
        out.id = data['id']
        out.from_ = data['from_']
        out.to = data['to']
        out.body = data['body']
        out.status = data['status']
        out.error_code = data['error_code']
        out.received_at = data['received_at']
        out.raw = data['raw']
        return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SendResult:
    """ The result of a send request.
    """

    # The provider's ID of the message
    id: 'str'

    # One of Status_List, as the provider reported it at the time of the send
    status: 'str'

    # The provider's own response payload
    raw: 'anydict'

    def to_dict(self) -> 'stranydict':
        out = asdict(self)
        return out

# ################################################################################################################################
# ################################################################################################################################
