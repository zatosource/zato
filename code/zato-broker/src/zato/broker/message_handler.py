# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.broker_message import code_to_name
from zato.common.typing_ import any_, anydict, dataclass, strnone

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class BrokerMessageResult:
    """ Class representing the result of broker message handling.
    """
    # Was the message successfully handled
    was_handled: 'bool' = False

    # Response from the handler if any
    response: 'any_' = None

    # Action code from the message
    action_code: 'strnone' = None

    # Action name derived from code
    action_name: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

def handle_broker_msg(msg:'anydict', context:'any_') -> 'BrokerMessageResult':
    """ Shared message handler. Extracts action from message, finds the corresponding method on context, and invokes it if found.
    """
    result = BrokerMessageResult()

    try:
        # Extract action information
        action_code = msg.get('action')
        if not action_code:
            return result

        # Store action info in result
        result.action_code = action_code
        action = code_to_name.get(action_code, '')
        result.action_name = action

        # Find and call the handler method
        handler = f'on_broker_msg_{action}'
        if hasattr(context, handler):
            func = getattr(context, handler)
            result.response = func(msg)
            result.was_handled = True

        return result

    except Exception:
        msg_action = msg.get('action') or 'undefined_msg_action'
        action = code_to_name.get(msg_action) or 'undefined_action'
        logger.error('Could not handle broker message: (%s:%s) `%r`, e:`%s`', action, msg_action, msg, format_exc())
        return result

# ################################################################################################################################
# ################################################################################################################################
