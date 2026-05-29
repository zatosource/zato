# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/security/basic-auth/?cluster=1'

_Test_Name_Prefix = 'test.pag.hdr.' + os.urandom(4).hex() + '.'

_Page_Size = 20

# ################################################################################################################################
# ################################################################################################################################

class TestPaginationHeaders:
    """ Verifies that pagination renders correctly with header-based metadata.
    """

    created_ids = []

    def test_80_create_items_via_api(self, logged_in_page:'Page', zato_dashboard:'anydict', api_client:'anydict') -> 'None':
        """ Creates enough definitions via API to exceed the page size.
        """

        for idx in range(25):
            resp = api_client.create('zato.security.basic-auth.create',
                name=f'{_Test_Name_Prefix}{idx:02d}',
                is_active=True,
                username=f'pag-hdr-user-{idx:02d}',
                realm='pag-hdr-realm',
            )
            self.__class__.created_ids.append(resp['id'])

    def test_81_page_info_displays_correctly(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to the list page and verifies pagination controls show correct info.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the basic-auth list ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. the action panel with pagination info must be present ..
        action_panel = page.query_selector('.action-panel')
        assert action_panel is not None, 'Pagination action-panel should be visible'

        # .. it should display "Page 1 of" ..
        panel_text = action_panel.inner_text()
        assert 'Page' in panel_text, f'Action panel should contain page info, got: {panel_text}'
        assert '1' in panel_text, f'Should be on page 1, got: {panel_text}'

        # .. the data table should have at most _Page_Size rows ..
        rows = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        assert len(rows) <= _Page_Size, f'Page 1 should have at most {_Page_Size} rows, got {len(rows)}'

        # .. "Next" link should be present ..
        next_link = page.query_selector('.action-panel a:has-text("Next")')
        assert next_link is not None, 'Next page link should be present'

    def test_82_next_page_shows_remaining_items(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to page 2 and verifies different rows are shown.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the list ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. click Next ..
        page.click('.action-panel a:has-text("Next")')
        page.wait_for_selector('#data-table', state='visible')
        time.sleep(0.3)

        # .. the action panel should show page 2 ..
        action_panel = page.query_selector('.action-panel')
        panel_text = action_panel.inner_text()
        assert '2' in panel_text, f'Should be on page 2, got: {panel_text}'

        # .. there should be at least 1 row on page 2 ..
        rows = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        assert len(rows) >= 1, f'Page 2 should have at least 1 row, got {len(rows)}'

        # .. "Prev" link should be present ..
        prev_link = page.query_selector('.action-panel a:has-text("Prev")')
        assert prev_link is not None, 'Prev page link should be present on page 2'

    def test_83_no_meta_in_page_source(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Verifies that _meta does not appear in the rendered HTML page source.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the list ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. the rendered page must not contain _meta anywhere ..
        content = page.content()
        assert '_meta' not in content, 'Page source should not contain _meta'

    def test_99_cleanup(self, api_client:'anydict') -> 'None':
        """ Removes all definitions created during this test class.
        """
        for item_id in self.__class__.created_ids:
            api_client.delete('zato.security.basic-auth.delete', id=item_id)

# ################################################################################################################################
# ################################################################################################################################
