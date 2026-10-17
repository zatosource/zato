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

# The extension key of the example with every optional property
_complete_example_key = 'x-complete-example'

# The URL path both test endpoints share
_url_path = '/api/messages'

# One required input element and two optional ones
_input = {
    'type': 'tuple',
    'elements': [
        {'name': 'phone_number', 'required': True},
        {'name': 'message_to_user', 'required': False},
        {'name': 'authentication_method', 'required': False},
    ],
}

# ################################################################################################################################
# ################################################################################################################################

def _make_service_entry(name:'str', http_method:'str') -> 'anydict':
    """ Builds one generator service entry with the test input.
    """
    out = {
        'name': name,
        'class_name': 'SendMessage',
        'url_path': _url_path,
        'http_method': http_method,
        'input': _input,
        'output': {'type': 'any'},
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCompleteExample(TestCase):

    def setUp(self) -> 'None':
        services = [
            _make_service_entry('test.message.send', 'post'),
            _make_service_entry('test.message.get', 'get'),
        ]

        generator = OpenAPIGenerator(TypeMapper())
        self.document = generator.build_spec({'services': services, 'models': {}})

# ################################################################################################################################

    def test_a_request_body_has_both_examples(self) -> 'None':

        operation = self.document['paths'][_url_path]['post']
        content = operation['requestBody']['content']['application/json']

        # The standard example has only the required property ..
        self.assertEqual(list(content['example']), ['phone_number'])

        # .. and the complete one has every property.
        self.assertEqual(list(content[_complete_example_key]), ['phone_number', 'message_to_user', 'authentication_method'])

# ################################################################################################################################

    def test_every_query_string_parameter_has_a_complete_example(self) -> 'None':

        operation = self.document['paths'][_url_path]['get']
        parameters_by_name:'anydict' = {}

        for parameter in operation['parameters']:
            parameters_by_name[parameter['name']] = parameter

        # Only the required parameter has the standard example ..
        self.assertIn('example', parameters_by_name['phone_number'])
        self.assertNotIn('example', parameters_by_name['message_to_user'])

        # .. while each of them has the complete one.
        for parameter in parameters_by_name.values():
            self.assertIn(_complete_example_key, parameter)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
