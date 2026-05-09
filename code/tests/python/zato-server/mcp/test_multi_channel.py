# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# Zato
from zato.common.api import GENERIC as COMMON_GENERIC
from zato.server.service.internal.generic import connection as conn_module
from zato.common.util.channel import on_mcp_channel_create_edit, on_mcp_channel_delete

# ################################################################################################################################
# ################################################################################################################################

class HookRegistration(TestCase):
    """ Tests that the MCP create/edit hook is registered.
    """

# ################################################################################################################################

    def test_hook_registered_for_channel_mcp(self):

        # The hook dict must contain our type ..
        hook = conn_module.hook
        mcp_type = COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_MCP

        # .. and it must point to the correct function.
        self.assertIn(mcp_type, hook)
        self.assertIs(hook[mcp_type], on_mcp_channel_create_edit)

# ################################################################################################################################

    def test_instance_hook_exists(self):

        # The module must define instance_hook for delete support.
        self.assertTrue(hasattr(conn_module, 'instance_hook'))
        self.assertTrue(callable(conn_module.instance_hook))

# ################################################################################################################################
# ################################################################################################################################

class InstanceHookDispatch(TestCase):
    """ Tests that instance_hook only calls on_mcp_channel_delete for MCP types.
    """

# ################################################################################################################################

    def test_instance_hook_skips_non_mcp(self):

        # Track whether on_mcp_channel_delete was called ..
        calls = []
        original = conn_module.on_mcp_channel_delete

        def _mock_delete(session, channel_name, cluster_id):
            calls.append((session, channel_name, cluster_id))

        conn_module.on_mcp_channel_delete = _mock_delete

        class _MockInstance:
            type_ = 'channel-kafka'
            name = 'test'
            cluster_id = 1

        class _MockAttrs:
            _meta_session = None

        try:
            conn_module.instance_hook(None, {}, _MockInstance(), _MockAttrs())
        finally:
            conn_module.on_mcp_channel_delete = original

        # .. must not have been called for non-MCP types.
        self.assertEqual(len(calls), 0)

# ################################################################################################################################

    def test_instance_hook_calls_delete_for_mcp(self):

        # Track whether on_mcp_channel_delete was called ..
        calls = []

        class _MockInstance:
            type_ = COMMON_GENERIC.CONNECTION.TYPE.CHANNEL_MCP
            name = 'my-mcp'
            cluster_id = 1

        class _MockAttrs:
            _meta_session = 'fake-session'

        # .. patch the delete function temporarily ..
        original = conn_module.on_mcp_channel_delete

        def _mock_delete(session, channel_name, cluster_id):
            calls.append((session, channel_name, cluster_id))

        conn_module.on_mcp_channel_delete = _mock_delete

        try:
            conn_module.instance_hook(None, {}, _MockInstance(), _MockAttrs())
        finally:
            conn_module.on_mcp_channel_delete = original

        # .. verify the call was made with the correct arguments.
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0], ('fake-session', 'my-mcp', 1))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
