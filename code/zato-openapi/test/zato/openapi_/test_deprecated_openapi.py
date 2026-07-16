# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# Zato
from zato.openapi.generator.io_scanner import TypeMapper
from zato.openapi.generator.openapi_ import OpenAPIGenerator

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# The deprecation attributes the deprecated test endpoint carries
_deprecation_sunset = '2030-06-30'
_deprecation_successor = '/api/v2/orders'

# ################################################################################################################################
# ################################################################################################################################

def _make_service_entry(name:'str', url_path:'str', is_deprecated:'bool') -> 'anydict':
    """ Builds one generator service entry, deprecated or not.
    """
    out = {
        'name': name,
        'class_name': 'GetOrders',
        'url_path': url_path,
        'http_method': 'get',
        'input': {'type': 'any'},
        'output': {'type': 'any'},
        'is_deprecated': is_deprecated,
        'deprecation_sunset': _deprecation_sunset if is_deprecated else '',
        'deprecation_successor': _deprecation_successor if is_deprecated else '',
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDeprecatedOpenAPI(TestCase):

    def test_deprecated_flag_in_document(self):
        """ A deprecated endpoint carries deprecated:true and its description names
        the sunset date and the successor path, while a regular endpoint carries neither.
        """
        services = [
            _make_service_entry('api.orders.get-list', '/api/v1/orders', True),
            _make_service_entry('api.orders.get-details', '/api/v2/orders', False),
        ]

        generator = OpenAPIGenerator(TypeMapper())
        spec = generator.build_spec({'services': services, 'models': {}})

        # The deprecated endpoint is marked as such in the document itself ..
        deprecated_operation = spec['paths']['/api/v1/orders']['get']
        self.assertIs(deprecated_operation['deprecated'], True)

        # .. and its description points callers to the sunset date and the successor.
        description = deprecated_operation['description']
        self.assertIn('deprecated', description)
        self.assertIn(_deprecation_sunset, description)
        self.assertIn(_deprecation_successor, description)

        # A regular endpoint carries no deprecation information at all.
        regular_operation = spec['paths']['/api/v2/orders']['get']
        self.assertNotIn('deprecated', regular_operation)
        self.assertNotIn('deprecated', regular_operation['description'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
