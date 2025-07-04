# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.broker_message import code_to_name, SERVICE

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, callnone, dataclass, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

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
    action_name: 'str' = 'undefined_action'

# ################################################################################################################################
# ################################################################################################################################

class BrokerMessageHandler:
    """ Handles broker messages with configurable preprocessing and filtering.
    """
    @staticmethod
    def handle_message(
        msg: 'anydict',
        context: 'any_'=None,
        preprocess_func: 'callnone'=None,
        filter_func: 'callnone'=None) -> 'BrokerMessageResult':

        # Initialize the result object
        result = BrokerMessageResult()

        if not context:
            return result

        try:
            # Apply pre-processing if available
            if preprocess_func:
                msg = preprocess_func(msg)

            # Apply filtering if available
            if filter_func and not filter_func(msg):
                logger.info('Rejecting broker message `%r`', msg)
                return result

            # Extract action code from message
            action_code = msg.get('action')
            if not action_code:
                logger.info('No action code in message: `%r`', msg)
                return result

            # Look up action name from code
            action_name = code_to_name.get(action_code) or 'undefined_action'
            result.action_code = action_code
            result.action_name = action_name

            # Build handler name and look it up in context
            handler_name = f'on_broker_msg_{action_name}'

            # Check if context has the handler method
            if not hasattr(context, handler_name):
                logger.info('No handler `%s` for message: `%r`', handler_name, msg)
                return result

            # Get handler function
            handler_func = getattr(context, handler_name)

            # Execute the handler
            result.response = handler_func(msg)
            result.was_handled = True

            # Return the result object
            return result

        except Exception:
            msg_action = msg.get('action') or 'undefined_msg_action'
            action_name = code_to_name.get(msg_action) or 'undefined_action'
            logger.error('Could not handle broker message: (%s:%s) `%r`, e:`%s`', action_name, msg_action, msg, format_exc())
            return result

# ################################################################################################################################
# ################################################################################################################################
