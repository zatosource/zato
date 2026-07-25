# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.api import MISC
from zato.common.util.url_dispatcher import get_match_target, normalize_path_info

# ################################################################################################################################
# ################################################################################################################################

_separator = MISC.SEPARATOR
_methods_allowed = '(?:GET|POST|PUT|PATCH|DELETE)'

# ################################################################################################################################
# ################################################################################################################################

class NormalizePathInfoTestCase(unittest.TestCase):
    """ Tests for the form a caller's own path is matched in.
    """

# ################################################################################################################################

    def test_a_plain_path_is_left_as_it_is(self) -> 'None':
        self.assertEqual(normalize_path_info('/api/invoice'), '/api/invoice')

# ################################################################################################################################

    def test_duplicate_slashes_collapse(self) -> 'None':
        self.assertEqual(normalize_path_info('/api//invoice///0001'), '/api/invoice/0001')

# ################################################################################################################################

    def test_a_single_dot_segment_goes(self) -> 'None':
        self.assertEqual(normalize_path_info('/api/./invoice'), '/api/invoice')

# ################################################################################################################################

    def test_a_double_dot_segment_cancels_the_one_in_front_of_it(self) -> 'None':
        self.assertEqual(normalize_path_info('/api/customer/../invoice'), '/api/invoice')

# ################################################################################################################################

    def test_a_double_dot_segment_at_the_root_has_nothing_to_cancel(self) -> 'None':
        self.assertEqual(normalize_path_info('/../api/invoice'), '/api/invoice')

# ################################################################################################################################

    def test_a_trailing_slash_stays(self) -> 'None':
        self.assertEqual(normalize_path_info('/api/invoice/'), '/api/invoice/')

# ################################################################################################################################

    def test_the_root_path_stays_the_root_path(self) -> 'None':
        self.assertEqual(normalize_path_info('/'), '/')

# ################################################################################################################################

    def test_percent_encoded_characters_are_decoded(self) -> 'None':
        self.assertEqual(normalize_path_info('/api/caf%C3%A9'), '/api/café')

# ################################################################################################################################

    def test_an_encoded_space_is_decoded(self) -> 'None':
        self.assertEqual(normalize_path_info('/api/invoice%20list'), '/api/invoice list')

# ################################################################################################################################

    def test_an_encoded_slash_stays_encoded(self) -> 'None':

        # Decoding it would hand the path a separator the caller never sent.
        self.assertEqual(normalize_path_info('/api/invoice%2F0001'), '/api/invoice%2F0001')

# ################################################################################################################################

    def test_encoded_dot_segments_are_not_resolved_after_decoding(self) -> 'None':

        # The segments are resolved before anything is decoded, so this stays one literal segment.
        self.assertEqual(normalize_path_info('/api/%2E%2E/invoice'), '/api/../invoice')

# ################################################################################################################################
# ################################################################################################################################

class GetMatchTargetTestCase(unittest.TestCase):
    """ Tests for the pattern a channel is matched by.
    """

# ################################################################################################################################

    def _get_target(self, config:'dict') -> 'str':
        out = get_match_target(config, http_methods_allowed_re=_methods_allowed)
        return out

# ################################################################################################################################

    def test_a_channel_without_a_method_accepts_the_allowed_ones(self) -> 'None':
        target = self._get_target({'url_path': '/api/invoice'})

        expected = f'{_separator}{_methods_allowed}{_separator}haanyHTTP_SEPhaany{_separator}/api/invoice'
        self.assertEqual(target, expected)

# ################################################################################################################################

    def test_regular_expression_syntax_in_the_path_is_escaped(self) -> 'None':
        target = self._get_target({'url_path': '/api/invoice.list+all(1)', 'method': 'GET'})

        self.assertIn(r'/api/invoice\.list\+all\(1\)', target)

# ################################################################################################################################

    def test_path_parameters_survive_the_escaping(self) -> 'None':
        target = self._get_target({'url_path': '/api/invoice/{invoice_id}', 'method': 'GET'})

        self.assertIn('/api/invoice/{invoice_id}', target)

# ################################################################################################################################

    def test_regular_expression_syntax_around_a_parameter_is_escaped(self) -> 'None':
        target = self._get_target({'url_path': '/api/v1.0/{invoice_id}.json', 'method': 'GET'})

        self.assertIn(r'/api/v1\.0/{invoice_id}\.json', target)

# ################################################################################################################################

    def test_regular_expression_syntax_in_the_accept_header_is_escaped(self) -> 'None':
        target = self._get_target({'url_path': '/api/invoice', 'method': 'GET', 'http_accept': 'application/vnd.api+json'})

        self.assertIn(r'applicationHTTP_SEPvnd\.api\+json', target)

# ################################################################################################################################

    def test_the_any_accept_marker_is_left_for_the_matcher(self) -> 'None':
        target = self._get_target({'url_path': '/api/invoice', 'method': 'GET', 'http_accept': '*/*'})

        self.assertIn('haanyHTTP_SEPhaany', target)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
