# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The headers the Dashboard's service client sends with each invocation.

# stdlib
from http.client import OK

# Zato
from zato.admin.middleware import Client
from zato.client import ZatoClient
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strstrdict

    # Add dummy assignments to satisfy type checkers
    any_ = any_
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

_server_address = 'http://localhost:17010'
_invoke_path    = '/zato/api/invoke/{}'
_username       = 'admin.invoke'
_password       = CryptoManager.generate_password(to_str=True)

# ################################################################################################################################
# ################################################################################################################################

class _UserStub:
    """ Stands in for a Django user.
    """

    def __init__(self, username:'str', is_authenticated:'bool') -> 'None':
        self.username = username
        self.is_authenticated = is_authenticated

# ################################################################################################################################

class _RequestStub:
    """ Stands in for a Django request.
    """

    def __init__(self, username:'str', is_authenticated:'bool') -> 'None':
        self.META = {'REMOTE_ADDR': '10.20.30.40'}
        self.user = _UserStub(username, is_authenticated)

# ################################################################################################################################

class _ResponseInnerStub:
    """ Stands in for the requests-level response.
    """
    status_code = OK

# ################################################################################################################################

class _ResponseStub:
    """ Stands in for the client-level response.
    """
    ok    = True
    inner = _ResponseInnerStub()
    data  = {'response': {'pong': 'zato'}}

# ################################################################################################################################

def _new_client(request:'_RequestStub') -> 'Client':
    credentials = (_username, _password)
    out = Client(request, _server_address, _invoke_path, auth=credentials)
    return out

# ################################################################################################################################

def _new_fake_invoke(captured:'strstrdict') -> 'any_':
    """ A stand-in for the underlying invocation that keeps the headers it was given.
    """

    def _fake_invoke(self:'any_', *args:'any_', **kwargs:'any_') -> '_ResponseStub':
        captured.update(kwargs['headers'])
        out = _ResponseStub()
        return out

    out = _fake_invoke
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestInvokeHeaders:
    """ The headers each invocation carries.
    """

    def test_the_username_travels_in_the_x_zato_user_header(self:'any_', monkeypatch:'any_') -> 'None':

        # Patch the underlying invocation ..
        captured:'strstrdict' = {}
        monkeypatch.setattr(ZatoClient, 'invoke', _new_fake_invoke(captured))

        # .. invoke through the client ..
        request = _RequestStub('dashboard.admin', True)
        client = _new_client(request)
        _ = client.invoke('demo.ping')

        # .. and the headers carry the caller's identity.
        assert captured['X-Zato-User'] == 'dashboard.admin'
        assert captured['X-Zato-Forwarded-For'] == '10.20.30.40'

# ################################################################################################################################

    def test_an_anonymous_request_sends_an_empty_username(self:'any_', monkeypatch:'any_') -> 'None':

        # Patch the underlying invocation ..
        captured:'strstrdict' = {}
        monkeypatch.setattr(ZatoClient, 'invoke', _new_fake_invoke(captured))

        # .. invoke through the client ..
        request = _RequestStub('ignored', False)
        client = _new_client(request)
        _ = client.invoke('demo.ping')

        # .. and an anonymous caller has no username to send.
        assert captured['X-Zato-User'] == ''

# ################################################################################################################################

    def test_the_async_invocation_sends_the_same_headers(self:'any_', monkeypatch:'any_') -> 'None':

        # Patch the underlying invocation ..
        captured:'strstrdict' = {}
        monkeypatch.setattr(ZatoClient, 'invoke_async', _new_fake_invoke(captured))

        # .. invoke through the client ..
        request = _RequestStub('dashboard.admin', True)
        client = _new_client(request)
        _ = client.invoke_async('demo.ping')

        # .. and the headers carry the caller's identity.
        assert captured['X-Zato-User'] == 'dashboard.admin'
        assert captured['X-Zato-Forwarded-For'] == '10.20.30.40'

# ################################################################################################################################
# ################################################################################################################################
