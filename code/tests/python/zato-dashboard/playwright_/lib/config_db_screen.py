# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Driving the Config DB screens the way a user would - navigating to them, filling
# the connection forms and clicking Test or Save, waiting for the outcome to render.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

Sql_Page_Url = '/zato/config-db/sql/'
Redis_Page_Url = '/zato/config-db/redis/'

# The checkbox fields of both forms - everything else is a text input
_checkbox_fields = ('ssl', 'ssl_verify')

# ################################################################################################################################
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
    _ = page.wait_for_selector('#id_host', state='visible')

# ################################################################################################################################

def save_redis_connection(page:'Page', base_url:'str', values:'anydict') -> 'None':
    """ Saves the given field values of the Redis connection via the screen.
    """
    open_redis_screen(page, base_url)

    _fill_form(page, values)
    _save_form(page)

# ################################################################################################################################

def run_redis_test(page:'Page', base_url:'str', values:'anydict') -> 'None':
    """ Fills the Redis form with the given values and clicks Test, without saving.
    The caller asserts on the outcome via expect_redis_test_ok or expect_redis_test_error.
    """
    open_redis_screen(page, base_url)

    _fill_form(page, values)
    page.click('#check-button')

# ################################################################################################################################

def expect_redis_test_ok(page:'Page') -> 'None':
    """ Waits for the OK outcome of a connection test.
    """
    result = page.wait_for_selector('.test-results .result-status.ok', state='visible', timeout=10000)
    result_text = result.inner_text()
    assert result_text == 'OK', f'Expected "OK", got: {result_text}'

    message = page.inner_text('.test-results .result-message')
    assert 'Connection OK' in message, f'Expected "Connection OK" in message, got: {message}'

# ################################################################################################################################

def expect_redis_test_error(page:'Page') -> 'None':
    """ Waits for the error outcome of a connection test.
    """
    result = page.wait_for_selector('.test-results .result-status.error', state='visible', timeout=10000)
    result_text = result.inner_text()
    assert result_text == 'Error', f'Expected "Error", got: {result_text}'

# ################################################################################################################################
# ################################################################################################################################
