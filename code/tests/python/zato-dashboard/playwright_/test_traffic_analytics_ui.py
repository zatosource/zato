# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import subprocess
import tempfile
from http.client import OK, UNAUTHORIZED
from urllib.parse import quote

# pytest
import pytest

# Zato
from zato.common.test import rand_string
from zato.common.test.playwright_pubsub import create_basic_auth

# ################################################################################################################################
# ################################################################################################################################

# The traffic analytics screens run over their own audit log and analytics store,
# in a directory of this session's own, so what the screens show is exactly what
# this test sent and nothing else. The variables must be set before the session
# fixture starts the server and the dashboard, both of which inherit them.
_analytics_state_dir = tempfile.mkdtemp(prefix='zato_analytics_test_')

os.environ['Zato_Audit_Log_DB_Name'] = os.path.join(_analytics_state_dir, 'audit.db')
os.environ['Zato_Analytics_DB_Name'] = os.path.join(_analytics_state_dir, 'analytics.db')

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, strlist

    # Dummy assignments to satisfy type checkers
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

from rest_channel import create_channel, invoke_channel, invoke_until_status

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.analytics.' + rand_string() + '.'

_Echo_Service = 'demo.echo'

# The screens under test
_Overview_Url = '/zato/analytics/?cluster=1&range=day'
_Channel_Url  = '/zato/analytics/channel/'
_Consumer_Url = '/zato/analytics/consumer/'

# Where the drill-down links land
_Audit_Log_Url_Prefix = '/zato/audit-log/'

# What the anonymous consumer bucket is called on the screens
_Caller_Anonymous = 'Anonymous'

# How many requests the test sends
_OK_Count         = 5
_Auth_Error_Count = 3

# How long the rollup subprocess may take at most, in seconds
_Rollup_Timeout = 60

# Log lines that failing authentication legitimately produces
_Auth_Log_Patterns = ('401 Unauthorized path_info', 'Unauthorized; path_info')

# ################################################################################################################################
# ################################################################################################################################

def _run_rollup() -> 'None':
    """ Runs the rollup CLI command the way cron would, in its own OS process,
    against the same audit log and analytics store the server and dashboard use.
    """
    zato_base = os.environ['ZATO_TEST_BASE_DIR']
    zato_bin = os.path.join(zato_base, 'code', 'bin', 'zato')

    result = subprocess.run([zato_bin, 'analytics', 'rollup'], capture_output=True, text=True, timeout=_Rollup_Timeout)

    logger.info('[rollup] returncode=%d stdout=%s stderr=%s', result.returncode, result.stdout, result.stderr)
    assert result.returncode == 0, f'Rollup failed:\nstdout: {result.stdout}\nstderr: {result.stderr}'

# ################################################################################################################################

def _wait_for_dashboard(page:'Page') -> 'None':
    """ Waits until an analytics screen has rendered its embedded data - the requests
    tile leaves its placeholder once the dashboard's init has run.
    """
    _ = page.wait_for_function('document.querySelector("#stat-requests").innerText !== "-"', timeout=10000)

# ################################################################################################################################

def _get_tile_number(page:'Page', tile_id:'str') -> 'int':
    """ Reads one stat tile as a number, undoing the thousands separators of its display form.
    """
    text = page.inner_text(f'#{tile_id}')
    text = text.replace(',', '')
    text = text.replace(' ', '')

    out = int(text)
    return out

# ################################################################################################################################

