# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import FOUND, UNAUTHORIZED

from api_portal_lib import Portal_Login_Path, Portal_Path, Path_Diffing, Path_Methods, Path_Typed, Path_Untyped, \
    Relay_Base_Path, Spec_JSON_Path, Spec_YAML_Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The one body every session failure returns, by design
_Unauthorized_Body = 'Unauthorized'

# None of these may ever appear in a response to a caller without a session
_Fixture_Names = [
    Path_Typed,
    Path_Untyped,
    Path_Methods,
    Path_Diffing,
    'GetUserRequest',
    'GetUserResponse',
    'ContractResponse',
]

# ################################################################################################################################
# ################################################################################################################################

class TestAPIPortalSecurityNoSession:
    """ Verifies that a caller with no session at all gets nothing from the portal -
    a redirect from the page, one fixed rejection from every data endpoint and nothing else in the body.
    """

# ################################################################################################################################

    def test_no_session(self, playwright_browser:'any_', zato_dashboard:'anydict') -> 'None':
        """ Requests every portal endpoint from a brand-new browser context with no cookies.
        """
        portal_url = zato_dashboard['portal_url']

        # A brand-new context carries no cookies of any kind
        context = playwright_browser.new_context()

        try:
            # The portal page redirects to the sign-in page ..
            response = context.request.get(portal_url + Portal_Path, max_redirects=0)
            assert response.status == FOUND, f'Expected a redirect, got {response.status}: {response.text()}'

            location = response.headers['location']
            assert location == Portal_Login_Path, f'Expected a redirect to the sign-in page, got: {location}'

            # .. and every data endpoint returns the one fixed rejection.
            data_paths = [
                Spec_JSON_Path,
                Spec_YAML_Path,
                Relay_Base_Path,
            ]

            for data_path in data_paths:

                response = context.request.get(portal_url + data_path)
                body = response.text()

                assert response.status == UNAUTHORIZED, f'Expected 401 from {data_path}, got {response.status}: {body}'
                assert body == _Unauthorized_Body, f'Expected the fixed rejection body from {data_path}, got: {body}'

                # No fixture path or schema name may appear in the rejection
                for fixture_name in _Fixture_Names:
                    assert fixture_name not in body, f'`{fixture_name}` appeared in the response from {data_path}: {body}'

        finally:
            context.close()

# ################################################################################################################################
# ################################################################################################################################
