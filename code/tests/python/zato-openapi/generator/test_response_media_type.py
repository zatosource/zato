# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.openapi.generator.io_scanner import TypeMapper
from zato.openapi.generator.openapi_ import OpenAPIGenerator

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_url_path = '/api/orders'
_xml_media_type = 'application/xml'
_json_media_type = 'application/json'

# Output that any JSON object satisfies
_any_output = {'type': 'any'}

# ################################################################################################################################
# ################################################################################################################################

class ResponseMediaTypeTestCase(TestCase):
    """ An operation's responses are documented in the media type that its endpoint requires, or in JSON otherwise.
    """

# ################################################################################################################################

    def _get_success_response(self, **entry_fields:'anydict | str') -> 'anydict':
        """ Builds a document with one operation and returns the operation's success response.
        """
        entry:'anydict' = {
            'name': 'api.orders.get',
            'url_path': _url_path,
            'http_method': 'get',
        }
        entry.update(entry_fields)

        generator = OpenAPIGenerator(TypeMapper())
        spec = generator.build_spec({'services': [entry], 'models': {}})

        out = spec['paths'][_url_path]['get']['responses']['200']
        return out

# ################################################################################################################################

    def test_a_media_type_without_output(self) -> 'None':
        response = self._get_success_response(response_media_type=_xml_media_type)
        self.assertEqual(response['content'], {_xml_media_type: {}})

# ################################################################################################################################

    def test_a_media_type_with_output(self) -> 'None':
        response = self._get_success_response(response_media_type=_xml_media_type, output=_any_output)

        self.assertEqual(list(response['content']), [_xml_media_type])
        self.assertIn('schema', response['content'][_xml_media_type])

# ################################################################################################################################

    def test_json_with_output(self) -> 'None':
        response = self._get_success_response(output=_any_output)
        self.assertEqual(list(response['content']), [_json_media_type])

# ################################################################################################################################

    def test_no_media_type_and_no_output(self) -> 'None':
        response = self._get_success_response()
        self.assertNotIn('content', response)

# ################################################################################################################################

    def test_an_empty_media_type_is_json(self) -> 'None':
        response = self._get_success_response(response_media_type='', output=_any_output)
        self.assertEqual(list(response['content']), [_json_media_type])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
