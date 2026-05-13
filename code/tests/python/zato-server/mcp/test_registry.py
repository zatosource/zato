# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# Zato
from zato.server.connection.mcp.registry import ToolRegistry, _default_page_size

# ################################################################################################################################
# ################################################################################################################################

class _MockServiceStore:
    """ Minimal mock of ServiceStore with name_to_impl_name and services dicts.
    """
    def __init__(self) -> 'None':
        self.name_to_impl_name:'dict' = {}
        self.services:'dict' = {}

    def add_service(self, name:'str', service_class:'type', impl_name:'str | None'=None) -> 'None':
        """ Helper to register a mock service.
        """
        if impl_name is None:
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

class _ServiceNoDoc:
    pass

# ################################################################################################################################
# ################################################################################################################################

class ToolRegistryBuild(TestCase):
    """ Tests for building the tools list from the service store.
    """

# ################################################################################################################################

    def test_single_service(self):
        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]
        registry.rebuild()
        tools = registry.get_tools()

        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]['name'], 'crm.get-customer')
        self.assertEqual(tools[0]['description'], 'Returns customer details by ID.')
        self.assertEqual(tools[0]['inputSchema'], {'type': 'object'})

# ################################################################################################################################

    def test_multiple_services(self):
        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)
        store.add_service('billing.create-invoice', _ServiceNoDoc)

        registry = ToolRegistry(store, ['crm.get-customer', 'billing.create-invoice']) # pyright: ignore[reportArgumentType]
        registry.rebuild()
        tools = registry.get_tools()

        self.assertEqual(len(tools), 2)

        names = []

        for tool in tools:
            names.append(tool['name'])

        self.assertIn('crm.get-customer', names)
        self.assertIn('billing.create-invoice', names)

# ################################################################################################################################

    def test_service_without_docstring(self):
        store = _MockServiceStore()
        store.add_service('my.service', _ServiceNoDoc)

        registry = ToolRegistry(store, ['my.service']) # pyright: ignore[reportArgumentType]
        registry.rebuild()
        tools = registry.get_tools()

        self.assertEqual(tools[0]['description'], '')

# ################################################################################################################################

    def test_internal_service_excluded(self):
        store = _MockServiceStore()
        store.add_service('zato.server.info', _ServiceWithDoc)
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['zato.server.info', 'crm.get-customer']) # pyright: ignore[reportArgumentType]
        registry.rebuild()
        tools = registry.get_tools()

        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]['name'], 'crm.get-customer')

# ################################################################################################################################

    def test_unknown_service_skipped(self):
        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer', 'nonexistent.service']) # pyright: ignore[reportArgumentType]
        registry.rebuild()
        tools = registry.get_tools()

        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]['name'], 'crm.get-customer')

# ################################################################################################################################

    def test_empty_allowlist(self):
        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, []) # pyright: ignore[reportArgumentType]
        registry.rebuild()
        tools = registry.get_tools()

        self.assertEqual(len(tools), 0)

# ################################################################################################################################

    def test_only_internal_services_in_allowlist(self):
        store = _MockServiceStore()
        store.add_service('zato.ping', _ServiceWithDoc)
        store.add_service('zato.server.info', _ServiceWithDoc)

        registry = ToolRegistry(store, ['zato.ping', 'zato.server.info']) # pyright: ignore[reportArgumentType]
        registry.rebuild()
        tools = registry.get_tools()

        self.assertEqual(len(tools), 0)

# ################################################################################################################################
# ################################################################################################################################

class ToolRegistryCache(TestCase):
    """ Tests for caching and rebuilding the tools list.
    """

# ################################################################################################################################

    def test_not_built_until_rebuild_called(self): # type: ignore

        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]

        # Not built until rebuild() is called explicitly
        self.assertEqual(len(registry._cached_tools), 0)

        registry.rebuild()
        self.assertEqual(len(registry._cached_tools), 1)

# ################################################################################################################################

    def test_cached_result_returned(self):
        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        tools_1 = registry.get_tools()
        tools_2 = registry.get_tools()

        # Same list object returned from cache
        self.assertIs(tools_1, tools_2)

# ################################################################################################################################

    def test_rebuild_updates_cache(self):
        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]
        registry.rebuild()
        tools_before = registry.get_tools()

        self.assertEqual(len(tools_before), 1)

        # Add a new service to the store and allowlist
        store.add_service('billing.create-invoice', _ServiceNoDoc)
        registry.allowed_services = ['crm.get-customer', 'billing.create-invoice']
        registry.rebuild()

        tools_after = registry.get_tools()

        self.assertEqual(len(tools_after), 2)

