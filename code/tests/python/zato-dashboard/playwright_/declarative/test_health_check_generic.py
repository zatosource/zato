# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import socket
import time

# pytest
import pytest

# Zato
from zato.common.api import ZATO_NONE
from zato.common.audit_log.api import AuditSource
from zato.common.test import rand_string
from zato.common.test.playwright_pubsub import open_create_dialog, submit_create_form

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from audit_log_ui import get_row_event, get_row_outcome, get_rows, goto_audit_log
from declarative import Delivery_Timeout, fill_rest_invocation_tabs, fill_soap_invocation_tabs, job_row_exists
from http_test_server import HTTPTestServer
from rest_outconn import delete_outconn, edit_outconn, fill_outconn_form, get_outconn_id, open_outconn_page, \
    wait_for_outconn_row
from soap_outconn import delete_soap_outconn, fill_soap_outconn_form, get_soap_outconn_id, open_soap_outconn_page, \
    wait_for_soap_outconn_row

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.health.check.generic.' + rand_string() + '.'

# How long to sleep between the polling attempts for a health check outcome
_Poll_Interval = 1.0

# The health check every connection in this module is created with - a ping every second,
# each ping's outcome landing in the audit log under the connection's health source.
_Health_Check_Options = {
    'health_check_run_every': '1',
    'health_check_run_unit': 'second',
}

# What a ping's completing event reads as on the audit log page, and its outcomes
_Event_Response_Received_Label = 'Response received'
_Outcome_OK = 'ok'
_Outcome_Error = 'error'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def http_test_server() -> 'any_':
    """ A live recording HTTP server for the duration of a single test.
    """

    server = HTTPTestServer()
    server.start()

    yield server

    server.stop()

# ################################################################################################################################
# ################################################################################################################################

def find_closed_port() -> 'int':
    """ Returns a TCP port that was just bound and released again, so nothing listens on it.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))
        out = tcp_socket.getsockname()[1]

    return out

# ################################################################################################################################

def wait_for_health_outcome(page:'Page', base_url:'str', source:'str', conn_name:'str', outcome:'str',
    timeout:'float'=Delivery_Timeout) -> 'None':
    """ Waits until the audit log of a connection's health source holds a ping's response with the given
    outcome - a check that came back is recorded as ok, one that did not as an error naming what stopped it.
    The page is reloaded on each attempt, so the newest events are the ones read.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        goto_audit_log(page, base_url, source, conn_name)

        for row in get_rows(page):

            if get_row_event(row) != _Event_Response_Received_Label:
                continue

            if get_row_outcome(page, row) == outcome:
                logger.info('[wait_for_health_outcome] found a `%s` response of `%s` under `%s`', outcome, conn_name, source)
                return

        time.sleep(_Poll_Interval)

    raise Exception(f'No health check response with outcome `{outcome}` for `{conn_name}` arrived within {timeout}s')

# ################################################################################################################################

def create_health_checked_rest_outconn(page:'Page', base_url:'str', name:'str', host:'str', url_path:'str') -> 'str':
    """ Creates an outgoing REST connection with the module's health check and returns its ID.
    The check is a line of the Alerts tab, so this is where it is filled in.
    """

    # Navigate to the outgoing REST connections page and open the create dialog ..
    open_outconn_page(page, base_url)
    open_create_dialog(page)

    # .. fill the Config tab ..
    fill_outconn_form(page, {
        'name': name,
        'host': host,
        'url_path': url_path,
        'security_value': ZATO_NONE,
    })

    # .. fill the health check line of the Alerts tab ..
    fill_rest_invocation_tabs(page, _Health_Check_Options, 'create')

    # .. submit and wait for the row.
    submit_create_form(page)
    _ = wait_for_outconn_row(page, name)

    out = get_outconn_id(page, name)
    return out

# ################################################################################################################################

