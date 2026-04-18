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

# zato-broker-core (Rust extension)
from zato_broker_core import log_admin_info, log_admin_error

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
        action_code = msg.get('action')
        if not action_code:
            return result

        result.action_code = action_code
        result.action_name = action_code

        handler_name = f'on_broker_msg_{action_code}'

        log_admin_info(f'Broker msg received -> action:{action_code}, msg:{msg}')

        if func := getattr(context, handler_name, None):
            msg = bunchify(msg)
            response = func(msg)

            result.response = response
            result.was_handled = True

            log_admin_info(f'Broker msg handled -> action:{action_code}, handler:{handler_name}')
        else:
            logger.debug('No handler %s on %s', handler_name, context.__class__.__name__)

        return result

    except Exception:
        msg_action = msg.get('action') or 'undefined_msg_action'
        action = code_to_name.get(msg_action) or 'undefined_action'
        log_admin_error(f'Broker msg error -> action:{msg_action} ({action}), e:{format_exc()}')
        msg = f'Could not handle broker message: ({action}:{msg_action}) `repr({msg})`, e:`{format_exc()}`' # type: ignore
        raise Exception(msg)

# ################################################################################################################################
# ################################################################################################################################
