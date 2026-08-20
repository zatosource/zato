# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Helpers for driving the audit log listing - the list of event rows beside the detail pane
holding the selected event, with the payload read in the pane's Data tab, the facts in its
Details tab and the complete message in the overlay behind the CID link.
"""

# stdlib
from urllib.parse import quote

# pytest
import pytest

# Playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anydictnone, anylist

# ################################################################################################################################
# ################################################################################################################################

# What the empty listing says
No_Events_Text = 'No events found'

_Audit_Log_URL_Prefix = '/zato/audit-log/'
_Poll_URL_Path        = '/zato/audit-log/poll/'

# One event is one row of the list, and everything else the event says is read in the pane
Row_Selector = '#audit-log-table-body tr.audit-log-row'

# The role tag names the event's kind in full in its title, whatever part the event plays
_Row_Role_Tag_Selector = '.audit-log-cell-role .dashboard-tag'
_Row_Main_Cell_Selector = '.audit-log-cell-main'
_Row_Time_Cell_Selector = '.audit-log-cell-time'

_Pane_Event_Selector   = '.audit-log-pane-head .audit-log-pane-event'
_Pane_Outcome_Selector = '.audit-log-pane-head .audit-log-outcome-filter'

_Data_Tab_Selector    = '.audit-log-pane-tab[data-tab="data"]'
_Details_Tab_Selector = '.audit-log-pane-tab[data-tab="details"]'

_Data_Panel_Selector    = '#audit-log-pane-panel-data'
_Details_Panel_Selector = '#audit-log-pane-panel-details .audit-log-pane-details'
_Details_CID_Selector   = '#audit-log-pane-panel-details .audit-log-cid-link'

_Payload_Text_Selector = '#audit-log-pane-payload .dashboard-payload-text'

_Overlay_Selector = '#zato-highlight-pane-overlay'

# How long to wait for the UI to settle, in milliseconds
_UI_Timeout = 10000

# ################################################################################################################################
# ################################################################################################################################

def goto_audit_log(page:'Page', base_url:'str', source:'str', object_name:'str') -> 'None':
    """ Navigates to the audit log page of one object and waits for the first page of events to load.
    """

    # Build the per-object URL ..
    encoded_name = quote(object_name)
    url = f'{base_url}{_Audit_Log_URL_Prefix}?source={source}&object_name={encoded_name}&cluster=1'

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
        timeout=_UI_Timeout)

# ################################################################################################################################

def get_rows(page:'Page') -> 'anylist':
    """ Returns all event rows currently shown in the audit log list.
    """
    out = page.query_selector_all(Row_Selector)
    return out

# ################################################################################################################################

def get_row_event(row:'any_') -> 'str':
    """ What kind of event one row says it is - the role tag carries the event's full label
    in its title, whichever part the event plays in its exchange.
    """
    tag = row.query_selector(_Row_Role_Tag_Selector)

    out = tag.get_attribute('title')
    return out

# ################################################################################################################################

def get_row_main_text(row:'any_') -> 'str':
    """ Everything one row's main cell says - the chips the row wears. The text is read through
    text_content because a narrow list hides the chips with CSS while the detail pane is open.
    """
    main_cell = row.query_selector(_Row_Main_Cell_Selector)

    out = main_cell.text_content()
    return out

# ################################################################################################################################

def get_row_time_text(row:'any_') -> 'str':
    """ When one row says its event happened, as the time cell shows it.
    """
    time_cell = row.query_selector(_Row_Time_Cell_Selector)

    out = time_cell.text_content().strip()
    return out

# ################################################################################################################################

def select_row(page:'Page', row:'any_') -> 'None':
    """ Selects one row and waits until the detail pane holds its event.
    """
    item_id = row.get_attribute('data-item-id')
    row.click()

    _ = page.wait_for_function(
        '''itemId => {
            let head = document.querySelector('.audit-log-pane-head .audit-log-pane-event');
            if (!head) return false;
            return head.innerText.trim().endsWith(' ' + itemId);
        }''',
        arg=item_id, timeout=_UI_Timeout)

# ################################################################################################################################

def open_details(page:'Page', row:'any_') -> 'None':
    """ Selects one row and opens the pane's Details tab on it.
    """
    select_row(page, row)

    page.click(_Details_Tab_Selector)
    _ = page.wait_for_selector(_Details_Panel_Selector, state='visible', timeout=_UI_Timeout)

# ################################################################################################################################

def get_details_text(page:'Page') -> 'str':
    """ Everything the pane's Details tab says about the selected event, lowercased because
    the fact labels are uppercased with CSS.
    """
    details_text = page.inner_text(_Details_Panel_Selector)

    out = details_text.lower()
    return out

# ################################################################################################################################

def get_details_value(page:'Page', label:'str') -> 'str':
    """ The value of one fact in the pane's Details tab, found by the fact's label. The value
    is read out of the DOM rather than the rendered text because the Copy and Search badges
    share the value's line, hidden only by their opacity.
    """
    out = page.evaluate(
        '''label => {
            let rows = document.querySelectorAll('#audit-log-pane-panel-details .dashboard-fact-row');
            for (const row of rows) {
                let rowLabel = row.querySelector('.dashboard-fact-row-label').textContent;
                if (rowLabel.toLowerCase() === label) {
                    return row.querySelector('.dashboard-fact-row-text').textContent.trim();
                }
            }
            return '';
        }''',
        arg=label.lower())

    return out

# ################################################################################################################################

def get_pane_cid(page:'Page') -> 'str':
    """ The CID of the selected event, read off the pane's Details tab.
    """
    out = page.inner_text(_Details_CID_Selector)
    return out

# ################################################################################################################################

def get_row_cid(page:'Page', row:'any_') -> 'str':
    """ The CID of one row's event, read by selecting the row and opening its Details tab.
    """
    open_details(page, row)

    out = get_pane_cid(page)
    return out

# ################################################################################################################################

def get_row_outcome(page:'Page', row:'any_') -> 'str':
    """ The outcome of one row's event, read off the badge in the pane's head, lowercased
    because the badge is styled with CSS.
    """
    select_row(page, row)

    _ = page.wait_for_selector(_Pane_Outcome_Selector, state='visible', timeout=_UI_Timeout)
    outcome_text = page.inner_text(_Pane_Outcome_Selector)

    out = outcome_text.strip().lower()
    return out

# ################################################################################################################################

def open_data(page:'Page', row:'any_') -> 'None':
    """ Selects one row and opens the pane's Data tab on it, which is where the event's
    payload is read in full.
    """
    select_row(page, row)

    page.click(_Data_Tab_Selector)
    _ = page.wait_for_selector(_Data_Panel_Selector, state='visible', timeout=_UI_Timeout)

# ################################################################################################################################

def wait_for_payload_text(page:'Page', text:'str', diagnostics:'anydictnone' = None) -> 'None':
    """ Waits until the payload shown in the pane's Data tab contains the given text.
    On timeout, the assertion message includes everything the browser and Django reported.
    """
    try:
        _ = page.wait_for_function(
            '''text => {
                let elements = document.querySelectorAll('#audit-log-pane-payload .dashboard-payload-text');
                for (const element of elements) {
                    if (element.textContent.includes(text)) return true;
                }
                return false;
            }''',
            arg=text, timeout=_UI_Timeout)
    except PlaywrightTimeoutError:
        payload_text = get_payload_text(page)
        details = format_diagnostics(diagnostics) if diagnostics else '(no diagnostics attached)'
        pytest.fail(f'Timed out waiting for "{text}" in the payload, the pane shows:\n{payload_text}\n\nDiagnostics:\n{details}')

# ################################################################################################################################

def get_payload_text(page:'Page') -> 'str':
    """ The payload the pane's Data tab currently shows.
    """
    out = page.inner_text(f'{_Payload_Text_Selector}:visible')
    return out

# ################################################################################################################################

def click_pane_cid(page:'Page') -> 'None':
    """ Clicks the CID link in the pane's Details tab, which opens the complete message overlay.
    """
    page.click(_Details_CID_Selector)
    _ = page.wait_for_selector(f'{_Overlay_Selector}:not(.hidden)', state='visible', timeout=_UI_Timeout)

# ################################################################################################################################

def read_overlay_text(page:'Page') -> 'str':
    """ The complete message the overlay shows, read through the Ace API because Ace
    renders only the visible part of the text into the DOM.
    """
    out = page.evaluate(
        '''() => {
            let element = document.querySelector('#zato-highlight-pane-overlay .zato-highlight-pane-editor');
            return ace.edit(element).getValue();
        }''')

    return out

# ################################################################################################################################

def open_cid_overlay(page:'Page', row:'any_') -> 'str':
    """ Opens the complete message of one row's event - the row is selected, its Details tab
    opened and the CID link clicked - and returns what the overlay shows.
    """
    open_details(page, row)
    click_pane_cid(page)

    out = read_overlay_text(page)
    return out

# ################################################################################################################################

def close_cid_overlay(page:'Page') -> 'None':
    """ Closes the complete message overlay and waits for it to disappear.
    """
    page.evaluate('$.fn.zato.highlight_pane.close_overlay()')
    _ = page.wait_for_selector(_Overlay_Selector, state='hidden', timeout=_UI_Timeout)

# ################################################################################################################################

def search(page:'Page', query:'str') -> 'None':
    """ Types a query into the audit log search form and submits it with the search button.
    """

    # Fill in the query ..
    page.fill('#audit-log-search-input', query)

    # .. and submit the form.
    page.click('#audit-log-search-form button[type="submit"]')

# ################################################################################################################################

def search_via_enter(page:'Page', query:'str') -> 'None':
    """ Types a query into the audit log search form and submits it by pressing Enter in the input.
    """

    # Fill in the query ..
    page.fill('#audit-log-search-input', query)

    # .. and submit the form by pressing Enter.
    page.press('#audit-log-search-input', 'Enter')

# ################################################################################################################################

def wait_for_row_count(page:'Page', count:'int', diagnostics:'anydictnone' = None) -> 'None':
    """ Waits until the audit log list shows exactly that many event rows - the payloads live
    in the pane rather than on the rows, so search results are awaited by row count.
    On timeout, the assertion message includes everything the browser and Django reported.
    """
    try:
        _ = page.wait_for_function(
            '''count => {
                let body = document.querySelector('#audit-log-table-body');
                if (body.querySelector('tr.detail-loading-row')) return false;
                let rows = body.querySelectorAll('tr.audit-log-row');
                return rows.length === count;
            }''',
            arg=count, timeout=_UI_Timeout)
    except PlaywrightTimeoutError:
        body_text = page.inner_text('#audit-log-table-body')
        details = format_diagnostics(diagnostics) if diagnostics else '(no diagnostics attached)'
        pytest.fail(f'Timed out waiting for {count} rows, the table shows:\n{body_text}\n\nDiagnostics:\n{details}')

# ################################################################################################################################

def wait_for_empty(page:'Page', diagnostics:'anydictnone' = None) -> 'None':
    """ Waits until the audit log list says there are no events at all.
    On timeout, the assertion message includes everything the browser and Django reported.
    """
    try:
        _ = page.wait_for_function(
            f'document.querySelector("#audit-log-table-body").innerText.includes(\'{No_Events_Text}\')',
            timeout=_UI_Timeout)
    except PlaywrightTimeoutError:
        body_text = page.inner_text('#audit-log-table-body')
        details = format_diagnostics(diagnostics) if diagnostics else '(no diagnostics attached)'
        pytest.fail(f'Timed out waiting for the empty listing, the table shows:\n{body_text}\n\nDiagnostics:\n{details}')

# ################################################################################################################################

def attach_diagnostics(page:'Page') -> 'anydict':
    """ Captures everything the browser and Django report while a test runs - console messages,
    uncaught page errors, failed requests and the full body of each poll response.
    """

    # All the captured facts go here ..
    out = {
        'console': [],
        'page_errors': [],
        'failed_requests': [],
        'poll_responses': [],
    } # type: anydict

    # .. every console message is recorded with its severity ..
    def _on_console(message:'any_') -> 'None':
        out['console'].append(f'[console.{message.type}] {message.text}')

    # .. uncaught JavaScript exceptions are recorded in full ..
    def _on_page_error(error:'any_') -> 'None':
        out['page_errors'].append(f'[pageerror] {error}')

    # .. requests that never completed are recorded with their failure reason, except for
    # .. requests aborted by navigation, e.g. the session keepalive ping, which are not errors ..
    def _on_request_failed(request:'any_') -> 'None':
        if request.failure != 'net::ERR_ABORTED':
            out['failed_requests'].append(f'[requestfailed] {request.method} {request.url} -> {request.failure}')

    # .. and each poll response is recorded with its status and body, which is what Django returned.
    def _on_response(response:'any_') -> 'None':
        if _Poll_URL_Path in response.url:
            body = response.text()
            out['poll_responses'].append(f'[poll] {response.status} {response.url} -> {body}')

    page.on('console', _on_console)
    page.on('pageerror', _on_page_error)
    page.on('requestfailed', _on_request_failed)
    page.on('response', _on_response)

    return out

# ################################################################################################################################

def format_diagnostics(diagnostics:'anydict') -> 'str':
    """ Turns the captured diagnostics into one readable block for assertion messages.
    """

    lines = [] # type: anylist

    for key in ('page_errors', 'failed_requests', 'console', 'poll_responses'):
        for entry in diagnostics[key]:
            lines.append(entry)

    out = '\n'.join(lines)
    return out

# ################################################################################################################################
# ################################################################################################################################
