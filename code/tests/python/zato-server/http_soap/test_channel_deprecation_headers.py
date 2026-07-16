# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.server.connection.http_soap.channel import _get_deprecation_headers

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# The moment the test channel became deprecated - noon UTC on 2026-01-15
_deprecation_since = '2026-01-15T12:00:00+00:00'

# The same moment as the Deprecation header announces it - a Unix timestamp
_deprecation_header_value = '@1768478400'

# The day the test channel will be retired and its HTTP-date form - midnight UTC
_deprecation_sunset           = '2030-06-30'
_deprecation_sunset_http_date = 'Sun, 30 Jun 2030 00:00:00 GMT'

# The URL path of the replacement channel and the Link header that points to it
_deprecation_successor = '/api/v2/orders'
_link_header_value     = f'<{_deprecation_successor}>; rel="successor-version"'

# ################################################################################################################################
# ################################################################################################################################

def _make_channel_item(
    deprecation_since:'str' = '',
    deprecation_sunset:'str' = '',
    deprecation_successor:'str' = '',
    ) -> 'anydict':
    """ Builds a deprecated channel item with the given deprecation attributes.
    """
    out = {
        'name': 'test.orders.v1',
        'is_deprecated': True,
        'deprecation_since': deprecation_since,
        'deprecation_sunset': deprecation_sunset,
        'deprecation_successor': deprecation_successor,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class DeprecationHeadersTestCase(unittest.TestCase):

    def test_all_headers_present(self) -> 'None':
        """ A channel with all the deprecation attributes announces all three headers.
        """
        channel_item = _make_channel_item(_deprecation_since, _deprecation_sunset, _deprecation_successor)

        headers = _get_deprecation_headers(channel_item)

        self.assertEqual(headers['Deprecation'], _deprecation_header_value)
        self.assertEqual(headers['Sunset'], _deprecation_sunset_http_date)
        self.assertEqual(headers['Link'], _link_header_value)

# ################################################################################################################################

    def test_since_only(self) -> 'None':
        """ A channel deprecated without a sunset date or a successor announces the Deprecation header only.
        """
        channel_item = _make_channel_item(deprecation_since=_deprecation_since)

        headers = _get_deprecation_headers(channel_item)

        self.assertEqual(headers['Deprecation'], _deprecation_header_value)
        self.assertNotIn('Sunset', headers)
        self.assertNotIn('Link', headers)

# ################################################################################################################################

    def test_no_attributes_means_no_headers(self) -> 'None':
        """ A channel with the flag alone and no attribute values announces nothing.
        """
        channel_item = _make_channel_item()

        headers = _get_deprecation_headers(channel_item)

        self.assertEqual(headers, {})

# ################################################################################################################################

    def test_headers_are_memoized(self) -> 'None':
        """ The headers are built once and reused for every following request.
        """
        channel_item = _make_channel_item(_deprecation_since, _deprecation_sunset, _deprecation_successor)

        first = _get_deprecation_headers(channel_item)

        # A later change to the attributes must not rebuild the memoized headers -
        # a real configuration change replaces the whole channel item instead.
        channel_item['deprecation_successor'] = '/api/v3/orders'
        second = _get_deprecation_headers(channel_item)

        self.assertIs(second, first)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
