# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Page_Url_Pattern = '/zato/demo-config/'

# One card per demo config set, in the order they are rendered
_Set_Names = ['tutorial', 'hl7', 'scheduler', 'pubsub', 'kafka', 'ibm_mq']

# The scheduler set is the quickest to import and remove, so it is the one the toggle test flips
_Toggle_Set = 'scheduler'

# Importing a set runs enmasse under the hood, so a flipped slider is given time to apply itself
_Apply_Timeout_Ms = 120_000

# ################################################################################################################################
# ################################################################################################################################

def _slider_selector(set_name:'str') -> 'str':
    out = '#id_demo_config_' + set_name
    return out

# ################################################################################################################################

def _flip_and_wait(page:'Page', set_name:'str', new_state:'bool') -> 'None':
    """ Flips a set's slider and waits until the change has applied itself -
    the sliders are disabled while the request is on its way and come back
    enabled once the cards have been repainted.
    """
    selector = _slider_selector(set_name)

    _ = page.set_checked(selector, new_state)
    _ = page.wait_for_selector(f'{selector}:enabled', state='attached', timeout=_Apply_Timeout_Ms)

# ################################################################################################################################
# ################################################################################################################################

class TestDemoConfig:
    """ Tests for the Demo config screen.
    """

    def test_01_page_loads(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Navigates to the Demo config screen and verifies its structure:
        - the master slider is present
        - every set has a card with a slider, a status badge and at least one count pill
        - the page-wide help badge is present
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Navigate to the Demo config screen ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#id_demo_config_all', state='visible')

        # .. every set has a slider, a status badge and its card lists its objects ..
        for set_name in _Set_Names:

            slider = page.query_selector(_slider_selector(set_name))
            assert slider is not None, f'No slider for: {set_name}'

            status_text = page.inner_text(f'#demo-config-status-{set_name}')
            assert status_text in ('Imported', 'Not imported'), f'Unexpected status for {set_name}: {status_text}'

            pill = page.query_selector(f'#demo-config-body-{set_name} .demo-config-pill')
            assert pill is not None, f'No count pill for: {set_name}'

        # .. the pills link to the objects' own screens ..
        scheduler_pill = page.query_selector('#demo-config-body-scheduler .demo-config-pill')
        assert scheduler_pill is not None

        scheduler_pill_href = scheduler_pill.get_attribute('href')
        assert scheduler_pill_href is not None
        assert '/zato/scheduler/' in scheduler_pill_href, f'Unexpected pill link: {scheduler_pill_href}'

        # .. the HL7 set's card is called MLLP ..
        hl7_title = page.inner_text('#demo-config-card-hl7 .demo-config-set-title')
        assert hl7_title.strip() == 'MLLP', f'Expected "MLLP", got: {hl7_title}'

        # .. and the page-wide help badge is present.
        help_badge = page.query_selector('#demo-config-how-it-works')
        assert help_badge is not None, 'No help badge'

# ################################################################################################################################

    def test_02_toggle_and_restore(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Flips one set's slider, waits for the change to apply itself, verifies
        the slider shows the new state, then flips it back and verifies the original
        state comes back too - the environment ends up exactly as it was found.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        selector = _slider_selector(_Toggle_Set)

        # Navigate to the Demo config screen ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#id_demo_config_all', state='visible')

        # .. note the state the set is in now ..
        initial_state = page.is_checked(selector)

        # .. flip it - the slider applies itself ..
        _flip_and_wait(page, _Toggle_Set, not initial_state)

        # .. no error line shows up ..
        error_text = page.inner_text('#demo-config-error')
        assert error_text.strip() == '', f'Unexpected error: {error_text}'

        # .. the slider shows the state as the server reports it after the change ..
        flipped_state = page.is_checked(selector)
        assert flipped_state == (not initial_state), f'Expected {not initial_state}, got: {flipped_state}'

        # .. a reload shows the same state, so it really is what exists in the cluster ..
        _ = page.goto(f'{base_url}{_Page_Url_Pattern}')
        _ = page.wait_for_selector('#id_demo_config_all', state='visible')

        reloaded_state = page.is_checked(selector)
        assert reloaded_state == (not initial_state), f'Expected {not initial_state}, got: {reloaded_state}'

        # .. flip it back ..
        _flip_and_wait(page, _Toggle_Set, initial_state)

        # .. and the original state is back.
        restored_state = page.is_checked(selector)
        assert restored_state == initial_state, f'Expected {initial_state}, got: {restored_state}'

# ################################################################################################################################
# ################################################################################################################################
