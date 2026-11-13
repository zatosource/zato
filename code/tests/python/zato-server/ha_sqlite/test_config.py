# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A node without a referee type uses the lease as its referee. A node configured with a referee type that is not supported
# stops with an error and starts no Zato server.

# stdlib
import logging
import time

# Zato
from ha_env import build_environment, remove_environment
from nodes import Timers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment, HASession
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite.config')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The variable that selects the referee type
    Referee_Type_Variable = 'Zato_HA_Referee_Type'

    # The referee type that no node supports
    Unsupported_Referee_Type = 'dynamodb'

    # What the log of the node contains
    Error_Text = 'unsupported referee type'

    # How long the node may take to stop, in seconds
    Stop_Timeout = 30

    # How often the container is checked while the test waits for it to stop, in seconds
    Poll_Interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

def test_default_referee_type(ha_pair:'HAEnvironment') -> 'None':
    """ Nodes that do not set the referee type use the lease, which names the active node of the pair.
    """
    env = ha_pair

    for node in env.node_list:
        assert ModuleCtx.Referee_Type_Variable not in node.env, node.env

    active = env.get_active()
    assert active is not None, 'No active node'

    record = env.referee.read_record()
    assert record is not None, 'No referee record'
    assert record['active_node'] == active.node_name, record

# ################################################################################################################################

def test_unsupported_referee_type(ha_session:'HASession', request:'any_') -> 'None':
    """ The node stops with an error that names the referee type, and its server never starts.
    """
    env = build_environment(ha_session, request.node.name, Timers(), [])

    try:
        node = env.node_list[0]
        node.remove()

        node.env[ModuleCtx.Referee_Type_Variable] = ModuleCtx.Unsupported_Referee_Type
        node.start()

        deadline = time.monotonic() + ModuleCtx.Stop_Timeout

        while node.is_running():
            assert time.monotonic() < deadline, f'{node.node_name} still running'
            time.sleep(ModuleCtx.Poll_Interval)

        logs = node.read_logs()
        assert ModuleCtx.Error_Text in logs, logs
        assert not node.is_server_up()

    finally:
        remove_environment(env)

# ################################################################################################################################
# ################################################################################################################################
