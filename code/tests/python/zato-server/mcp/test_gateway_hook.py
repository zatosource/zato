# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.common.exception import BadRequest
from zato.common.util.gateway import on_mcp_gateway_create_edit

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

class _StubQuery:
    """ A query that finds nothing, whatever it is filtered or joined by.
    """
    def join(self, *args:'any_', **kwargs:'any_') -> '_StubQuery':
        return self

    def filter(self, *args:'any_', **kwargs:'any_') -> '_StubQuery':
        return self

    def first(self) -> 'None':
        return None

    def all(self) -> 'anylist':
        return []

# ################################################################################################################################

class _StubSession:
    """ A database session in which no object exists.
    """
    def query(self, *args:'any_', **kwargs:'any_') -> '_StubQuery':
        return _StubQuery()

    def close(self) -> 'None':
        pass

# ################################################################################################################################

class _StubODB:
    def session(self) -> '_StubSession':
        return _StubSession()

# ################################################################################################################################

class _StubServer:
    def __init__(self) -> 'None':
        self.odb = _StubODB()

# ################################################################################################################################

class _StubService:
    """ A service that records what it invokes instead of invoking it.
    """
    def __init__(self) -> 'None':
        self.cid = 'test-cid'
        self.server = _StubServer()
        self.invoked:'anylist' = []

    def invoke(self, service_name:'str', payload:'anydict') -> 'None':
        self.invoked.append((service_name, payload))

# ################################################################################################################################

class _StubModel:
    def __init__(self, is_active:'bool') -> 'None':
        self.is_active = is_active

# ################################################################################################################################
# ################################################################################################################################

def _make_data(**kwargs:'any_') -> 'anydict':
    """ The input of a gateway save, without is_active unless given.
    """
    out = {
        'name': 'Customer Records',
        'url_path': '/mcp/customer-records',
        'security_groups': [],
    }
    out.update(kwargs)

    return out

# ################################################################################################################################
# ################################################################################################################################

class ChannelIsActive(TestCase):
    """ The gateway's channel serves exactly when the stored gateway is active.
    """

    def test_inactive_gateway_saved_without_is_active(self) -> 'None':
        """ A save that does not carry is_active keeps the channel of an inactive gateway inactive.
        """
        service = _StubService()
        data = _make_data()

        on_mcp_gateway_create_edit(service, data, _StubModel(False), None)

        service_name, payload = service.invoked[0]

        self.assertEqual(service_name, 'zato.http-soap.create')
        self.assertIs(payload['is_active'], False)

    def test_active_gateway(self) -> 'None':
        """ The channel of an active gateway is active.
        """
        service = _StubService()
        data = _make_data(is_active=True)

        on_mcp_gateway_create_edit(service, data, _StubModel(True), None)

        _, payload = service.invoked[0]
        self.assertIs(payload['is_active'], True)

# ################################################################################################################################
# ################################################################################################################################

class SizeCapValidation(TestCase):
    """ Size caps that would break every tool call are refused when a gateway is saved.
    """

    def _assert_refused(self, **kwargs:'any_') -> 'None':
        service = _StubService()
        data = _make_data(**kwargs)

        with self.assertRaises(BadRequest):
            on_mcp_gateway_create_edit(service, data, _StubModel(True), None)

        self.assertEqual(service.invoked, [])

    def test_ratio_of_zero_refused(self) -> 'None':
        self._assert_refused(characters_per_token=0)

    def test_ratio_stored_as_false_refused(self) -> 'None':
        self._assert_refused(characters_per_token=False)

    def test_negative_ratio_refused(self) -> 'None':
        self._assert_refused(characters_per_token=-2.5)

    def test_infinite_ratio_refused(self) -> 'None':
        self._assert_refused(characters_per_token=float('inf'))

    def test_ratio_that_is_not_a_number_refused(self) -> 'None':
        self._assert_refused(characters_per_token=float('nan'))

    def test_ratio_as_text_refused(self) -> 'None':
        self._assert_refused(characters_per_token='four')

    def test_negative_max_response_size_refused(self) -> 'None':
        self._assert_refused(max_response_size=-1)

    def test_negative_min_size_threshold_refused(self) -> 'None':
        self._assert_refused(min_size_threshold=-100)

    def test_unknown_size_cap_mode_refused(self) -> 'None':
        self._assert_refused(size_cap_mode='compress')

    def test_valid_size_caps_accepted(self) -> 'None':
        service = _StubService()
        data = _make_data(characters_per_token=3.5, max_response_size=2000, min_size_threshold=False, size_cap_mode='block')

        on_mcp_gateway_create_edit(service, data, _StubModel(True), None)

        self.assertEqual(len(service.invoked), 1)

# ################################################################################################################################
# ################################################################################################################################
