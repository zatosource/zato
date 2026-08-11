# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Driving the Config DB and Redis screens the way a user would - navigating to them,
# filling the connection forms and clicking Test or Save, waiting for the outcome to render.

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

Sql_Page_Url = '/zato/config-db/sql/'
Redis_Page_Url = '/zato/redis/'

# The checkbox fields of both forms - everything else is a text input
_checkbox_fields = ('ssl', 'ssl_verify')

# ################################################################################################################################
# ################################################################################################################################

def redis_field_selector(field:'str') -> 'str':
    """ Returns the selector of one field of the Redis form, e.g. display_name maps to #redis-display-name.
    """
    field_id = field.replace('_', '-')

    out = f'#redis-{field_id}'
    return out

# ################################################################################################################################

def _fill_form(page:'Page', values:'anydict') -> 'None':
    """ Fills the given fields of a Config DB form, leaving everything else as it is.
    """
    for field, value in values.items():

        if field in _checkbox_fields:
            page.set_checked(f'#id_{field}', value)
        else:
            page.fill(f'#id_{field}', str(value))

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

def _save_form(page:'Page') -> 'None':
    """ Clicks Save and waits for the confirmation to appear in the progress list.
    """
    page.click('#update-button')

    _ = page.wait_for_selector('#progress-configure .progress-icon.completed', state='visible', timeout=10000)

    progress_text = page.inner_text('#progress-configure .progress-text')
    assert 'Saved' in progress_text, f'Expected "Saved" in progress text, got: {progress_text}'

# ################################################################################################################################

def open_sql_screen(page:'Page', base_url:'str', database:'str') -> 'None':
    """ Navigates to the SQL screen and selects the given database.
    """
    _ = page.goto(f'{base_url}{Sql_Page_Url}')
    _ = page.wait_for_selector('#id_database', state='visible')

    _ = page.select_option('#id_database', database)

# ################################################################################################################################

def save_sql_database(page:'Page', base_url:'str', database:'str', values:'anydict') -> 'None':
    """ Saves the given field values for one of the SQL databases via the screen.
    """
    open_sql_screen(page, base_url, database)

    _fill_form(page, values)
    _save_form(page)

# ################################################################################################################################

def get_sql_form_values(page:'Page', base_url:'str', database:'str', fields:'tuple') -> 'anydict':
    """ Returns the current values of the given fields of one of the SQL databases.
    """
    open_sql_screen(page, base_url, database)

    out = {} # type: anydict

    for field in fields:
        out[field] = page.input_value(f'#id_{field}')

    return out

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
    """ Waits for the OK outcome of a connection test - a tooltip over the Test connection link.
    """
    tooltip = cast_('any_', page.wait_for_selector('.tippy-content', state='visible', timeout=10000))
    tooltip_text = tooltip.inner_text()
    assert 'Connection OK' in tooltip_text, f'Expected "Connection OK" in tooltip, got: {tooltip_text}'

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
