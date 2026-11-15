# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.server.connection.mcp.session import MCPSessionManager, remove_all_sessions

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Identity = 'test.identity'
    Protocol_Version = '2025-06-18'

# ################################################################################################################################
# ################################################################################################################################

def test_the_sessions_of_every_gateway_are_removed_at_startup() -> 'None':

    orders_manager = MCPSessionManager('test.mcp.orders')
    billing_manager = MCPSessionManager('test.mcp.billing')

    # Each gateway has sessions of its own ..
    _ = orders_manager.create(ModuleCtx.Protocol_Version, ModuleCtx.Identity)
    _ = billing_manager.create(ModuleCtx.Protocol_Version, ModuleCtx.Identity)
    _ = billing_manager.create(ModuleCtx.Protocol_Version, ModuleCtx.Identity)

    assert orders_manager.session_count == 1
    assert billing_manager.session_count == 2

    # .. and none remains after a server start removed them.
    engine = get_pubsub_engine()
    remove_all_sessions(engine)

    assert orders_manager.session_count == 0
    assert billing_manager.session_count == 0

# ################################################################################################################################
# ################################################################################################################################
