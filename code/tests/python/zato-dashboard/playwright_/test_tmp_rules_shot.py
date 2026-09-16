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

def test_shot(logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
    page = logged_in_page
    url = zato_dashboard['dashboard_url'] + '/zato/alerting/rules/config/?cluster=1'

    for _ in range(10):
        _ = page.goto(url)
        if page.locator('#alert-rules-card-soap').count():
            break
        page.wait_for_timeout(3000)

    _ = page.wait_for_selector('#alert-rules-card-soap', state='visible')
    page.click('#alert-rules-card-soap .alert-rules-param-edit[data-field="fault_codes"]')
    _ = page.wait_for_selector('#alert-rules-row-popup', state='visible')
    page.wait_for_timeout(600)
    _ = page.locator('#alert-rules-row-popup').screenshot(path='/tmp/rules_soap.png')

# ################################################################################################################################
# ################################################################################################################################
