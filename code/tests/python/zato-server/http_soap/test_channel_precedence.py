# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import MagicMock

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.util.url_dispatcher import build_methods_allowed_re, get_match_target, to_internal_accept
from zato.server.connection.http_soap.url_data import URLData
from zato.server.connection.http_soap.url_dispatcher import Matcher

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

_any_accept = to_internal_accept(HTTP_SOAP.ACCEPT.ANY)

_methods_allowed_re = build_methods_allowed_re(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])

# ################################################################################################################################
# ################################################################################################################################

def _make_channel_item(
    url_path:'str',
    name:'str',
    method:'str'='',
    http_accept:'str'='',
    is_internal:'bool'=False,
    ) -> 'anydict':
    """ Builds a channel item with its match target built the way the server builds one.
    """
    config = {
        'url_path': url_path,
        'method': method,
        'http_accept': http_accept,
    }

    match_target = get_match_target(config, http_methods_allowed_re=_methods_allowed_re)

    out:'anydict' = {
        'name': name,
        'url_path': url_path,
        'method': method,
        'http_accept': http_accept,
        'is_internal': is_internal,
        'match_target': match_target,
        'match_target_compiled': Matcher(match_target),
    }

    return out

# ################################################################################################################################

def _make_url_data(channel_data:'anylist') -> 'URLData':
    """ A URLData with everything but its channel data mocked out. Sorting the channel data is part
    of what it does on the way up, so what comes back is already in matching order.
    """
    out = URLData(MagicMock(), channel_data=channel_data)
    return out

# ################################################################################################################################

def _names_in_order(url_data:'URLData') -> 'strlist':
    out = [item['name'] for item in url_data.channel_data]
    return out

# ################################################################################################################################

def _matched_name(url_data:'URLData', url_path:'str', http_method:'str'='GET') -> 'str':
    _, channel_item = url_data.match(url_path, http_method, _any_accept)

    out = channel_item['name']
    return out

# ################################################################################################################################
# ################################################################################################################################

class MatchingPrecedenceTestCase(TestCase):
    """ Which channel answers a request that more than one of them matches.

    A path parameter takes in whole segments and, by default, several of them, so a channel with a
    parameter early in its path also matches the paths that channels with longer literal paths sit
    at. Nothing about a channel's name has any bearing on which of the two is the narrower one.
    """

# ################################################################################################################################

    def test_a_literal_path_wins_over_a_parameter(self) -> 'None':

        # Sorted by name, the wildcard channel would come first and answer both requests
        url_data = _make_url_data([
            _make_channel_item('/api/{action}', 'a.wildcard.channel'),
            _make_channel_item('/api/admin', 'z.admin.channel'),
        ])

        self.assertEqual(_matched_name(url_data, '/api/admin'), 'z.admin.channel')
        self.assertEqual(_matched_name(url_data, '/api/something-else'), 'a.wildcard.channel')

# ################################################################################################################################

    def test_a_deeper_literal_path_wins_over_a_parameter_matching_across_slashes(self) -> 'None':
        url_data = _make_url_data([
            _make_channel_item('/api/{action}', 'a.wildcard.channel'),
            _make_channel_item('/api/admin/keys', 'z.keys.channel'),
        ])

        self.assertEqual(_matched_name(url_data, '/api/admin/keys'), 'z.keys.channel')

# ################################################################################################################################

    def test_the_longer_path_wins_between_two_of_one_literal_prefix(self) -> 'None':
        url_data = _make_url_data([
            _make_channel_item('/api/{id}', 'a.item.channel'),
            _make_channel_item('/api/{id}/history', 'z.history.channel'),
        ])

        self.assertEqual(_matched_name(url_data, '/api/123/history'), 'z.history.channel')
        self.assertEqual(_matched_name(url_data, '/api/123'), 'a.item.channel')

# ################################################################################################################################

    def test_a_channel_naming_an_accept_value_comes_first(self) -> 'None':
        url_data = _make_url_data([
            _make_channel_item('/api/invoice', 'a.any.channel'),
            _make_channel_item('/api/invoice', 'z.json.channel', http_accept='application/json'),
        ])

        self.assertEqual(_names_in_order(url_data), ['z.json.channel', 'a.any.channel'])

# ################################################################################################################################

    def test_a_channel_naming_a_method_comes_first(self) -> 'None':
        url_data = _make_url_data([
            _make_channel_item('/api/invoice', 'a.any.channel'),
            _make_channel_item('/api/invoice', 'z.post.channel', method='POST'),
        ])

        self.assertEqual(_names_in_order(url_data), ['z.post.channel', 'a.any.channel'])

# ################################################################################################################################

    def test_two_channels_of_one_shape_are_ordered_by_name(self) -> 'None':

        # Nothing tells these two apart, so the order is at least the same on every server
        url_data = _make_url_data([
            _make_channel_item('/api/{id}', 'z.channel'),
            _make_channel_item('/api/{id}', 'a.channel'),
        ])

        self.assertEqual(_names_in_order(url_data), ['a.channel', 'z.channel'])

# ################################################################################################################################

    def test_internal_channels_stay_behind_the_user_facing_ones(self) -> 'None':
        url_data = _make_url_data([
            _make_channel_item('/zato/api/invoice', 'a.internal.channel', is_internal=True),
            _make_channel_item('/api/{id}', 'z.user.channel'),
        ])

        self.assertEqual(_names_in_order(url_data), ['z.user.channel', 'a.internal.channel'])

# ################################################################################################################################

    def test_a_channel_created_later_takes_its_place_in_the_order(self) -> 'None':

        # The order is rebuilt on every configuration change, so a narrower channel added to a
        # running server starts answering the requests that the broader one was answering.
        url_data = _make_url_data([_make_channel_item('/api/{action}', 'a.wildcard.channel')])

        self.assertEqual(_matched_name(url_data, '/api/admin'), 'a.wildcard.channel')

        url_data.channel_data.append(_make_channel_item('/api/admin', 'z.admin.channel'))
        url_data.sort_channel_data()
        url_data.url_path_cache.clear()

        self.assertEqual(_matched_name(url_data, '/api/admin'), 'z.admin.channel')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
