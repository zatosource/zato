# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.server.connection.mcp.registry import ToolRegistry, _default_page_size

# ################################################################################################################################
# ################################################################################################################################

class _MockServiceStore:
    """ Minimal mock of ServiceStore with name_to_impl_name and services dicts.
    """
    def __init__(self) -> 'None':
        self.name_to_impl_name:'anydict' = {}
        self.services:'anydict' = {}

    def add_service(self, name:'str', service_class:'type', impl_name:'str | None' = None) -> 'None':
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

if 0:
    from zato.common.typing_ import anydict

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

    def test_single_service(self) -> 'None':
        """ Verifies that a single allowed service produces one tool entry.
        """

        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]
        registry.rebuild()
        tools = registry.get_tools()

        self.assertEqual(len(tools), 1)

        first_tool = tools[0]
        tool_name = first_tool['name']
        tool_description = first_tool['description']
        tool_input_schema = first_tool['inputSchema']
        self.assertEqual(tool_name, 'crm.get-customer')
        self.assertEqual(tool_description, 'Returns customer details by ID.')
        self.assertEqual(tool_input_schema, {'type': 'object'})

# ################################################################################################################################

    def test_multiple_services(self) -> 'None':
        """ Verifies that multiple allowed services produce multiple tool entries.
        """

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

    def test_service_without_docstring(self) -> 'None':
        """ Verifies that a service without a docstring gets an empty description.
        """

        store = _MockServiceStore()
        store.add_service('my.service', _ServiceNoDoc)

        registry = ToolRegistry(store, ['my.service']) # pyright: ignore[reportArgumentType]
        registry.rebuild()
        tools = registry.get_tools()

        first_tool = tools[0]
        self.assertEqual(first_tool['description'], '')

# ################################################################################################################################

    def test_internal_service_excluded(self) -> 'None':
        """ Verifies that services with the zato. prefix are excluded.
        """

        store = _MockServiceStore()
        store.add_service('zato.server.info', _ServiceWithDoc)
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['zato.server.info', 'crm.get-customer']) # pyright: ignore[reportArgumentType]
        registry.rebuild()
        tools = registry.get_tools()

        self.assertEqual(len(tools), 1)

        first_tool = tools[0]
        self.assertEqual(first_tool['name'], 'crm.get-customer')

# ################################################################################################################################

    def test_unknown_service_raises(self) -> 'None':
        """ Verifies that a service not in the store causes rebuild to raise.
        """

        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer', 'nonexistent.service']) # pyright: ignore[reportArgumentType]

        with self.assertRaises(ValueError):
            registry.rebuild()

# ################################################################################################################################

    def test_empty_allow_list(self) -> 'None':
        """ Verifies that an empty allow list produces no tools.
        """

        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, []) # pyright: ignore[reportArgumentType]
        registry.rebuild()
        tools = registry.get_tools()

        self.assertEqual(len(tools), 0)

# ################################################################################################################################

    def test_only_internal_services_in_allow_list(self) -> 'None':
        """ Verifies that an allow list with only internal services produces no tools.
        """

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

    def test_not_built_until_rebuild_called(self) -> 'None':
        """ Verifies that the cache is empty until rebuild is called explicitly.
        """

        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]

        # Not built until rebuild() is called explicitly
        self.assertEqual(len(registry._cached_tools), 0)

        registry.rebuild()
        self.assertEqual(len(registry._cached_tools), 1)

# ################################################################################################################################

    def test_cached_result_returned(self) -> 'None':
        """ Verifies that get_tools returns the same cached list object.
        """

        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        tools_1 = registry.get_tools()
        tools_2 = registry.get_tools()

        # Same list object returned from cache
        self.assertIs(tools_1, tools_2)

# ################################################################################################################################

    def test_rebuild_updates_cache(self) -> 'None':
        """ Verifies that rebuild refreshes the cached tools list.
        """

        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]
        registry.rebuild()
        tools_before = registry.get_tools()

        self.assertEqual(len(tools_before), 1)

        # Add a new service to the store and allow list
        store.add_service('billing.create-invoice', _ServiceNoDoc)
        registry.allowed_services = ['crm.get-customer', 'billing.create-invoice']
        registry.rebuild()

        tools_after = registry.get_tools()

        self.assertEqual(len(tools_after), 2)

# ################################################################################################################################

    def test_rebuild_after_service_removed_from_store(self) -> 'None':
        """ Verifies that rebuild raises when a previously deployed service is removed.
        """

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

        with self.assertRaises(ValueError):
            registry.rebuild()

# ################################################################################################################################
# ################################################################################################################################

class ToolRegistryPagination(TestCase):
    """ Tests for cursor-based pagination in get_tools_page.
    """

# ################################################################################################################################

    def test_no_cursor_returns_all_when_under_page_size(self) -> 'None':
        """ Verifies that all tools are returned in one page when under page size.
        """

        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)
        store.add_service('billing.create-invoice', _ServiceNoDoc)

        registry = ToolRegistry(store, ['crm.get-customer', 'billing.create-invoice']) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        tools, next_cursor = registry.get_tools_page()

        self.assertEqual(len(tools), 2)
        self.assertIsNone(next_cursor)

# ################################################################################################################################

    def test_no_cursor_with_empty_registry(self) -> 'None':
        """ Verifies that an empty registry returns an empty page.
        """

        store = _MockServiceStore()

        registry = ToolRegistry(store, []) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        tools, next_cursor = registry.get_tools_page()

        self.assertEqual(len(tools), 0)
        self.assertIsNone(next_cursor)

