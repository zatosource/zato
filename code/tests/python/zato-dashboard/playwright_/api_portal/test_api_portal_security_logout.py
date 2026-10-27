# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import FOUND, UNAUTHORIZED

from api_portal_lib import portal_login, Admin_Username, Portal_Login_Path, Portal_Logout_Path, Portal_Path, \
    Spec_JSON_Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The one body every session failure returns
_Unauthorized_Body = 'Unauthorized'

# ################################################################################################################################
# ################################################################################################################################

class TestAPIPortalSecurityLogout:
    """ Verifies that signing out ends the session for good - the stale cookie
    grants no access to the portal page or the document endpoint.
    """

# ################################################################################################################################

    def test_logout(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Signs in, signs out and asserts the old session cookie is worthless.
        """
        page = logged_in_page
        portal_url = zato_dashboard['portal_url']
        password = zato_dashboard['password']

        # Establish a valid session first ..
        portal_login(page, portal_url, Admin_Username, password)

        # .. signing out redirects to the sign-in page ..
        response = page.request.get(portal_url + Portal_Logout_Path, max_redirects=0)
        assert response.status == FOUND, f'Expected a redirect from logout, got {response.status}'

        location = response.headers['location']
        assert location == Portal_Login_Path, f'Expected a redirect to the sign-in page, got: {location}'

        # .. the stale cookie no longer opens the portal page ..
        response = page.request.get(portal_url + Portal_Path, max_redirects=0)
        assert response.status == FOUND, f'Expected a redirect from the portal page, got {response.status}'

        location = response.headers['location']
        assert location == Portal_Login_Path, f'Expected a redirect to the sign-in page, got: {location}'

        # .. and no longer opens the document endpoint either.
        response = page.request.get(portal_url + Spec_JSON_Path)
        body = response.text()

        assert response.status == UNAUTHORIZED, f'Expected 401 from the document endpoint, got {response.status}: {body}'
        assert body == _Unauthorized_Body, f'Expected the fixed rejection body, got: {body}'

# ################################################################################################################################
# ################################################################################################################################