def _get_table_row(page:'Page', table_body_id:'str', name:'str') -> 'anydict':
    """ Returns one table row's cells keyed by position, found by the name in its first cell.
    """
    row_selector = f'#{table_body_id} tr:has(a:text-is("{name}"))'
    row = page.wait_for_selector(row_selector, state='attached', timeout=10000)
    assert row is not None, f'Expected a row for `{name}` in `{table_body_id}`'

    cells = [] # type: strlist

    for cell in row.query_selector_all('td'):
        cells.append(cell.inner_text().strip())

    out = {
        'cells': cells,
        'row': row,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestTrafficAnalyticsUI:
    """ Live tests of the four traffic analytics screens, over a real dynamically
    created environment - real requests through a real channel, the rollup run
    as its own process, the screens driven in the browser.
    """

    @pytest.mark.expect_log_errors(*_Auth_Log_Patterns)
    def test_traffic_analytics_end_to_end(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Create a security definition and a channel authenticating with it ..
        definition = create_basic_auth(page, base_url, _Test_Name_Prefix, 'consumer')

        channel_name = _Test_Name_Prefix + 'channel'
        url_path = '/test/analytics/' + rand_string()

        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'data_format': 'json',
            'security': f'Basic Auth/{definition["name"]}',
        })

        # .. send real traffic through the channel - successes with the credential ..
        auth = (definition['username'], definition['password'])

        response = invoke_until_status(server_port, url_path, OK, data='{"analytics":"ok"}', auth=auth)
        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

        for _ in range(_OK_Count - 1):
            response = invoke_channel(server_port, url_path, data='{"analytics":"ok"}', auth=auth)
            assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

        # .. and failing requests with credentials that never authenticate.
        wrong_auth = (definition['username'], 'invalid.' + rand_string())

        for _ in range(_Auth_Error_Count):
            response = invoke_channel(server_port, url_path, data='{"analytics":"denied"}', auth=wrong_auth)
            assert response.status_code == UNAUTHORIZED, f'Expected UNAUTHORIZED, got {response.status_code}'

        # The rollup aggregates the audit events into the analytics store,
        # running as its own OS process the way cron runs it.
        _run_rollup()

        total_count = _OK_Count + _Auth_Error_Count

        # Screen one - the overview shows the traffic. Its totals span every audited
        # channel of the environment, so the tiles are only checked for having rendered,
        # while our own numbers are asserted exactly on the rows and screens they own ..
        _ = page.goto(f'{base_url}{_Overview_Url}')
        _wait_for_dashboard(page)

        total_count_text = str(total_count)
        ok_count_text = str(_OK_Count)

        # .. the channel ranking has our channel with its full request count ..
        channel_row = _get_table_row(page, 'analytics-channels-table-body', channel_name)
        assert total_count_text in channel_row['cells'], \
            f'Expected {total_count} requests in the channel row, got: {channel_row["cells"]}'

        # .. and the consumer ranking has both the credential and the anonymous bucket.
        consumer_row = _get_table_row(page, 'analytics-consumers-table-body', definition['name'])
        assert ok_count_text in consumer_row['cells'], \
            f'Expected {_OK_Count} requests in the consumer row, got: {consumer_row["cells"]}'

        _ = _get_table_row(page, 'analytics-consumers-table-body', _Caller_Anonymous)

        # Screen two - the channel ranking links to the per-channel screen ..
        channel_link = channel_row['row'].query_selector(f'a:text-is("{channel_name}")')
        channel_link.click()

        page.wait_for_url(f'**{_Channel_Url}**')
        _wait_for_dashboard(page)

        # .. with the channel's own totals ..
        assert _get_tile_number(page, 'stat-requests') == total_count

        # .. its consumer breakdown ..
        consumer_row = _get_table_row(page, 'analytics-consumers-table-body', definition['name'])
        assert ok_count_text in consumer_row['cells'], \
            f'Expected {_OK_Count} requests in the consumer row, got: {consumer_row["cells"]}'

        # .. and the error-source split attributing every failure to authentication.
        expected_auth_errors = str(_Auth_Error_Count)
        auth_errors_text = page.inner_text(
            '#analytics-error-sources-table-body tr:has(td:text-is("Authentication")) td:nth-child(2)')
        assert auth_errors_text == expected_auth_errors, \
            f'Expected {_Auth_Error_Count} auth errors, got: {auth_errors_text}'

        # The per-channel table export downloads the same rows as CSV.
        with page.expect_download() as download_info:
            page.click('#analytics-csv-pill')

        download = download_info.value
        download_path = download.path()

        with open(download_path, 'r') as csv_file:
            csv_content = csv_file.read()

        csv_lines = csv_content.splitlines()
        assert csv_lines[0] == 'consumer,requests,errors,error_rate,p95_ms,last_seen', \
            f'Unexpected CSV headers: {csv_lines[0]}'

        # The credential's own row is somewhere among the CSV lines
        expected_row_prefix = f'{definition["name"]},{_OK_Count},'

        has_credential_row = False

        for line in csv_lines:
            if line.startswith(expected_row_prefix):
                has_credential_row = True
                break

        assert has_credential_row, f'Expected the credential in the CSV, got:\n{csv_content}'

        # Screen three - the consumer page shows what the credential does ..
        encoded_consumer = quote(definition['name'])
        _ = page.goto(f'{base_url}{_Consumer_Url}?cluster=1&name={encoded_consumer}&range=day')
        _wait_for_dashboard(page)

        # .. only its own, authenticated requests count here ..
        assert _get_tile_number(page, 'stat-requests') == _OK_Count

        # .. and its channel table lists our channel with a drill-down into the audit log.
        channel_row = _get_table_row(page, 'analytics-channels-table-body', channel_name)

        # Screen four - the drill-down is the existing audit log pre-filtered
        # to this channel and this credential.
        audit_link = channel_row['row'].query_selector('a:text-is("Open")')
        audit_link.click()

        page.wait_for_url(f'**{_Audit_Log_Url_Prefix}**')

        assert 'source=rest-channel' in page.url, f'Expected source=rest-channel in the URL, got: {page.url}'
        assert quote(channel_name) in page.url, f'Expected the channel name in the URL, got: {page.url}'
        assert f'query={encoded_consumer}' in page.url, f'Expected the credential in the URL, got: {page.url}'

        # The pre-filtered audit log shows the credential's response events - the search
        # matches ext_client_id, which request events do not carry yet.
        _ = page.wait_for_function(
            '''() => {
                let body = document.querySelector('#audit-log-table-body');
                if (!body) return false;
                let rows = body.querySelectorAll('tr');
                if (!rows.length) return false;
                return !body.querySelector('tr.detail-loading-row');
            }''',
            timeout=10000)

        audit_rows = page.query_selector_all('#audit-log-table-body tr')
        audit_row_count = len(audit_rows)
        assert audit_row_count == _OK_Count, f'Expected {_OK_Count} audit log rows, got {audit_row_count}'

# ################################################################################################################################
# ################################################################################################################################
