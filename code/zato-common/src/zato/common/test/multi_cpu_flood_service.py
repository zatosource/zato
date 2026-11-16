# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The services through which the configuration suite of a server with several workers sends a flood of configuration
# events and observes the order in which each worker applies them.

# stdlib
import os
from time import monotonic

# gevent
from gevent import sleep

# Zato
from zato.common.broker_message import Server as BrokerMessageServer
from zato.common.worker_slot import get_slot_or_single
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The value that stands for a variable that no event has set yet
    Unset_Value = -1

    # How often the watch reads the variable, in seconds
    Watch_Interval = 0.001

# ################################################################################################################################
# ################################################################################################################################

class EventFlood(Service):
    """ Runs in the config process and relays one event per sequence number to every worker, each of which sets
    the variable of the request to that number.
    """
    name = 'test.multi-cpu.event-flood'

    changes_config = True

    def handle(self) -> 'None':
        request = self.request.payload
        variable = request['name']

        for seq in range(request['count']):
            self.config_dispatcher.relay_only({
                'action': BrokerMessageServer.Env_Variables_Apply.value,
                'set_variables': {variable: str(seq)},
                'deleted_variables': [],
            })

        self.response.payload = {
            'count': request['count'],
        }

# ################################################################################################################################
# ################################################################################################################################

class EventWatch(Service):
    """ Reads the variable of the request in the worker that serves the request until it holds the expected value
    or the timeout ends, and returns whether its values only increased, which they do if the worker applied
    the events in order.
    """
    name = 'test.multi-cpu.event-watch'

    def handle(self) -> 'None':
        request = self.request.payload
        variable = request['name']
        expected = request['expected']
        deadline = monotonic() + request['timeout']

        values:'intlist' = []
        is_in_order = True
        previous = ModuleCtx.Unset_Value

        while monotonic() < deadline:

            if variable in os.environ:
                current = int(os.environ[variable])
            else:
                current = ModuleCtx.Unset_Value

            if current < previous:
                is_in_order = False

            if current != previous:
                values.append(current)

            previous = current

            if current == expected:
                break

            sleep(ModuleCtx.Watch_Interval)

        self.response.payload = {
            'slot': get_slot_or_single(),
            'is_in_order': is_in_order,
            'last_value': previous,
            'distinct_value_count': len(values),
        }

# ################################################################################################################################
# ################################################################################################################################
