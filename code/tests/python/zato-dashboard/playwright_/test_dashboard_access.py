# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from http import HTTPStatus
from urllib.parse import urlparse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page, Response
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The title of each of the two pages a login and a logout lead to
_Login_Page_Title = 'Log in - Zato'
_Main_Page_Title  = 'Hello - Zato'

# The link in the page header that logs the user out
_Logout_Link_Selector = '#logout a[href="/logout/"]'

# The links of the main menu, of which only the ones with a path of the Dashboard lead to an index page,
# the others open a submenu, run an action in the page or lead to an external site
_Menu_Link_Selector = 'nav.menu a.menu-link'
_Index_Href_Prefix = '/'

# The statuses of a response that a page loads without an error
_Status_OK = {HTTPStatus.FOUND, HTTPStatus.MOVED_PERMANENTLY, HTTPStatus.NOT_MODIFIED, HTTPStatus.OK}

# Responses whose status is not checked - by path, and by a fragment of the path
_Skip_Status_Paths = {'/favicon.ico'}
_Skip_Status_Fragment = 'zato/groups/'

# ################################################################################################################################
# ################################################################################################################################

def _get_index_paths(page:'Page', dashboard_url:'str') -> 'strlist':
    """ Returns the path, including the query string, of every index page that the main menu of the Dashboard links to.
    """
    _ = page.goto(dashboard_url + '/zato/')

    hrefs = page.eval_on_selector_all(_Menu_Link_Selector, 'links => links.map(link => link.getAttribute("href"))')

    paths = {href for href in hrefs if href.startswith(_Index_Href_Prefix)}

    out = sorted(paths)
    return out

# ################################################################################################################################

def _collect_failed_responses(page:'Page', dashboard_url:'str') -> 'anylist':
    """ Records every response of the Dashboard that the page receives with an error status and returns the list it adds them to.
    """
    out = []

    def _on_response(response:'Response') -> 'None':

        # Only the Dashboard's own responses are checked ..
        if not response.url.startswith(dashboard_url):
            return

        path = urlparse(response.url).path

        if path in _Skip_Status_Paths:
            return

        if _Skip_Status_Fragment in path:
            return

        # .. and each one with an unexpected status is recorded.
        if response.status not in _Status_OK:
            out.append(f'{response.status} {response.url}')

    page.on('response', _on_response)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDashboardAccess:
    """ The login and the logout of the Dashboard, and every index page of it loading without an error.
    """

    def test_login_logout(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A logged-in user reaches the main page, and once logged out is sent to the login page from it.
        """
        page = logged_in_page
        dashboard_url = zato_dashboard['dashboard_url']

        main_page_url = dashboard_url + '/zato/'
        login_page_url = dashboard_url + '/accounts/login/?next=/zato/'

        # The login took the user to the main page ..
        assert page.title() == _Main_Page_Title, f'Expected the main page after the login, got: {page.title()}'
        assert page.url == main_page_url, f'Expected {main_page_url} after the login, got: {page.url}'

        # .. the user logs out ..
        page.click(_Logout_Link_Selector)
        page.wait_for_url(f'{dashboard_url}/accounts/login/**')

        # .. and the main page now sends the user to the login page.
        _ = page.goto(main_page_url)

        assert page.title() == _Login_Page_Title, f'Expected the login page after the logout, got: {page.title()}'
        assert page.url == login_page_url, f'Expected {login_page_url} after the logout, got: {page.url}'

# ################################################################################################################################

    def test_index_pages(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Every index page of the main menu loads, along with everything it requests from the Dashboard, without an error.
        """
        page = logged_in_page
        dashboard_url = zato_dashboard['dashboard_url']

        paths = _get_index_paths(page, dashboard_url)
        assert paths, 'Expected the main menu to link to index pages'

        failed_responses = _collect_failed_responses(page, dashboard_url)

        for path in paths:
            logger.info('[test_index_pages] visiting %s', path)
            _ = page.goto(dashboard_url + path)

        assert not failed_responses, 'Expected no responses with an error status, got:\n' + '\n'.join(failed_responses)

# ################################################################################################################################
# ################################################################################################################################
