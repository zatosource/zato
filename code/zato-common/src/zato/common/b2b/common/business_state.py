# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime

# Zato
from zato.common.audit_log.common import B2BAttr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, dtnone, stranydict, strlist, strnone
    anylist = anylist
    dtnone = dtnone
    stranydict = stranydict
    strlist = strlist
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# The key of the data document of a sent event under which the business transaction is recorded.
Data_Business = 'business'

# ################################################################################################################################
# ################################################################################################################################

class BusinessState:
    """ Where the business transaction of one message sent stands - waiting for its signals and its response,
    receipted, refused at receipt or at acceptance, answered, past a deadline without what it waited for,
    or never delivered to the partner.
    """
    Sent               = 'sent'
    Receipted          = 'receipted'
    Receipt_Refused    = 'receipt-refused'
    Acceptance_Refused = 'acceptance-refused'
    Answered           = 'answered'
    Timed_Out          = 'timed-out'
    Delivery_Failed    = 'delivery-failed'

# The states each state can change to when a signal, a response or the end of the delivery of the message arrives.
_next_states = {
    BusinessState.Sent: {
        BusinessState.Receipted,
        BusinessState.Receipt_Refused,
        BusinessState.Acceptance_Refused,
        BusinessState.Answered,
        BusinessState.Delivery_Failed,
    },
    BusinessState.Receipted: {
        BusinessState.Acceptance_Refused,
        BusinessState.Answered,
    },
}

# The states after which nothing changes the transaction any more.
Final_States = (
    BusinessState.Receipt_Refused,
    BusinessState.Acceptance_Refused,
    BusinessState.Answered,
    BusinessState.Timed_Out,
    BusinessState.Delivery_Failed,
)

# ################################################################################################################################
# ################################################################################################################################

class BusinessData:
    """ The keys of the data documents the events of a business message have.
    """
    Conversation_ID   = 'conversation_id'
    Service           = 'service'
    Action            = 'action'
    Sent_At           = 'sent_at'
    Receipt_Deadline  = 'receipt_deadline'
    Response_Deadline = 'response_deadline'
    Reply_Message_ID  = 'reply_message_id'
    Errors            = 'errors'
    Failure_Cause     = 'failure_cause'
    Failure_Detail    = 'failure_detail'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BusinessMessage:
    """ One business message sent, with the deadlines of its business transaction and where the transaction stands.
    """
    message_id:      str
    cpa_id:          str
    conversation_id: str
    from_party:      str
    to_party:        str
    service:         str
    action:          str
    sent_at:         'datetime'

    # By when the receipt signal and the response are to arrive, None for a deadline that does not apply.
    receipt_deadline:  'dtnone' = None
    response_deadline: 'dtnone' = None

    state: str = BusinessState.Sent

    # The latest signal or response that changed the state, and the errors of an exception signal.
    reply_message_id: str = ''
    errors: 'strlist'

    # Why the last delivery of a message that was never delivered failed, and the status code or the error code of it.
    failure_cause:  str = ''
    failure_detail: str = ''

    def __init__(self) -> 'None':
        self.errors = []

# ################################################################################################################################

    @property
    def earliest_deadline(self) -> 'dtnone':
        """ The first deadline of the transaction, or None when no deadline applies to it.
        """
        deadlines:'anylist' = []

        for deadline in (self.receipt_deadline, self.response_deadline):
            if deadline:
                deadlines.append(deadline)

        if deadlines:
            out = min(deadlines)
        else:
            out = None

        return out

# ################################################################################################################################

    def is_past_deadline(self, now:'datetime') -> 'bool':
        """ Says whether a deadline of the transaction passed without what it waits for - the receipt signal
        while the message is not receipted, or the response while it is not answered.
        """

        # Our response to produce
        out = False

        # A transaction that ended has no deadline any more ..
        if self.state in Final_States:
            return out

        # .. the receipt is awaited only until the message is receipted ..
        if self.state == BusinessState.Sent:
            if receipt_deadline := self.receipt_deadline:
                if now > receipt_deadline:
                    out = True

        # .. and the response until the message is answered.
        if response_deadline := self.response_deadline:
            if now > response_deadline:
                out = True

        return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BusinessOutcome:
    """ What a signal, a response or a deadline did to the business transaction of one message sent.
    """
    message_id: str
    state:      str

    # The signal or the response that refers to the message, empty when a deadline passed.
    reply_message_id: str = ''

    # The error descriptions of an exception signal.
    errors: 'strlist'

    def __init__(self) -> 'None':
        self.errors = []

# ################################################################################################################################
# ################################################################################################################################

def can_change(current:'str', new:'str') -> 'bool':
    """ Says whether a transaction in the current state changes to the new one when a signal, a response
    or the end of the delivery of the message arrives.
    """
    if allowed := _next_states.get(current):
        out = new in allowed
    else:
        out = False

    return out

# ################################################################################################################################

def ends_transaction(state:'str', response_deadline:'dtnone') -> 'bool':
    """ Says whether a transaction in the given state has ended - the state is final, or the message is receipted
    and its transaction awaits no response.
    """
    if state in Final_States:
        out = True

    elif state == BusinessState.Receipted:
        out = response_deadline is None

    else:
        out = False

    return out

# ################################################################################################################################

def parse_time(value:'strnone') -> 'dtnone':
    if value:
        out = datetime.fromisoformat(value)
    else:
        out = None

    return out

# ################################################################################################################################

def format_time(value:'dtnone') -> 'strnone':
    if value:
        out = value.isoformat()
    else:
        out = None

    return out

# ################################################################################################################################

def business_data(message:'BusinessMessage') -> 'stranydict':
    """ Returns the document a business message is recorded with when it is sent.
    """
    out:'stranydict' = {
        BusinessData.Conversation_ID: message.conversation_id,
        BusinessData.Service: message.service,
        BusinessData.Action: message.action,
        BusinessData.Sent_At: message.sent_at.isoformat(),
        BusinessData.Receipt_Deadline: format_time(message.receipt_deadline),
        BusinessData.Response_Deadline: format_time(message.response_deadline),
    }

    return out

# ################################################################################################################################

def business_attrs(message:'BusinessMessage') -> 'stranydict':
    """ Returns the searchable attributes of every event of a business message.
    """
    out:'stranydict' = {
        B2BAttr.From_Party: message.from_party,
        B2BAttr.To_Party: message.to_party,
        B2BAttr.Service: message.service,
        B2BAttr.Action: message.action,
    }

    return out

# ################################################################################################################################

def business_sent_attrs(message:'BusinessMessage') -> 'stranydict':
    """ Returns the searchable attributes of the event that records a business message as sent.
    """
    out = business_attrs(message)

    if earliest_deadline := message.earliest_deadline:
        out[B2BAttr.Deadline_At] = earliest_deadline.isoformat()

    return out

# ################################################################################################################################

def new_business_outcome(message:'BusinessMessage') -> 'BusinessOutcome':
    """ Returns the outcome that says where the transaction of a message stands.
    """
    out = BusinessOutcome()
    out.message_id = message.message_id
    out.state = message.state
    out.reply_message_id = message.reply_message_id
    out.errors = message.errors

    return out

# ################################################################################################################################
# ################################################################################################################################
