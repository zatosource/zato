# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http.client import FOUND, OK, UNAUTHORIZED

from openapi_console_lib import Admin_Username, Console_Login_Path, Console_Path, Spec_JSON_Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The one message the sign-in page shows for any rejected credentials
_Invalid_Credentials_Message = 'Invalid username or password'

# The one body every session failure returns
_Unauthorized_Body = 'Unauthorized'

# ################################################################################################################################
# ################################################################################################################################

def _submit_login_form(page:'Page', console_url:'str', username:'str', password:'str') -> 'any_':
    """ Submits the sign-in form with the given credentials and returns the response to the POST itself.
    """
    _ = page.goto(console_url + Console_Login_Path)

    page.fill('#username', username)
    page.fill('#password', password)

    def is_login_post(response:'any_') -> 'bool':
        out = response.url.endswith(Console_Login_Path) and response.request.method == 'POST'
        return out

    with page.expect_response(is_login_post) as response_info:
        page.click('.console-login-button')

    out = response_info.value

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOpenAPIConsoleSecurityBadCredentials:
    """ Verifies that rejected credentials re-render the sign-in page with one fixed message
    and that the failed attempts leave no session behind.
    """

# ################################################################################################################################

    def test_bad_credentials(self, playwright_browser:'any_', zato_dashboard:'anydict') -> 'None':
        """ Submits the sign-in form with a wrong password and with a nonexistent user,
        then confirms the cookies those attempts left grant no access.
        """
        console_url = zato_dashboard['console_url']

        # A fresh context so no earlier sign-in can mask the failures
        context = playwright_browser.new_context()
        page = context.new_page()

        try:
            # A valid username with a wrong password re-renders the sign-in page with the fixed message ..
            response = _submit_login_form(page, console_url, Admin_Username, 'not.the.right.password')
            assert response.status == OK, f'Expected the form re-rendered, got {response.status}'

            error = page.wait_for_selector('.console-login-error', state='visible', timeout=5000)
            error_text = error.inner_text().strip()
            assert error_text == _Invalid_Credentials_Message, f'Unexpected error message: {error_text}'

            # .. a nonexistent username produces exactly the same outcome ..
            response = _submit_login_form(page, console_url, 'no.such.user.anywhere', 'password.whatever')
            assert response.status == OK, f'Expected the form re-rendered, got {response.status}'

            error = page.wait_for_selector('.console-login-error', state='visible', timeout=5000)
            error_text = error.inner_text().strip()
            assert error_text == _Invalid_Credentials_Message, f'Unexpected error message: {error_text}'

            # .. and whatever cookies the failed attempts left grant no access at all.
            response = context.request.get(console_url + Spec_JSON_Path)
            body = response.text()

            assert response.status == UNAUTHORIZED, f'Expected 401 from the document endpoint, got {response.status}: {body}'
            assert body == _Unauthorized_Body, f'Expected the fixed rejection body, got: {body}'

            response = context.request.get(console_url + Console_Path, max_redirects=0)
            assert response.status == FOUND, f'Expected a redirect from the console page, got {response.status}'

            location = response.headers['location']
            assert location == Console_Login_Path, f'Expected a redirect to the sign-in page, got: {location}'

        finally:
            context.close()

# ################################################################################################################################
# ################################################################################################################################
