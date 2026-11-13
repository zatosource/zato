# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The hooks a service runs around its handle method and the handlers of individual HTTP verbs.

# stdlib
from http.client import BAD_REQUEST, METHOD_NOT_ALLOWED, OK

# Zato
from channel_definitions import Paths

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_client import ChannelClient

# ################################################################################################################################
# ################################################################################################################################

def test_before_and_after_handle(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Hooks)

    assert response.status == OK
    assert response.json() == {'calls': ['before_handle', 'handle', 'after_handle']}

# ################################################################################################################################

def test_accept_returning_false(client:'ChannelClient') -> 'None':
    response = client.get(Paths.Not_Accepted)

    assert response.status == BAD_REQUEST
    assert response.headers['content-type'] == 'text/plain'
    assert response.body == b''

# ################################################################################################################################

def test_verb_handlers(client:'ChannelClient') -> 'None':

    response = client.get(Paths.Verbs)
    assert response.status == OK
    assert response.json() == {'verb': 'GET'}

    response = client.post_json(Paths.Verbs, {'customer_id': 1})
    assert response.status == OK
    assert response.json() == {
        'verb': 'POST',
        'payload': {'type': 'dict', 'value': {'customer_id': {'type': 'int', 'value': 1}}},
    }

# ################################################################################################################################

def test_verb_not_implemented(client:'ChannelClient') -> 'None':

    for method in ('PUT', 'DELETE', 'PATCH'):
        response = client.request(method, Paths.Verbs)

        assert response.status == METHOD_NOT_ALLOWED, method
        assert response.headers['content-type'] == 'application/json'
        assert response.body == b''

# ################################################################################################################################
# ################################################################################################################################
