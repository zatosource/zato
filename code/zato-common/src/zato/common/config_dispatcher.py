# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import date
from json import dumps, loads
from logging import getLogger
from traceback import format_exc

# Bunch
from zato.common.ext.bunch import bunchify

# Zato
from zato.common.broker_message import code_to_name
from zato.common.typing_ import any_, anydict, callable_, dataclass, strnone
from zato.common.util.config import resolve_env_variables
from zato.input_output import ServiceInput

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.base.parallel import ParallelServer
    from zato.server.base.config_manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ConfigEventResult:
    was_handled: 'bool' = False
    response: 'any_' = None
    action_code: 'strnone' = None
    action_name: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################

def _to_json_value(value:'any_') -> 'any_':
    """ Returns the JSON form of a value of a config event that JSON has no type for.
    """
    if isinstance(value, bytes):
        out = value.decode('utf8')
    elif isinstance(value, date):
        out = value.isoformat()
    elif isinstance(value, (set, frozenset, tuple)):
        out = list(value)

    # The input of a service is published as the event of its change by many admin services
    elif isinstance(value, ServiceInput):
        out = value.to_dict()

    else:
        out = str(value)

    return out

# ################################################################################################################################

def get_relay_body(msg:'anydict') -> 'anydict':
    """ Returns a config event as the JSON body that the arbiter relays to the other process, taken before the handler
    of this process runs, because a handler may add objects to the event that exist in this process only.
    """
    msg_json = dumps(msg, default=_to_json_value)
    out = loads(msg_json)
    return out

# ################################################################################################################################
# ################################################################################################################################

def handle_config_event(msg:'anydict', context:'any_') -> 'ConfigEventResult':
    """ Dispatches a config event to the appropriate handler on the context object.
    """
    action_code = msg['action']
    result = ConfigEventResult()
    result.action_code = action_code
    result.action_name = action_code

    try:
        handler_name = f'on_config_event_{action_code}'
        func = getattr(context, handler_name, None)

        if func:
            bunch_msg = bunchify(msg)
            response = func(bunch_msg)
            result.response = response
            result.was_handled = True
        else:
            logger.warning('No handler: %s in context: %s -> %s', handler_name, context, msg)

        return result

    except Exception:
        action = code_to_name[action_code]
        raise Exception(f'Could not handle config event: ({action}:{action_code}), e:`{format_exc()}`')

# ################################################################################################################################
# ################################################################################################################################

class ConfigDispatchReceiver:
    """ Mixin for objects that receive config events from the dispatcher.
    """
    config_dispatcher: 'ConfigDispatcher'
    config_manager: 'ConfigManager'

    def on_config_event(self, msg:'anydict') -> 'None':
        msg = resolve_env_variables(msg)
        if not self.filter(msg):
            return
        _ = handle_config_event(msg, self.config_manager)

    def filter(self, msg:'anydict') -> 'bool':
        return True

# ################################################################################################################################
# ################################################################################################################################

class ConfigDispatcher:

    def __init__(self, *, server:'ParallelServer', **kwargs:'any_') -> 'None':
        self.server = server

        # In a worker process, the function that sends an event to the arbiter, which relays it to every other worker
        self.relay:'callable_ | None' = None

    def publish(self, msg:'any_', *args:'any_', **kwargs:'any_') -> 'None':

        # A process that an arbiter started applies the event itself first and then sends it to the other process ..
        if self.relay:
            relay_body = get_relay_body(msg)
            _ = handle_config_event(msg, self.server.config_manager)
            self.relay(relay_body)

        # .. while a process with no arbiter only applies it.
        else:
            _ = handle_config_event(msg, self.server.config_manager)

    invoke_async = publish

    def relay_only(self, msg:'anydict') -> 'None':
        """ Sends an event to the other processes of the server without applying it in this one, which made the change
        that the event describes already. A process with no arbiter has no other process to send it to.
        """
        if self.relay:
            relay_body = get_relay_body(msg)
            self.relay(relay_body)

# ################################################################################################################################
# ################################################################################################################################
