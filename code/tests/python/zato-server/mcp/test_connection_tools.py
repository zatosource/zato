# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.server.connection.mcp.connection_tools.api import build_tool_name, group_registry
from zato.server.connection.mcp.registry import ToolRegistry

# Zato - test helpers
from connection_stubs import make_rest_item, StubConfigManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class _MockServiceStore:
    """ Minimal mock of ServiceStore with name_to_impl_name and services dicts.
    """
    def __init__(self) -> 'None':
        self.name_to_impl_name:'anydict' = {}
        self.services:'anydict' = {}

    def add_service(self, name:'str', service_class:'type') -> 'None':
        """ Helper to register a mock service.
        """

        impl_name = f'impl.{name}'

        self.name_to_impl_name[name] = impl_name
        self.services[impl_name] = {
            'name': name,
            'service_class': service_class,
            'is_active': True,
        }

# ################################################################################################################################
# ################################################################################################################################

class _ServiceWithDoc:
    """ Returns customer details by ID.
    """

# ################################################################################################################################
# ################################################################################################################################

class ToolNameBuild(TestCase):
    """ Tests for how connection tool names are built.
    """

# ################################################################################################################################

    def test_plain_name(self) -> 'None':
        """ Verifies that a plain connection name is prefixed with the group.
        """

        out = build_tool_name('rest', 'billing')
        self.assertEqual(out, 'rest.billing')

# ################################################################################################################################

    def test_name_is_made_fs_safe(self) -> 'None':
        """ Verifies that punctuation and whitespace turn into underscores,
        the same transformation attribute-style facade lookups apply.
        """

        out = build_tool_name('rest', 'My CRM (Live)')
        self.assertEqual(out, 'rest.My_CRM__Live_')

# ################################################################################################################################
# ################################################################################################################################

class GroupRegistryShape(TestCase):
    """ Tests for the shape of the group registration table.
    """

# ################################################################################################################################

    def test_every_group_is_complete(self) -> 'None':
        """ Verifies that each registered group carries all its parts
        and is keyed by its own group name.
        """

        self.assertGreater(len(group_registry), 0)

        for group, definition in group_registry.items():

            self.assertEqual(definition.group, group)
            self.assertTrue(definition.config_key)
            self.assertTrue(definition.tool_prefix)
            self.assertTrue(callable(definition.get_config_dict))
            self.assertTrue(callable(definition.build_description))
            self.assertTrue(callable(definition.invoke))
            self.assertEqual(definition.input_schema['type'], 'object')

# ################################################################################################################################

    def test_config_keys_are_unique(self) -> 'None':
        """ Verifies that no two groups share a config key or a tool prefix.
        """

        config_keys = []
        tool_prefixes = []

        for definition in group_registry.values():
            config_keys.append(definition.config_key)
            tool_prefixes.append(definition.tool_prefix)

        self.assertEqual(len(config_keys), len(set(config_keys)))
        self.assertEqual(len(tool_prefixes), len(set(tool_prefixes)))

# ################################################################################################################################
# ################################################################################################################################

class ConnectionToolRegistryBuild(TestCase):
    """ Tests for building connection tools next to service tools.
    """

# ################################################################################################################################

    def test_connection_tool_built(self) -> 'None':
        """ Verifies that an allow-listed connection becomes one tool
        with the group's schema and a target the registry records.
        """

        store = _MockServiceStore()

        config_manager = StubConfigManager()
        config_manager.config_store.out_plain_http['billing'] = make_rest_item('https://example.com', '/api')

        registry = ToolRegistry(store, [], {'rest': ['billing']}, config_manager) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        tools = registry.get_tools()
        self.assertEqual(len(tools), 1)

        tool = tools[0]
        self.assertEqual(tool['name'], 'rest.billing')
        self.assertIn('billing', tool['description'])
        self.assertIn('https://example.com/api', tool['description'])
        self.assertEqual(tool['inputSchema'], group_registry['rest'].input_schema)

        self.assertEqual(registry.tool_targets['rest.billing'], ('rest', 'billing'))

# ################################################################################################################################

    def test_missing_connection_raises(self) -> 'None':
        """ Verifies that an allow-listed connection that does not exist
        makes rebuild raise, mirroring the missing-service path.
        """

        store = _MockServiceStore()
        config_manager = StubConfigManager()

        registry = ToolRegistry(store, [], {'rest': ['nonexistent']}, config_manager) # pyright: ignore[reportArgumentType]

        with self.assertRaises(Exception):
            registry.rebuild()

# ################################################################################################################################

    def test_services_and_connections_sorted_together(self) -> 'None':
        """ Verifies that service tools and connection tools come out
        as one list sorted by name.
        """

        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        config_manager = StubConfigManager()
        config_manager.config_store.out_plain_http['billing'] = make_rest_item('https://example.com', '/api')

        registry = ToolRegistry(store, ['crm.get-customer'], {'rest': ['billing']}, config_manager) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        names = []

        for tool in registry.get_tools():
            names.append(tool['name'])

        self.assertEqual(names, sorted(names))
        self.assertIn('crm.get-customer', names)
        self.assertIn('rest.billing', names)

# ################################################################################################################################

    def test_empty_allow_lists_add_nothing(self) -> 'None':
        """ Verifies that groups with empty allow lists produce no tools.
        """

        store = _MockServiceStore()
        config_manager = StubConfigManager()

        registry = ToolRegistry(store, [], {'rest': [], 'sql': []}, config_manager) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        self.assertEqual(len(registry.get_tools()), 0)
        self.assertEqual(len(registry.tool_targets), 0)

# ################################################################################################################################

    def test_schema_lookup_serves_connection_tools(self) -> 'None':
        """ Verifies that get_tool_schema returns the group's schema
        for a connection tool name.
        """

        store = _MockServiceStore()

        config_manager = StubConfigManager()
        config_manager.config_store.out_plain_http['billing'] = make_rest_item('https://example.com', '/api')

        registry = ToolRegistry(store, [], {'rest': ['billing']}, config_manager) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        out = registry.get_tool_schema('rest.billing')
        self.assertEqual(out, group_registry['rest'].input_schema)

# ################################################################################################################################
# ################################################################################################################################

class ConnectionToolAllowCheck(TestCase):
    """ Tests for is_tool_allowed with connection tools in play.
    """

# ################################################################################################################################

    def test_connection_tool_allowed(self) -> 'None':
        """ Verifies that a connection tool the last rebuild recorded passes the check.
        """

        store = _MockServiceStore()

        config_manager = StubConfigManager()
        config_manager.config_store.out_plain_http['billing'] = make_rest_item('https://example.com', '/api')

        registry = ToolRegistry(store, [], {'rest': ['billing']}, config_manager) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        self.assertTrue(registry.is_tool_allowed('rest.billing'))

# ################################################################################################################################

    def test_unknown_connection_tool_disallowed(self) -> 'None':
        """ Verifies that a connection tool name the registry never built fails the check.
        """

        store = _MockServiceStore()

        config_manager = StubConfigManager()
        config_manager.config_store.out_plain_http['billing'] = make_rest_item('https://example.com', '/api')

        registry = ToolRegistry(store, [], {'rest': ['billing']}, config_manager) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        self.assertFalse(registry.is_tool_allowed('rest.other'))

# ################################################################################################################################
# ################################################################################################################################
