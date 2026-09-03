# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc
from typing import NamedTuple

# Zato
from zato.common.hl7.exception import HL7ApplicationError
from zato.common.hl7.mllp.ack import build_ack, Condition_Application_Error, ErrorCondition

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.hl7.mllp.router import ChannelRoute
    from zato.common.typing_ import any_

    ChannelRoute = ChannelRoute
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# AA - the message was accepted
Accepted_Ack_Code = 'AA'

# AR - the connection is refused before any message was read
Rejection_Ack_Code = 'AR'

# AR - the service failed
Transient_Failure_Ack_Code = 'AR'

# AE - the message content cannot be processed
Application_Error_Ack_Code = 'AE'

# What the sender reads in MSA-3 when the service failed and the channel does not spell the reason out
Internal_Error_Text = 'Internal processing error'

# Where MSH-9, the message type, sits when the header is split on the field separator -
# a header with nothing there cannot be identified as any message at all
MSH9_Field_Index = 8

# What a channel's own answer has to begin with to be sent back in place of a locally built
# acknowledgment. A channel that replies from one of its destinations answers with the
# acknowledgment that destination gave it, and everything else is not an answer at all.
Reply_Segment_Prefix = 'MSH'

# What a message that matched no channel is filed under in the audit log - there is no channel
# whose name it could carry, yet a turned-away message is still worth finding afterwards
Unmatched_Object_Name = 'unmatched'

# ################################################################################################################################
# ################################################################################################################################

class CallbackOutcome(NamedTuple):
    """ What one service callback invocation came to - the channel's own answer if any,
    and the acknowledgment that describes the outcome to the sender.
    """
    callback_response:'any_'
    ack_code:'str'
    error_text:'str'
    error_condition:'ErrorCondition | None'

# ################################################################################################################################
# ################################################################################################################################

def resolve_reply(
    callback_response:'any_',
    msh_line:'str',
    ack_code:'str',
    error_text:'str',
    error_condition:'ErrorCondition | None' = None,
    ) -> 'str':
    """ Returns what the sender is answered with - the message the channel itself produced when it
    produced one, and otherwise an acknowledgment built here from the outcome of the delivery.
    """
    if isinstance(callback_response, str):
        if callback_response.startswith(Reply_Segment_Prefix):
            return callback_response

    out = build_ack(msh_line, ack_code, error_text=error_text, error_condition=error_condition)
    return out

# ################################################################################################################################

def invoke_callback(route:'ChannelRoute', data:'any_', cid:'str', endpoint:'str', what:'str') -> 'CallbackOutcome':
    """ Runs a matched route's service callback and turns what happened into an acknowledgment outcome.
    """

    # The callback ran and whatever it returned is the channel's own answer ..
    try:
        callback_response = route.callback(data, cid)
        out = CallbackOutcome(callback_response, Accepted_Ack_Code, '', None)

    # .. the service says the message itself cannot be processed ..
    except HL7ApplicationError as e:
        logger.warning('Application error for %s on channel `%s` from %s; e:`%s`',
            what, route.channel_name, endpoint, e)

        error_text = str(e)
        out = CallbackOutcome(None, Application_Error_Ack_Code, error_text, Condition_Application_Error)

    # .. and anything else is the service failing.
    except Exception:
        error_details = format_exc()
        logger.warning('Service callback error for %s on channel `%s` from %s; e:`%s`',
            what, route.channel_name, endpoint, error_details)

        out = CallbackOutcome(None, Transient_Failure_Ack_Code, Internal_Error_Text, Condition_Application_Error)

    return out

# ################################################################################################################################
# ################################################################################################################################
