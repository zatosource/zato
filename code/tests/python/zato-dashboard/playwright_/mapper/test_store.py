# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Playwright
from playwright.sync_api import expect, Page

# ################################################################################################################################
# ################################################################################################################################

def test_store_assertions_all_pass(page:'Page', base_url:'str') -> 'None':
    """ The browser assertions for the store and the schema module all pass.
    """

    # Load the assertion page ..
    _ = page.goto(base_url + '/static/js/mapper/test.html')

    # .. wait until the whole run completed ..
    summary = page.locator('#assertion-summary')
    expect(summary).to_have_attribute('data-complete', 'true')

    # .. every failing assertion is listed by name in the failure message ..
    failed = summary.get_attribute('data-failed')
    failures = page.locator('li.assertion-fail').all_text_contents()
    assert failed == '0', 'Failing assertions: {}'.format(failures)

    # .. and the run must have actually asserted something.
    passed = summary.get_attribute('data-passed')
    assert passed is not None
    assert int(passed) > 0

# ################################################################################################################################
# ################################################################################################################################
