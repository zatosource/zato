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

_Test_Name_Prefix = 'test.pag.' + os.urandom(4).hex() + '.'

_Page_Size = 20

# ################################################################################################################################
# ################################################################################################################################

def _create_definition(page:'Page', suffix:'str') -> 'dict':
    """ Creates a basic auth definition via the UI and returns its details.
    """

    name = _Test_Name_Prefix + suffix
    username = 'user.' + name
    realm = 'realm.' + name
    password = 'password.' + os.urandom(8).hex()

    # Open the create dialog ..
    page.click('#markup .page_prompt a')
    page.wait_for_selector('#create-div', state='visible')

    # .. fill in the fields ..
    page.fill('#id_name', name)
    page.fill('#id_username', username)
    page.fill('#id_realm', realm)
    page.fill('#id_password', password)

    # .. submit and wait for the dialog to close ..
    page.click('#create-div input[type="submit"]')
    page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    # .. wait for the row to appear.
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    page.wait_for_selector(row_selector, state='visible', timeout=5000)

    out = {
        'name': name,
        'username': username,
        'realm': realm,
        'password': password,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestBasicAuthPagination:
    """ Tests for pagination controls, navigation, and search across pages.
    """

    def test_70_pagination_controls_visible(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates enough definitions to exceed page 1, reloads,
        and verifies pagination controls are present.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. count existing rows to determine how many more we need ..
        existing_rows = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        existing_count = len(existing_rows)
        needed = max(0, _Page_Size + 1 - existing_count)
        print(f'[test_70] existing_count={existing_count}, needed={needed}')

        # .. create enough definitions to exceed the page size ..
        for idx in range(needed):
            _ = _create_definition(page, f'ctrl-{idx:02d}')

        # .. reload without query filter so pagination kicks in ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. verify pagination controls exist ..
        action_panel = page.query_selector('.action-panel')
        print(f'[test_70] action_panel={action_panel}')
        assert action_panel is not None, 'Pagination action-panel should be visible with 21+ items'

        # .. verify the "Next" link is present (we are on page 1 and there are more pages).
        next_link = page.query_selector('.action-panel a:has-text("Next")')
        print(f'[test_70] next_link={next_link}')
        assert next_link is not None, 'Next page link should be present'

# ################################################################################################################################

    def test_71_pagination_navigate_to_page_2(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates enough definitions to span two pages, navigates to page 2,
        and verifies different rows are shown.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. count existing rows to determine how many more we need ..
        existing_rows = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        existing_count = len(existing_rows)
        needed = max(0, _Page_Size + 1 - existing_count)
        print(f'[test_71] existing_count={existing_count}, needed={needed}')

        # .. create enough definitions ..
        for idx in range(needed):
            _ = _create_definition(page, f'nav-{idx:02d}')

        # .. reload without query filter so pagination kicks in ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. collect page 1 names ..
        cells_page1 = page.query_selector_all('#data-table tbody tr:not(.ignore) td:nth-child(3)')
        names_page1 = []
        for cell in cells_page1:
            text = cell.inner_text().strip()
            if text:
                names_page1.append(text)

        print(f'[test_71] page 1 names count={len(names_page1)}')

        # .. click Next ..
        page.click('.action-panel a:has-text("Next")')
        page.wait_for_selector('#data-table', state='visible')
        time.sleep(0.3)

        # .. collect page 2 names ..
        cells_page2 = page.query_selector_all('#data-table tbody tr:not(.ignore) td:nth-child(3)')
        names_page2 = []
        for cell in cells_page2:
            text = cell.inner_text().strip()
            if text:
                names_page2.append(text)

        print(f'[test_71] page 2 names count={len(names_page2)}')

        # .. page 2 should have at least 1 row ..
        assert len(names_page2) >= 1, f'Page 2 should have at least 1 row, got {len(names_page2)}'

        # .. page 1 and page 2 rows must be different.
        overlap = set(names_page1) & set(names_page2)
        assert len(overlap) == 0, f'Page 1 and page 2 should have no overlap, got: {overlap}'

# ################################################################################################################################

    def test_72_search_filters_across_pages(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates definitions with a unique prefix, uses ?query= to filter,
        and verifies all matching rows appear regardless of pagination position.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        filter_prefix = _Test_Name_Prefix + 'filter'

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create 3 definitions with the filter prefix ..
        created_names = []
        for idx in range(3):
            defn = _create_definition(page, f'filter-{idx}')
            created_names.append(defn['name'])

        # .. navigate with query filter ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}&query={filter_prefix}')
        page.wait_for_selector('#data-table', state='visible')

        # .. collect all visible names ..
        cells = page.query_selector_all('#data-table tbody tr:not(.ignore) td:nth-child(3)')
        visible_names = []
        for cell in cells:
            text = cell.inner_text().strip()
            if text:
                visible_names.append(text)

        # .. all 3 created names must be in the filtered results.
        for name in created_names:
            assert name in visible_names, f'Expected "{name}" in filtered results, got: {visible_names}'

# ################################################################################################################################

    def test_73_create_then_search_finds_new_row(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a definition, then navigates with ?query= to find it,
        verifying the row is found even if it would be on page 2+.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. create a definition ..
        defn = _create_definition(page, 'search-find')

        # .. navigate with query filter to find it ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}&query={defn["name"]}')
        page.wait_for_selector('#data-table', state='visible')

        # .. verify the row is found.
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert row is not None, f'Row "{defn["name"]}" should be found via query filter'

# ################################################################################################################################

    def test_74_pagination_preserves_sort_order(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates enough definitions to span two pages, navigates to page 2,
        clicks the Name header to sort, and verifies sorting works on page 2.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. count existing rows to determine how many more we need ..
        existing_rows = page.query_selector_all('#data-table tbody tr:not(.ignore)')
        existing_count = len(existing_rows)
        needed = max(0, _Page_Size + 1 - existing_count)
        print(f'[test_74] existing_count={existing_count}, needed={needed}')

        # .. create enough definitions ..
        for idx in range(needed):
            _ = _create_definition(page, f'sort-{idx:02d}')

        # .. reload without query filter so pagination kicks in ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. click Next to go to page 2 ..
        page.click('.action-panel a:has-text("Next")')
        page.wait_for_selector('#data-table', state='visible')
        time.sleep(0.3)

        # .. click the Name column header to sort ..
        page.click('#data-table thead th:nth-child(3)')
        time.sleep(0.3)

        # .. collect names after first click ..
        cells_first = page.query_selector_all('#data-table tbody tr:not(.ignore) td:nth-child(3)')
        names_first = []
        for cell in cells_first:
            text = cell.inner_text().strip()
            if text:
                names_first.append(text)

        print(f'[test_74] names after first sort click: {names_first}')

        # .. click again to reverse ..
        page.click('#data-table thead th:nth-child(3)')
        time.sleep(0.3)

        cells_second = page.query_selector_all('#data-table tbody tr:not(.ignore) td:nth-child(3)')
        names_second = []
        for cell in cells_second:
            text = cell.inner_text().strip()
            if text:
                names_second.append(text)

        print(f'[test_74] names after second sort click: {names_second}')

        # .. the two clicks must produce different orders.
        assert names_first != names_second, \
            f'Clicking header twice on page 2 should reverse order, got same: {names_first}'

# ################################################################################################################################
# ################################################################################################################################
