# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.test import RequestFactory

# Zato
from zato.common.webapp.request import client_address, No_Remote_Address

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class TestClientAddress:

    def test_zato_header_wins_over_everything(self:'any_') -> 'None':
        factory = RequestFactory()
        request = factory.get(
            '/',
            HTTP_X_ZATO_FORWARDED_FOR='192.0.2.10',
            HTTP_X_FORWARDED_FOR='192.0.2.20',
            REMOTE_ADDR='192.0.2.30',
        )

        out = client_address(request)
        assert out == '192.0.2.10'

# ################################################################################################################################

    def test_forwarded_header_wins_over_remote_addr(self:'any_') -> 'None':
        factory = RequestFactory()
        request = factory.get(
            '/',
            HTTP_X_FORWARDED_FOR='192.0.2.20',
            REMOTE_ADDR='192.0.2.30',
        )

        out = client_address(request)
        assert out == '192.0.2.20'

# ################################################################################################################################

    def test_remote_addr_is_the_last_resort(self:'any_') -> 'None':
        factory = RequestFactory()
        request = factory.get('/', REMOTE_ADDR='192.0.2.30')

        out = client_address(request)
        assert out == '192.0.2.30'

# ################################################################################################################################

    def test_no_address_at_all(self:'any_') -> 'None':
        factory = RequestFactory()
        request = factory.get('/')

        # The factory always sets a remote address, so it has to go for this case
        _ = request.META.pop('REMOTE_ADDR')

        out = client_address(request)
        assert out == No_Remote_Address

# ################################################################################################################################
# ################################################################################################################################
