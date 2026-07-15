# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

class TestConfig:
    """ The identifiers the whole suite signs in with - the values look the way
    a real Entra ID tenant publishes them.
    """
    __test__ = False

    tenant_id     = '7c1b32a4-2d5e-4f8a-9b3c-6e1d0a842f95'
    client_id     = 'e94f2d81-63b7-4c5a-8f2e-1a9d7b3c4e60'
    client_secret = 'client-secret-' + CryptoManager.generate_hex_string()

    group_admin = '9d7c5b3a-8e6f-4a2b-9c1d-3e5f7a9b1c2d'

    user_principal_name = 'test.user@example.com'
    user_display_name   = 'Test User'

    redirect_url = 'http://testserver/accounts/login/callback/'

# ################################################################################################################################
# ################################################################################################################################
