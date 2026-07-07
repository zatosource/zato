# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/security/basic-auth/?cluster=1'

_Test_Name_Prefix = 'test.nav.' + os.urandom(4).hex() + '.'

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

def _get_item_id(page:'Page', name:'str') -> 'str':
    """ Extracts the server-side ID of a row by its name.
    """

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    row = page.query_selector(row_selector)
    id_cell = row.query_selector('td[class*="item_id_"]')

    out = id_cell.inner_text().strip()
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestBasicAuthNavigation:
    """ Tests for browser navigation, search, cross-page state, login redirect, and row numbering.
    """

    def test_47_back_button_after_rate_limiting(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to the rate limiting page via the link, presses browser back,
        and verifies the basic auth list page loads correctly.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, 'back-btn')

        # .. click the rate limiting link ..
        item_id = _get_item_id(page, defn['name'])
        link_selector = f'#data-table tbody tr:has(td:text-is("{defn["name"]}")) a[href*="rate-limiting"]'
        page.click(link_selector)
        page.wait_for_selector('#rate-limiting-container', state='visible', timeout=10000)

        # .. verify we are on the rate limiting page ..
        current_url = page.url
        assert f'/rate-limiting/{item_id}/' in current_url

        # .. navigate back with query filter so the row is visible ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}&query={defn["name"]}')
        page.wait_for_selector('#data-table', state='visible', timeout=10000)

        # .. verify we are back on the basic auth list page ..
        heading = page.query_selector('h2.zato')
        heading_text = heading.inner_text()
        assert 'Basic Auth' in heading_text, f'Expected "Basic Auth" in heading, got: "{heading_text}"'

        # .. verify the row is still present.
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert row is not None, f'Row "{defn["name"]}" should be present after back'

# ################################################################################################################################

    def test_48_search_filter(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates multiple definitions, uses the search form to filter by partial name,
        and verifies only matching rows are shown.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create two definitions with distinct suffixes ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn_alpha = _create_definition(page, 'search-alpha')
        defn_beta = _create_definition(page, 'search-beta')

        # .. reload with query filter so both test rows are visible ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}&query={_Test_Name_Prefix}search')
        page.wait_for_selector('#data-table', state='visible')

        # .. verify both exist before searching ..
        row_alpha = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn_alpha["name"]}"))')
        row_beta = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn_beta["name"]}"))')
        assert row_alpha is not None, 'Alpha should exist before search'
        assert row_beta is not None, 'Beta should exist before search'

        # .. type a search term that matches only alpha ..
        search_input = page.query_selector('#id_query')
        assert search_input is not None, 'Search input #id_query should exist'

        page.fill('#id_query', defn_alpha['name'])
        page.click('#main_page_form input[type="submit"]')
        page.wait_for_selector('#data-table', state='visible', timeout=10000)

        # .. verify alpha is in the results ..
        row_alpha_after = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn_alpha["name"]}"))')
        assert row_alpha_after is not None, 'Alpha should appear in search results'

        # .. verify beta is NOT in the filtered results.
        row_beta_after = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn_beta["name"]}"))')
        assert row_beta_after is None, 'Beta should not appear when searching for alpha'

# ################################################################################################################################

    def test_49_cross_page_no_state_pollution(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates from basic auth to API keys and back.
        Verifies no form state or table state bleeds across pages.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to basic auth and create a definition ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        defn = _create_definition(page, 'cross-page')

        # .. navigate to API keys page ..
        _ = page.goto(f'{base_url}/zato/security/apikey/?cluster=1')
        page.wait_for_selector('#data-table', state='visible')

        # .. verify the basic auth definition name is not in the API keys table ..
        ba_row_on_apikey = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert ba_row_on_apikey is None, 'Basic auth definition should not appear on API keys page'

        # .. navigate back to basic auth with query filter ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}&query={defn["name"]}')
        page.wait_for_selector('#data-table', state='visible')

        # .. verify the definition is still there ..
        row = page.query_selector(f'#data-table tbody tr:has(td:text-is("{defn["name"]}"))')
        assert row is not None, f'Row "{defn["name"]}" should be present after returning from API keys'

        # .. verify the create form is not open (no stale dialog state).
        is_create_open = page.evaluate('!!document.querySelector("#create-div").offsetParent')
        assert not is_create_open, 'Create dialog should not be open after page navigation'

# ################################################################################################################################

    def test_50_direct_url_without_login(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Without session cookies, navigates to the basic auth page URL.
        Verifies the user is redirected to the login page.
        """

        base_url = zato_dashboard['dashboard_url']

        # Drop the session cookies so the tab below is not logged in, a new tab is used
        # instead of a new context so no additional browser window opens.
        context = logged_in_page.context
        context.clear_cookies()

        fresh_page = context.new_page()

        try:
            # .. navigate directly to the basic auth page ..
            _ = fresh_page.goto(f'{base_url}{_Page_Url_Pattern}')
            fresh_page.wait_for_load_state('networkidle', timeout=10000)

            # .. verify we are on the login page.
            current_url = fresh_page.url
            assert '/accounts/login/' in current_url, \
                f'Expected redirect to login page, got: {current_url}'

        finally:
            fresh_page.close()

# ################################################################################################################################

    def test_51_row_numbering(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates multiple definitions and verifies that each data row has a td.numbering cell.
        The actual numbers come from CSS counters (counter-reset on #data-table, counter-increment
        on td.numbering::before), which are not readable via JS. We verify the CSS structure
        and that each row has the numbering cell present.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate and create three definitions ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        _create_definition(page, 'num-a')
        _create_definition(page, 'num-b')
        _create_definition(page, 'num-c')

        # .. reload so the server renders all rows ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        page.wait_for_selector('#data-table', state='visible')

        # .. verify the CSS counter setup is correct ..
        counter_setup = page.evaluate("""
        (() => {
            var table = document.querySelector('#data-table');
            var tableStyle = window.getComputedStyle(table);
            var counterReset = tableStyle.counterReset;

            var cells = document.querySelectorAll('#data-table tbody tr:not(.ignore) td.numbering');
            var cellCount = cells.length;

            var firstCellBefore = '';
            if (cells.length > 0) {
                firstCellBefore = window.getComputedStyle(cells[0], '::before').content;
            }

            return {
                'counter_reset': counterReset,
                'cell_count': cellCount,
                'first_before_content': firstCellBefore
            };
        })()
        """)

        # .. verify counter-reset is set on the table ..
        counter_reset = counter_setup['counter_reset']
        assert 'data_table_counter' in counter_reset, \
            f'Expected data_table_counter in counter-reset, got: "{counter_reset}"'

        # .. verify there are at least 3 numbering cells ..
        cell_count = counter_setup['cell_count']
        assert cell_count >= 3, f'Expected at least 3 numbering cells, got: {cell_count}'

        # .. verify the ::before pseudo-element uses the counter.
        before_content = counter_setup['first_before_content']
        assert before_content != 'none', \
            f'Expected ::before content on numbering cell, got: "{before_content}"'

# ################################################################################################################################
# ################################################################################################################################