def create_health_checked_soap_outconn(page:'Page', base_url:'str', name:'str', host:'str', url_path:'str') -> 'str':
    """ Creates an outgoing SOAP connection with the module's health check and returns its ID.
    The check is a line of the Alerts tab, so this is where it is filled in.
    """

    # Navigate to the outgoing SOAP connections page and open the create dialog ..
    open_soap_outconn_page(page, base_url)
    open_create_dialog(page)

    # .. fill the base tabs ..
    fill_soap_outconn_form(page, {
        'name': name,
        'host': host,
        'url_path': url_path,
        'soap_version': '1.2',
        'security_value': ZATO_NONE,
    })

    # .. fill the health check line of the Alerts tab ..
    fill_soap_invocation_tabs(page, _Health_Check_Options, 'create')

    # .. submit and wait for the row.
    submit_create_form(page)
    _ = wait_for_soap_outconn_row(page, name)

    out = get_soap_outconn_id(page, name)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestHealthCheckGeneric:
    """ Tests for the generic scheduled health check component - one dispatch service shared by every
    connection type with a ping, each ping's outcome recorded in the audit log under the connection's
    health source, where the connection's alerts read it - proven here on outgoing REST and outgoing SOAP.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors('test.health.check.generic')
    def test_rest_health_check_ok_then_failure(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ A REST connection with a health check is pinged by the scheduler through the auto-created
        health. job and each outcome lands in the audit log under the rest-outgoing-health source -
        ok while the endpoint is up, an error once the connection points at a closed port. The
        connection's own audit log is off, and the check is recorded all the same.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'rest'
        url_path = '/test/health/generic/' + rand_string()

        http_test_server.set_response(url_path, body='{"pong": true}')

        # Create the connection against the live endpoint ..
        outconn_id = create_health_checked_rest_outconn(page, base_url, name, http_test_server.address, url_path)

        # .. the auto-created job is on the scheduler page under the health. prefix ..
        assert job_row_exists(page, base_url, 'health.' + name), f'Job "health.{name}" should exist after create'

        # .. the health source records an ok response while the endpoint answers ..
        wait_for_health_outcome(page, base_url, AuditSource.REST_Outgoing_Health, name, _Outcome_OK)

        # .. now point the connection at a closed port ..
        closed_port = find_closed_port()
        closed_address = f'http://127.0.0.1:{closed_port}'

        open_outconn_page(page, base_url)
        edit_outconn(page, outconn_id, {'host': closed_address})

        # .. and the health source records an error response once the pings are refused.
        wait_for_health_outcome(page, base_url, AuditSource.REST_Outgoing_Health, name, _Outcome_Error)

        # Clean up - the health check would otherwise keep pinging every second ..
        open_outconn_page(page, base_url)
        delete_outconn(page, outconn_id)

        # .. and the linked job is gone with the connection.
        assert not job_row_exists(page, base_url, 'health.' + name), f'Job "health.{name}" should be gone after delete'

# ################################################################################################################################

    @pytest.mark.expect_log_errors('test.health.check.generic')
    def test_soap_health_check_ok(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        soap_test_server:'any_',
        ) -> 'None':
        """ The same health check component works on an outgoing SOAP connection - the auto-created
        job pings the endpoint and the soap-outgoing-health source records ok responses, proving
        the component is generic across connection types.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        name = _Test_Name_Prefix + 'soap'
        url_path = '/health-check-generic'

        # Create the connection against the live SOAP endpoint ..
        outconn_id = create_health_checked_soap_outconn(page, base_url, name, soap_test_server.address, url_path)

        # .. the auto-created job is on the scheduler page under the health. prefix ..
        assert job_row_exists(page, base_url, 'health.' + name), f'Job "health.{name}" should exist after create'

        # .. and the health source records an ok response.
        wait_for_health_outcome(page, base_url, AuditSource.SOAP_Outgoing_Health, name, _Outcome_OK)

        # Clean up - the health check would otherwise keep pinging every second ..
        open_soap_outconn_page(page, base_url)
        delete_soap_outconn(page, outconn_id)

        # .. and the linked job is gone with the connection.
        assert not job_row_exists(page, base_url, 'health.' + name), f'Job "health.{name}" should be gone after delete'

# ################################################################################################################################
# ################################################################################################################################
