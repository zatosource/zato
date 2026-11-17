# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Driving the Redis screen the way a user would - navigating to it,
# filling the connection form and clicking Test or Save, waiting for the outcome to render.

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

Redis_Page_Url = '/zato/redis/'

# The checkbox fields of the form - everything else is a text input
_checkbox_fields = ('ssl', 'ssl_verify')

# ################################################################################################################################
# ################################################################################################################################

def redis_field_selector(field:'str') -> 'str':
    """ Returns the selector of one field of the Redis form, e.g. ssl_ca_file maps to #redis-ssl-ca-file.
    """
    field_id = field.replace('_', '-')

    out = f'#redis-{field_id}'
    return out

# ################################################################################################################################

def _fill_redis_form(page:'Page', values:'anydict') -> 'None':
    """ Fills the given fields of the Redis form, leaving everything else as it is.
    """
    for field, value in values.items():
        selector = redis_field_selector(field)

        if field in _checkbox_fields:
            page.set_checked(selector, value)
        else:
            page.fill(selector, str(value))

# ################################################################################################################################

def open_redis_screen(page:'Page', base_url:'str') -> 'None':
    """ Navigates to the Redis screen and waits for the form to render.
    """
    _ = page.goto(f'{base_url}{Redis_Page_Url}')
    _ = page.wait_for_selector('#redis-host', state='visible')

# ################################################################################################################################

def save_redis_connection(page:'Page', base_url:'str', values:'anydict') -> 'None':
    """ Saves the given field values of the Redis connection via the screen.
    """
    open_redis_screen(page, base_url)

    _fill_redis_form(page, values)

    page.click('.redis-save-group input[type="submit"]')

    status = cast_('any_', page.wait_for_selector('#redis-status.status-message-success', state='visible', timeout=10000))
    status_text = status.inner_text()
    assert 'OK, saved' in status_text, f'Expected "OK, saved" in status, got: {status_text}'

# ################################################################################################################################

def run_redis_test(page:'Page', base_url:'str', values:'anydict') -> 'None':
    """ Fills the Redis form with the given values and clicks Test connection, without saving.
    The caller asserts on the outcome via expect_redis_test_ok or expect_redis_test_error.
    """
    open_redis_screen(page, base_url)

    _fill_redis_form(page, values)
    page.click('.redis-test-link')

# ################################################################################################################################

def expect_redis_test_ok(page:'Page') -> 'None':
    """ Waits for the OK outcome of a connection test - the green status message
    to the left of the Test connection link.
    """
    status = cast_('any_', page.wait_for_selector('#redis-status.status-message-success', state='visible', timeout=10000))
    status_text = status.inner_text()
    assert 'Connection OK' in status_text, f'Expected "Connection OK" in status, got: {status_text}'

# ################################################################################################################################

def expect_redis_test_error(page:'Page') -> 'None':
    """ Waits for the error outcome of a connection test - a persistent tooltip
    over the Test connection link, with a Show details link to a copyable modal.
    """
    tooltip = cast_('any_', page.wait_for_selector('.tippy-content:has-text("Show details")', state='visible', timeout=10000))
    tooltip_text = tooltip.inner_text()
    assert 'Connection OK' not in tooltip_text, f'Expected an error in tooltip, got: {tooltip_text}'

# ################################################################################################################################
# ################################################################################################################################
