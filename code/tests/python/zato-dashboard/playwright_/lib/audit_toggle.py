# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from urllib.parse import quote

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Audit_Log_Url_Prefix = '/zato/audit-log/'

# ################################################################################################################################
# ################################################################################################################################

def goto_audit_log(page:'Page', base_url:'str', source:'str', object_name:'str') -> 'None':
    """ Navigates to the audit log page of one object and waits for the first page of events to load.
    """

    # Build the per-object URL ..
    encoded_name = quote(object_name)
    url = f'{base_url}{_Audit_Log_Url_Prefix}?source={source}&object_name={encoded_name}&cluster=1'

    # .. go there ..
    _ = page.goto(url)

    # .. and wait for the initial poll to replace the loading row.
    wait_for_table(page)

# ################################################################################################################################

def wait_for_table(page:'Page') -> 'None':
    """ Waits until the audit log table has finished loading its current page of events,
    i.e. until the table body exists, has rows and none of them is the loading placeholder.
    """
    _ = page.wait_for_function(
        '''() => {
            let body = document.querySelector('#audit-log-table-body');
            if (!body) return false;
            let rows = body.querySelectorAll('tr');
            if (!rows.length) return false;
            return !body.querySelector('tr.detail-loading-row');
        }''',
        timeout=10000)

# ################################################################################################################################

def get_audit_row_count(page:'Page', base_url:'str', source:'str', object_name:'str') -> 'int':
    """ Opens the audit log page of one object and returns how many event rows it shows.
    The empty-state placeholder is a single row saying no events were found, which counts as zero.
    """

    goto_audit_log(page, base_url, source, object_name)

    rows = page.query_selector_all('#audit-log-table-body tr')

    if len(rows) == 1:
        row_text = rows[0].inner_text()
        if 'No events found' in row_text:
            return 0

    out = len(rows)
    return out

# ################################################################################################################################

def get_checkbox_state(page:'Page', selector:'str') -> 'bool':
    """ Returns whether a checkbox is checked, read via jQuery so the state comes
    straight from the DOM regardless of the slider styling.
    """

    out = page.evaluate(f'$("{selector}").prop("checked")')
    return out

# ################################################################################################################################

def assert_checkbox_exists(page:'Page', selector:'str') -> 'None':
    """ Asserts that a checkbox of the given selector exists in the DOM.
    """

    count = page.evaluate(f'$("{selector}").length')
    assert count == 1, f'Expected exactly one element for `{selector}`, got {count}'

# ################################################################################################################################
# ################################################################################################################################
