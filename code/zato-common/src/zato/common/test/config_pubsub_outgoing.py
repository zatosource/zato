# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.test.conftest_base_pubsub import find_free_port, start_server_process

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato.test.pubsub_outgoing')

# ################################################################################################################################
# ################################################################################################################################

class TestConfig:
    """ What the tests of publishing to outgoing connections need to know about the environment
    the session fixture built for them.
    """

    base_url = ''
    password = ''

    server_directory = ''
    server_port = 0
    zato_bin = ''

    # The connections published to, by the names the enmasse file gives them
    orders_connection = 'test.outgoing.orders'
    inventory_connection = 'test.outgoing.inventory'

    # The credentials the inventory connection authenticates with
    connection_username = ''
    connection_password = ''

    # The targets of those two connections
    orders_receiver: 'any_' = None
    inventory_receiver: 'any_' = None

    # The session state, which is what a restart goes through
    state: 'any_' = None

# ################################################################################################################################
# ################################################################################################################################

def restart_server() -> 'None':
    """ Stops the server and starts it again on the same port, the way a restart in production does.
    """
    state = TestConfig.state
    state.kill_server()

    # The broker the new process runs listens on a port of its own ..
    broker_port = find_free_port()

    # .. and the server itself comes back on the port everything already knows.
    _ = start_server_process(
        state=state,
        logger=logger,
        zato_bin=TestConfig.zato_bin,
        server_directory=TestConfig.server_directory,
        server_port=TestConfig.server_port,
        broker_port=broker_port,
        extra_server_env={},
        patch_server_conf_bind=False,
    )

# ################################################################################################################################
# ################################################################################################################################