# ################################################################################################################################

    def test_rebuild_after_service_removed_from_store(self):
        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)
        store.add_service('billing.create-invoice', _ServiceNoDoc)

        registry = ToolRegistry(store, ['crm.get-customer', 'billing.create-invoice']) # pyright: ignore[reportArgumentType]
        registry.rebuild()
        tools_before = registry.get_tools()

        self.assertEqual(len(tools_before), 2)

        # Remove a service from the store (simulating undeployment)
        impl_name = store.name_to_impl_name.pop('billing.create-invoice')
        del store.services[impl_name]

        registry.rebuild()
        tools_after = registry.get_tools()

        self.assertEqual(len(tools_after), 1)
        self.assertEqual(tools_after[0]['name'], 'crm.get-customer')

# ################################################################################################################################
# ################################################################################################################################

class ToolRegistryPagination(TestCase):
    """ Tests for cursor-based pagination in get_tools_page.
    """

# ################################################################################################################################

    def test_no_cursor_returns_all_when_under_page_size(self):
        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)
        store.add_service('billing.create-invoice', _ServiceNoDoc)

        registry = ToolRegistry(store, ['crm.get-customer', 'billing.create-invoice']) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        tools, next_cursor = registry.get_tools_page()

        self.assertEqual(len(tools), 2)
        self.assertIsNone(next_cursor)

# ################################################################################################################################

    def test_no_cursor_with_empty_registry(self):
        store = _MockServiceStore()

        registry = ToolRegistry(store, []) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        tools, next_cursor = registry.get_tools_page()

        self.assertEqual(len(tools), 0)
        self.assertIsNone(next_cursor)

# ################################################################################################################################

    def test_cursor_zero_same_as_no_cursor(self):
        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        tools_no_cursor, _ = registry.get_tools_page()
        tools_cursor_zero, _ = registry.get_tools_page('0')

        self.assertEqual(tools_no_cursor, tools_cursor_zero)

# ################################################################################################################################

    def test_pagination_splits_tools(self):
        store = _MockServiceStore()

        # Create more services than the default page size
        total_services = _default_page_size + 5

        service_names = []

        for i in range(total_services):
            name = f'svc.service-{i:04d}'
            store.add_service(name, _ServiceWithDoc)
            service_names.append(name)

        registry = ToolRegistry(store, service_names) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        # First page
        tools_page1, next_cursor = registry.get_tools_page()

        self.assertEqual(len(tools_page1), _default_page_size)
        self.assertIsNotNone(next_cursor)
        self.assertEqual(next_cursor, str(_default_page_size))

        # Second page
        tools_page2, next_cursor2 = registry.get_tools_page(next_cursor)

        self.assertEqual(len(tools_page2), 5)
        self.assertIsNone(next_cursor2)

# ################################################################################################################################

    def test_cursor_beyond_end_returns_empty(self):
        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        tools, next_cursor = registry.get_tools_page('999')

        self.assertEqual(len(tools), 0)
        self.assertIsNone(next_cursor)

# ################################################################################################################################

    def test_all_tools_reachable_via_pagination(self):
        store = _MockServiceStore()

        total_services = _default_page_size * 3 + 7

        service_names = []

        for i in range(total_services):
            name = f'svc.service-{i:04d}'
            store.add_service(name, _ServiceWithDoc)
            service_names.append(name)

        registry = ToolRegistry(store, service_names) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        # Walk through all pages
        all_collected = []
        cursor = None

        while True:
            tools, cursor = registry.get_tools_page(cursor)
            all_collected.extend(tools)

            if cursor is None:
                break

        self.assertEqual(len(all_collected), total_services)

# ################################################################################################################################
# ################################################################################################################################

class ToolRegistryAllowlistCheck(TestCase):
    """ Tests for is_tool_allowed.
    """

# ################################################################################################################################

    def test_allowed_service(self):
        store = _MockServiceStore()
        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]

        self.assertTrue(registry.is_tool_allowed('crm.get-customer'))

# ################################################################################################################################

    def test_disallowed_service(self):
        store = _MockServiceStore()
        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]

        self.assertFalse(registry.is_tool_allowed('billing.create-invoice'))

# ################################################################################################################################

    def test_internal_service_always_disallowed(self):
        store = _MockServiceStore()
        registry = ToolRegistry(store, ['zato.server.info']) # pyright: ignore[reportArgumentType]

        self.assertFalse(registry.is_tool_allowed('zato.server.info'))

# ################################################################################################################################

    def test_internal_prefix_checked(self):
        store = _MockServiceStore()
        registry = ToolRegistry(store, ['zato.ping']) # pyright: ignore[reportArgumentType]

        self.assertFalse(registry.is_tool_allowed('zato.ping'))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()
