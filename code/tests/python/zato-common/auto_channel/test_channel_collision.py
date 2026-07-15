# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.channel import find_channel_collision

# ################################################################################################################################
# ################################################################################################################################

def make_item(name:'str', url_path:'str', method:'str'='', soap_action:'str'='', http_accept:'str'='*/*') -> 'dict':
    return {
        'name': name,
        'url_path': url_path,
        'method': method,
        'soap_action': soap_action,
        'http_accept': http_accept,
    }

# ################################################################################################################################
# ################################################################################################################################

class TestFindChannelCollision:

    def test_same_path_method_and_accept_collide(self) -> 'None':

        existing = [make_item('channel.1', '/api/customer')]
        result = find_channel_collision('/api/customer', '*/*', '', '', existing)

        assert result == 'channel.1'

    def test_different_url_path_never_collides(self) -> 'None':

        existing = [make_item('channel.1', '/api/customer')]
        result = find_channel_collision('/api/invoice', '*/*', '', '', existing)

        assert result is None

    def test_different_soap_action_never_collides(self) -> 'None':

        existing = [make_item('channel.1', '/api/customer', soap_action='my.action')]
        result = find_channel_collision('/api/customer', '*/*', '', '', existing)

        assert result is None

    def test_different_method_does_not_collide(self) -> 'None':

        existing = [make_item('channel.1', '/api/customer', method='POST')]
        result = find_channel_collision('/api/customer', '*/*', 'GET', '', existing)

        assert result is None

    def test_different_accept_does_not_collide(self) -> 'None':

        existing = [make_item('channel.1', '/api/customer', http_accept='application/json')]
        result = find_channel_collision('/api/customer', '*/*', '', '', existing)

        assert result is None

    def test_first_colliding_item_wins(self) -> 'None':

        existing = [
            make_item('channel.1', '/api/customer', method='POST'),
            make_item('channel.2', '/api/customer'),
            make_item('channel.3', '/api/customer'),
        ]
        result = find_channel_collision('/api/customer', '*/*', '', '', existing)

        assert result == 'channel.2'

    def test_empty_existing_items(self) -> 'None':

        result = find_channel_collision('/api/customer', '*/*', '', '', [])

        assert result is None

# ################################################################################################################################
# ################################################################################################################################
