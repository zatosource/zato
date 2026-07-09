# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page

# ################################################################################################################################
# ################################################################################################################################

def login(page:'Page', base_url:'str', password:'str') -> 'None':
    """ Logs into the Zato dashboard as the admin user.
    """

    # Navigate to the login page ..
    login_url = f'{base_url}/accounts/login/?next=/zato/'
    _ = page.goto(login_url)

    # .. fill in credentials ..
    page.fill('input[name="username"]', 'admin')
    page.fill('input[name="password"]', password)

    # .. submit the form ..
    page.click('text=Log in')

    # .. and wait for the redirect to complete.
    page.wait_for_url(f'{base_url}/zato/')

# ################################################################################################################################
# ################################################################################################################################
