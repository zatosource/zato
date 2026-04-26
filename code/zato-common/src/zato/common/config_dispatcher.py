# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

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
from zato.common.util.config import resolve_env_variables

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.server.base.parallel import ParallelServer
    from zato.server.base.worker import WorkerStore

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

def handle_config_event(msg:'anydict', context:'any_') -> 'ConfigEventResult':
    """ Dispatches a config event to the appropriate handler on the context object.
    """
    action_code = msg['action']
    result = ConfigEventResult()
    result.action_code = action_code
    result.action_name = action_code

    try:
        handler_name = f'on_config_event_{action_code}'
        if func := getattr(context, handler_name, None):
            msg = bunchify(msg)
            response = func(msg)
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
    worker_store: 'WorkerStore'

    def on_config_event(self, msg:'anydict') -> 'None':
        msg = resolve_env_variables(msg)
        if not self.filter(msg):
            return
        handle_config_event(msg, self.worker_store)

    def filter(self, msg:'anydict') -> 'bool':
        return True

# ################################################################################################################################
# ################################################################################################################################

class ConfigDispatcher:

    def __init__(self, *, server:'ParallelServer | None'=None, **kwargs:'any_') -> 'None':
        self.server = server

    def publish(self, msg:'any_', *args:'any_', **kwargs:'any_') -> 'None':
        handle_config_event(msg, self.server.worker_store)

    invoke_async = publish

# ################################################################################################################################
# ################################################################################################################################
