# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A node configured with a referee type that is not supported stops with an error and starts no Zato server.

# stdlib
import logging
import time

# Zato
from ha_env import build_environment, remove_environment
from nodes import Timers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HASession
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul.config')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

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

def test_unsupported_referee_type(ha_session:'HASession', request:'any_') -> 'None':
    """ The node stops with an error that names the referee type, and its server never starts.
    """
    env = build_environment(ha_session, request.node.name, Timers(), [])

    try:
        node = env.node_list[0]
        node.remove()

        node.env['Zato_HA_Referee_Type'] = ModuleCtx.Unsupported_Referee_Type
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
