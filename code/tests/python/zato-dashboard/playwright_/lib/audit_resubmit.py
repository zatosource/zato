# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import loads
from time import monotonic, sleep

# pytest
import pytest

# Zato
from audit_toggle import wait_for_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The endpoint of the Dashboard view the row action talks to
_Resubmit_Url_Path = '/zato/audit-log/resubmit/'

# How long to keep retrying while the connections of an exchange propagate to the server
_Propagation_Timeout = 60

# How long to wait between retries
_Retry_Sleep = 2

# How long one click may take - a resubmit blocks while the connection pool is still being built
_Response_Timeout_Ms = 60000

# How long the marker and the table have to appear
_Selector_Timeout_Ms = 10000

# ################################################################################################################################
# ################################################################################################################################

def row_selector_of_event(event_label:'str') -> 'str':
    """ Returns the selector of the audit log row showing one kind of event, by the event's
    on-screen label, which the row's role tag carries in its title - the pages these helpers
    drive are pre-filtered to a single exchange, so one kind names one row.
    """
    out = f'#audit-log-table-body tr.audit-log-row:has(.audit-log-cell-role .dashboard-tag[title="{event_label}"])'
    return out

# ################################################################################################################################

def get_resubmit_label(page:'Page', row_selector:'str') -> 'str':
    """ Returns the text of the resubmit action of one row. The text is read out of the DOM
    rather than the rendered text because a list drawn narrow drops its action column with CSS.
    """
    out = page.eval_on_selector(row_selector + ' a.audit-log-resubmit-link', 'element => element.textContent')
    return out

# ################################################################################################################################

def _is_resubmit_response(response:'any_') -> 'bool':
    """ Matches the response of the resubmit view.
    """
    out = _Resubmit_Url_Path in response.url
    return out

# ################################################################################################################################

def click_resubmit(page:'Page', row_selector:'str') -> 'anydict | None':
    """ Clicks the resubmit action of one row and returns the parsed report, or None if the endpoint
    did not answer with one.
    """
    selector = row_selector + ' a.audit-log-resubmit-link'

    # The click goes through the DOM rather than the pointer because a list drawn narrow
    # drops its action column with CSS - the delegated handler fires either way.
    with page.expect_response(_is_resubmit_response, timeout=_Response_Timeout_Ms) as response_info:
        page.eval_on_selector(selector, 'element => element.click()')

    response = response_info.value

    # A non-2xx response means the invocation itself failed, e.g. the service has not deployed
    # yet - the retry loop treats it the same as a failed report.
    if response.status != 200:
        return None

    # The endpoint answers display-ready - the raw report the resubmit service produced
    # travels in the details field, as JSON for a success and as the error text otherwise.
    envelope = loads(response.text())

    if envelope['is_success']:
        out = loads(envelope['details'])
    else:
        out = {'is_ok': False, 'error': envelope['details']}

    return out

# ################################################################################################################################

def resubmit_until(page:'Page', row_selector:'str', is_done_func:'any_') -> 'anydict':
    """ Clicks the resubmit action of one row until the report satisfies the given condition,
    retrying while the configuration of the exchange propagates to the server.
    """
    deadline = monotonic() + _Propagation_Timeout

    while True:
        out = click_resubmit(page, row_selector)

        if out is not None:
            if is_done_func(out):
                break

        if monotonic() > deadline:
            pytest.fail(f'Resubmit did not reach the expected outcome in time, the last report was: {out}')

        sleep(_Retry_Sleep)

        # The report handler refreshes the table after each attempt, so wait for it to settle
        # and close the previous attempt's tooltip before clicking again.
        wait_for_table(page)
        page.keyboard.press('Escape')

    return out

# ################################################################################################################################

def wait_for_marker(page:'Page', row_selector:'str') -> 'None':
    """ Waits until the row of the original event carries the resubmitted marker - the table
    refreshes itself once the report arrives. The wait is for the marker being there rather
    than for it showing, because a list drawn narrow hides the row's badges with CSS.
    """
    selector = row_selector + ' .audit-log-resubmitted-marker'
    _ = page.wait_for_selector(selector, state='attached', timeout=_Selector_Timeout_Ms)

# ################################################################################################################################

def is_report_ok(report:'anydict') -> 'bool':
    """ Tells whether one resubmit went through.
    """
    out = report['is_ok']
    return out

# ################################################################################################################################
# ################################################################################################################################