# ################################################################################################################################

    def test_cursor_zero_same_as_no_cursor(self) -> 'None':
        """ Verifies that cursor '0' produces the same result as no cursor.
        """

        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        tools_no_cursor, _ = registry.get_tools_page()
        tools_cursor_zero, _ = registry.get_tools_page('0')

        self.assertEqual(tools_no_cursor, tools_cursor_zero)

# ################################################################################################################################

    def test_pagination_splits_tools(self) -> 'None':
        """ Verifies that tools are split across pages when exceeding page size.
        """

        store = _MockServiceStore()

        # Create more services than the default page size
        total_services = _default_page_size + 5

        service_names = []

        for _ in range(total_services):
            name = f'svc.service-{len(service_names):04d}'
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

    def test_cursor_beyond_end_returns_empty(self) -> 'None':
        """ Verifies that a cursor beyond the end returns an empty page.
        """

        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        tools, next_cursor = registry.get_tools_page('999')

        self.assertEqual(len(tools), 0)
        self.assertIsNone(next_cursor)

# ################################################################################################################################

    def test_all_tools_reachable_via_pagination(self) -> 'None':
        """ Verifies that paginating through all pages collects all tools.
        """

        store = _MockServiceStore()

        total_services = _default_page_size * 3 + 7

        service_names = []

        for _ in range(total_services):
            name = f'svc.service-{len(service_names):04d}'
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

    def test_allowed_service(self) -> 'None':
        """ Verifies that an allowed service passes the check.
        """

        store = _MockServiceStore()
        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]

        self.assertTrue(registry.is_tool_allowed('crm.get-customer'))

# ################################################################################################################################

    def test_disallowed_service(self) -> 'None':
        """ Verifies that a non-listed service fails the check.
        """

        store = _MockServiceStore()
        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]

        self.assertFalse(registry.is_tool_allowed('billing.create-invoice'))

# ################################################################################################################################

    def test_internal_service_always_disallowed(self) -> 'None':
        """ Verifies that internal services are always disallowed.
        """

        store = _MockServiceStore()
        registry = ToolRegistry(store, ['zato.server.info']) # pyright: ignore[reportArgumentType]

        self.assertFalse(registry.is_tool_allowed('zato.server.info'))

# ################################################################################################################################

    def test_internal_prefix_checked(self) -> 'None':
        """ Verifies that the zato. prefix is checked for rejection.
        """

        store = _MockServiceStore()
        registry = ToolRegistry(store, ['zato.ping']) # pyright: ignore[reportArgumentType]

        self.assertFalse(registry.is_tool_allowed('zato.ping'))

# ################################################################################################################################
# ################################################################################################################################

class RegistryCursorGuard(TestCase):
    """ Tests for cursor validation and clamping in get_tools_page.
    """

# ################################################################################################################################

    def test_negative_cursor_clamped_to_first_page(self) -> 'None':
        """ Verifies that a negative cursor is clamped to 0 and returns the first page.
        """

        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        tools_negative, cursor_negative = registry.get_tools_page('-5')
        tools_zero, cursor_zero = registry.get_tools_page('0')

        self.assertEqual(tools_negative, tools_zero)
        self.assertEqual(cursor_negative, cursor_zero)

# ################################################################################################################################

    def test_out_of_range_cursor_returns_empty_page(self) -> 'None':
        """ Verifies that a cursor beyond the tool count is clamped and returns an empty page.
        """

        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)
        store.add_service('billing.create-invoice', _ServiceNoDoc)

        registry = ToolRegistry(store, ['crm.get-customer', 'billing.create-invoice']) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        tools, next_cursor = registry.get_tools_page('99999')

        self.assertEqual(len(tools), 0)
        self.assertIsNone(next_cursor)

# ################################################################################################################################

    def test_valid_cursor_returns_expected_page(self) -> 'None':
        """ Verifies that a valid numeric cursor returns the correct slice and nextCursor.
        """

        store = _MockServiceStore()

        total_services = _default_page_size + 10

        service_names = []

        for _ in range(total_services):
            name = f'svc.service-{len(service_names):04d}'
            store.add_service(name, _ServiceWithDoc)
            service_names.append(name)

        registry = ToolRegistry(store, service_names) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        # Request second page starting at _default_page_size
        cursor_value = str(_default_page_size)
        tools, next_cursor = registry.get_tools_page(cursor_value)

        self.assertEqual(len(tools), 10)
        self.assertIsNone(next_cursor)

        # First tool on second page should be the one at index _default_page_size
        expected_name = f'svc.service-{_default_page_size:04d}'
        first_tool = tools[0]
        self.assertEqual(first_tool['name'], expected_name)

# ################################################################################################################################

    def test_non_numeric_cursor_raises(self) -> 'None':
        """ Verifies that a non-numeric cursor raises ValueError.
        """

        store = _MockServiceStore()
        store.add_service('crm.get-customer', _ServiceWithDoc)

        registry = ToolRegistry(store, ['crm.get-customer']) # pyright: ignore[reportArgumentType]
        registry.rebuild()

        with self.assertRaises(ValueError):
            _ = registry.get_tools_page('abc')

# ################################################################################################################################
# ################################################################################################################################
