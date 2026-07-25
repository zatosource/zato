# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.channel import find_channel_collision

# ################################################################################################################################
# ################################################################################################################################

def make_item(name:'str', url_path:'str', method:'str'='', http_accept:'str'='*/*', item_id:'int'=1) -> 'dict':
    return {
        'id': item_id,
        'name': name,
        'url_path': url_path,
        'method': method,
        'http_accept': http_accept,
    }

# ################################################################################################################################
# ################################################################################################################################

class TestFindChannelCollision:

    def test_same_path_method_and_accept_collide(self) -> 'None':

        existing = [make_item('channel.1', '/api/customer')]
        result = find_channel_collision('/api/customer', '*/*', '', existing, None)

        assert result == 'channel.1'

    def test_different_url_path_never_collides(self) -> 'None':

        existing = [make_item('channel.1', '/api/customer')]
        result = find_channel_collision('/api/invoice', '*/*', '', existing, None)

        assert result is None

    def test_different_method_does_not_collide(self) -> 'None':

        existing = [make_item('channel.1', '/api/customer', method='POST')]
        result = find_channel_collision('/api/customer', '*/*', 'GET', existing, None)

        assert result is None

    def test_different_accept_does_not_collide(self) -> 'None':

        existing = [make_item('channel.1', '/api/customer', http_accept='application/json')]
        result = find_channel_collision('/api/customer', '*/*', '', existing, None)

        assert result is None

    def test_first_colliding_item_wins(self) -> 'None':

        existing = [
            make_item('channel.1', '/api/customer', method='POST', item_id=1),
            make_item('channel.2', '/api/customer', item_id=2),
            make_item('channel.3', '/api/customer', item_id=3),
        ]
        result = find_channel_collision('/api/customer', '*/*', '', existing, None)

        assert result == 'channel.2'

    def test_empty_existing_items(self) -> 'None':

        result = find_channel_collision('/api/customer', '*/*', '', [], None)

        assert result is None

    def test_a_channel_does_not_collide_with_itself(self) -> 'None':

        existing = [make_item('channel.1', '/api/customer', item_id=7)]
        result = find_channel_collision('/api/customer', '*/*', '', existing, 7)

        assert result is None

# ################################################################################################################################
# ################################################################################################################################
