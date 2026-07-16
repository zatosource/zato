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
_deprecation_sunset    = '2030-06-30'
_deprecation_successor = '/api/v2/orders'

# The URL paths of the two test endpoints - the deprecated one and its successor
_url_path_deprecated = '/api/v1/orders'
_url_path_regular    = '/api/v2/orders'

# ################################################################################################################################
# ################################################################################################################################

def _make_service_entry(name:'str', url_path:'str', is_deprecated:'bool') -> 'anydict':
    """ Builds one generator service entry, deprecated or not.
    """
    if is_deprecated:
        deprecation_sunset = _deprecation_sunset
        deprecation_successor = _deprecation_successor
    else:
        deprecation_sunset = ''
        deprecation_successor = ''

    out = {
        'name': name,
        'class_name': 'GetOrders',
        'url_path': url_path,
        'http_method': 'get',
        'input': {'type': 'any'},
        'output': {'type': 'any'},
        'is_deprecated': is_deprecated,
        'deprecation_sunset': deprecation_sunset,
        'deprecation_successor': deprecation_successor,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDeprecatedOpenAPI(TestCase):

    def test_deprecated_flag_in_document(self):
        """ A deprecated endpoint carries deprecated:true and its description names
        the sunset date and the successor path, while a regular endpoint carries neither.
        """
        deprecated_entry = _make_service_entry('api.orders.get-list', _url_path_deprecated, True)
        regular_entry = _make_service_entry('api.orders.get-details', _url_path_regular, False)

        spec_input = {
            'services': [deprecated_entry, regular_entry],
            'models': {},
        }

        type_mapper = TypeMapper()
        generator = OpenAPIGenerator(type_mapper)
        spec = generator.build_spec(spec_input)

        paths = spec['paths']

        # The deprecated endpoint is marked as such in the document itself ..
        deprecated_path = paths[_url_path_deprecated]
        deprecated_operation = deprecated_path['get']
        self.assertIs(deprecated_operation['deprecated'], True)

        # .. and its description points callers to the sunset date and the successor.
        description = deprecated_operation['description']
        self.assertIn('deprecated', description)
        self.assertIn(_deprecation_sunset, description)
        self.assertIn(_deprecation_successor, description)

        # A regular endpoint carries no deprecation information at all.
        regular_path = paths[_url_path_regular]
        regular_operation = regular_path['get']
        self.assertNotIn('deprecated', regular_operation)
        self.assertNotIn('deprecated', regular_operation['description'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
