# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Bunch
from bunch import bunchify

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

logger = getLogger(__name__)

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
        handler_name = f'on_broker_msg_{action}'
        if func := getattr(context, handler_name, None):
            msg = bunchify(msg)
            response = func(msg)
            result.response = response
            result.was_handled = True
        else:
            logger.warning('No such handler: %s in context: %s', handler_name, context)

        return result

    except Exception:
        msg_action = msg.get('action') or 'undefined_msg_action'
        action = code_to_name.get(msg_action) or 'undefined_action'
        msg = f'Could not handle broker message: ({action}:{msg_action}) `repr({msg})`, e:`{format_exc()}`'
        raise Exception(msg)

# ################################################################################################################################
# ################################################################################################################################
