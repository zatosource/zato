# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
from urllib.parse import quote

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.soap.client import SOAPClient
from zato.common.soap.common import SOAPFault, SOAPVersion
from zato.common.soap.message import SOAPMessage

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

from audit_log_ui import No_Events_Text, attach_diagnostics, format_diagnostics, get_row_cid, get_row_event, \
    get_row_main_text, get_row_outcome, get_row_time_text, get_rows, goto_audit_log, close_cid_overlay, \
    open_cid_overlay, open_data, search, wait_for_empty, wait_for_payload_text, wait_for_row_count, wait_for_table

from soap_channel import create_soap_channel, wait_for_channel_fixture_services
from soap_outconn import create_soap_outconn, invoke_soap_outconn_from_ide, open_soap_outconn_page, ping_soap_outconn, \
    wait_for_soap_invoker_service

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.soap.outconn.audit.' + CryptoManager.generate_hex_string(32) + '.'

# The fixture services behind the loopback channels, deployed during server boot
_Echo_Service   = 'test.soap.channel.echo'
_Faulty_Service = 'test.soap.channel.faulty'

# The SOAPAction the echo service's operation is invoked with
_Echo_SOAP_Action = 'urn:cdc:iisb:2014:connectivityTest'
_Echo_Namespace   = 'urn:cdc:iisb:2014'
_Echo_Operation   = 'connectivityTest'

_Audit_Log_URL_Prefix = '/zato/audit-log/'

_Source = 'soap-outgoing'

# How the events of one invocation read on their rows
_Event_Request_Sent_Label      = 'Request sent'
_Event_Response_Received_Label = 'Response received'

_Outcome_OK    = 'ok'
_Outcome_Error = 'error'

# The section title for the outgoing SOAP source, compared lowercase because the heading is styled with CSS
_SOAP_Outgoing_Title = 'outgoing soap audit log'

# A TCP port that nothing listens on, for connections that must fail
_Dead_Port = 1

# How long to keep retrying an invocation while a UI change propagates to the server
_Propagation_Timeout = 30

# How long to sleep between the attempts above
_Propagation_Poll_Interval = 1.0

# Log patterns produced when an invocation cannot reach its target
_Connection_Failure_Log_Patterns = ('Connection refused', 'NewConnectionError', 'Max retries exceeded', 'ConnectionError')

# Log patterns produced when a ping reaches the loopback channel - a ping is a bodiless HEAD request,
# so the SOAP channel on the other end has no envelope to parse and says so.
_Ping_Log_Patterns = ('Could not parse SOAP request', 'Malformed XML')

# ################################################################################################################################
# ################################################################################################################################

def _warm_up_channel(server_port:'int', url_path:'str', service_name:'str') -> 'None':
    """ Invokes a freshly created loopback channel directly, the way an external counterparty
    would, until it responds - so later invocations through the outgoing connection never hit
    a channel that has not propagated to the server yet. A channel of the faulty service is
    ready once it answers with its fault.
    """

    client_config = {
        'address': f'http://127.0.0.1:{server_port}{url_path}',
        'timeout': 10,
        'soap_version': SOAPVersion.V11,
        'soap_action': _Echo_SOAP_Action,
    } # type: anydict

    client = SOAPClient(client_config)

    message = SOAPMessage()
    message.namespace = _Echo_Namespace
    message.echoBack = 'channel-warm-up'

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    try:
        while time.monotonic() < deadline:
            try:
                _ = client.invoke(_Echo_Operation, message)
            except SOAPFault:

                # A fault of the faulty service proves the channel is live.
                if service_name == _Faulty_Service:
                    return
                raise
            except Exception as invoke_error:
                last_error = invoke_error
                time.sleep(_Propagation_Poll_Interval)
            else:
                return

        raise Exception(f'Channel `{url_path}` did not propagate within {_Propagation_Timeout}s, last error: {last_error!r}')
    finally:
        client.close()

# ################################################################################################################################

def _create_ready_pair(
    page:'Page',
    base_url:'str',
    server_port:'int',
    name_suffix:'str',
    service_name:'str'=_Echo_Service,
    ) -> 'anydict':
    """ Creates a loopback pair - a SOAP channel on a fixture service and an outgoing
    connection pointed back at it - with the channel warmed up so invocations through
    the connection only ever meet a live endpoint.
    """

    name = _Test_Name_Prefix + name_suffix
    url_path = '/' + name

    # The channel comes first and is warmed up before the connection points at it ..
    _ = create_soap_channel(page, base_url, name, service_name, url_path, {
        'soap_action': _Echo_SOAP_Action,
    })

    _warm_up_channel(server_port, url_path, service_name)

    # .. now the outgoing connection back at that channel.
    outconn_id = create_soap_outconn(page, base_url, name, f'http://127.0.0.1:{server_port}', {
        'url_path': url_path,
        'soap_action': _Echo_SOAP_Action,
    })

    out = {
        'id': outconn_id,
        'name': name,
        'url_path': url_path,
        'address': f'http://127.0.0.1:{server_port}{url_path}',
    }

    return out

# ################################################################################################################################

def _invoke_echo_via_outconn(page:'Page', base_url:'str', outconn_name:'str', marker:'str') -> 'None':
    """ Invokes the loopback pair once through the pre-deployed invoker service, retrying
    while the freshly created connection propagates to the server. Until then the service
    reports the connection as unknown without ever reaching the wrapper, so the one
    invocation that succeeds is also the only one that is audited.
    """

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:

        result = invoke_soap_outconn_from_ide(page, base_url, outconn_name, _Echo_Operation,
            namespace=_Echo_Namespace,
            fields={'echoBack': marker},
            response_fields=['echoed'],
        )

        if 'fields' in result:
            echoed = result['fields']['echoed']
            assert echoed == marker, f'Expected the echo back "{marker}", got: {result}'
            return

        last_error = result
        time.sleep(_Propagation_Poll_Interval)

    raise Exception(f'Could not invoke `{outconn_name}` within {_Propagation_Timeout}s, last error: {last_error}')

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPOutconnAuditLog:
    """ Live tests for the outgoing SOAP connection audit log page - each connection is
    configured through the browser and exercised by real SOAP traffic against a loopback
    channel of the same server.
    """

    def test_invoke_creates_events(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)
        wait_for_soap_invoker_service(page, base_url)

        # Create a loopback pair and invoke it once ..
        outconn = _create_ready_pair(page, base_url, server_port, 'events')
        _invoke_echo_via_outconn(page, base_url, outconn['name'], 'single-invocation')

        # .. open the audit log page for that connection ..
        goto_audit_log(page, base_url, _Source, outconn['name'])

        # .. the section title names the source, compared case-insensitively because of CSS styling ..
        title_text = page.inner_text('#detail-section-title')
        title_text = title_text.lower()
        assert title_text.startswith(_SOAP_Outgoing_Title), \
            f'Expected the title to start with "{_SOAP_Outgoing_Title}", got: "{title_text}"'

        # .. the section title pill shows the connection name, compared case-insensitively
        # .. because the pill is uppercased with CSS ..
        pill_text = page.inner_text('#detail-section-title .detail-component-pill')
        pill_text = pill_text.lower()
        assert pill_text == outconn['name'], f'Expected connection name "{outconn["name"]}" in the pill, got: "{pill_text}"'

        # .. one invocation produces exactly two events ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the newest event is the response, the older one is the request ..
        event_label = get_row_event(rows[0])
        assert event_label == _Event_Response_Received_Label, \
            f'Expected event "{_Event_Response_Received_Label}", got: "{event_label}"'

        event_label = get_row_event(rows[1])
        assert event_label == _Event_Request_Sent_Label, \
            f'Expected event "{_Event_Request_Sent_Label}", got: "{event_label}"'

        # .. both events carry the address invoked and completed fine ..
        for row in rows:

            main_text = get_row_main_text(row)
            assert outconn['address'] in main_text, \
                f'Expected the address "{outconn["address"]}" on the row, got: "{main_text}"'

            # .. the time is shown in the browser's locale format, not as a raw ISO string ..
            time_text = get_row_time_text(row)
            assert time_text != '', 'Expected a non-empty event time'
            assert '+00:00' not in time_text, f'Expected a locale-formatted time, got a raw ISO string: "{time_text}"'

            outcome = get_row_outcome(page, row)
            assert outcome == _Outcome_OK, f'Expected outcome "{_Outcome_OK}", got: "{outcome}"'

            # .. the raw envelope as it was on the wire is read in the pane's Data tab ..
            open_data(page, row)
            wait_for_payload_text(page, 'Envelope')

        # .. the request's CID opens the complete envelope, which carries the marker ..
        request_envelope = open_cid_overlay(page, rows[1])
        assert 'single-invocation' in request_envelope, \
            f'Expected the marker in the complete request, got: "{request_envelope}"'
        close_cid_overlay(page)

        # .. and so does the response's, echoed back by the loopback channel.
        response_envelope = open_cid_overlay(page, rows[0])
        assert 'single-invocation' in response_envelope, \
            f'Expected the marker in the complete response, got: "{response_envelope}"'
        close_cid_overlay(page)

# ################################################################################################################################

    def test_link_from_connection_list(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)
        wait_for_soap_invoker_service(page, base_url)

        # Create a loopback pair and invoke it once ..
        outconn = _create_ready_pair(page, base_url, server_port, 'from-list')
        _invoke_echo_via_outconn(page, base_url, outconn['name'], 'from-connection-list')

        # .. go back to the outgoing SOAP connections page ..
        open_soap_outconn_page(page, base_url)

        # .. click the audit log link in this connection's row ..
        row_selector = f'#data-table tbody tr:has(span.name-value:text-is("{outconn["name"]}"))'
        page.click(f'{row_selector} a:text-is("Audit log")')

        # .. wait for the audit log page to load ..
        page.wait_for_url(f'**{_Audit_Log_URL_Prefix}**')
        wait_for_table(page)

        # .. the URL points to the audit log page for this connection ..
        assert _Audit_Log_URL_Prefix in page.url, f'Expected an audit log URL, got: "{page.url}"'
        assert 'source=soap-outgoing' in page.url, f'Expected source=soap-outgoing in the URL, got: "{page.url}"'
        assert quote(outconn['name']) in page.url, f'Expected the connection name in the URL, got: "{page.url}"'

        # .. and the invocation's events are shown ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. carrying this invocation's marker in the complete request.
        request_envelope = open_cid_overlay(page, rows[1])
        assert 'from-connection-list' in request_envelope, \
            f'Expected the marker in the complete request, got: "{request_envelope}"'
        close_cid_overlay(page)

# ################################################################################################################################

    def test_events_share_cid_newest_first(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)
        wait_for_soap_invoker_service(page, base_url)

        # Create a loopback pair and invoke it twice, in a known order ..
        outconn = _create_ready_pair(page, base_url, server_port, 'ordering')
        _invoke_echo_via_outconn(page, base_url, outconn['name'], 'first-invocation')
        _invoke_echo_via_outconn(page, base_url, outconn['name'], 'second-invocation')

        # .. open the audit log page ..
        goto_audit_log(page, base_url, _Source, outconn['name'])

        # .. both invocations are shown, two events each ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 4, f'Expected 4 audit log rows, got {row_count}'

        # .. the newest invocation comes first - the markers travel inside the envelopes,
        # .. which only the complete messages behind the CID links reveal ..
        newest_request_envelope = open_cid_overlay(page, rows[1])
        assert 'second-invocation' in newest_request_envelope, \
            f'Expected the newest marker first, got: "{newest_request_envelope}"'
        close_cid_overlay(page)

        oldest_request_envelope = open_cid_overlay(page, rows[3])
        assert 'first-invocation' in oldest_request_envelope, \
            f'Expected the oldest marker last, got: "{oldest_request_envelope}"'
        close_cid_overlay(page)

        # .. within one invocation the response comes before the request ..
        event_label = get_row_event(rows[0])
        assert event_label == _Event_Response_Received_Label, \
            f'Expected event "{_Event_Response_Received_Label}", got: "{event_label}"'

        event_label = get_row_event(rows[1])
        assert event_label == _Event_Request_Sent_Label, \
            f'Expected event "{_Event_Request_Sent_Label}", got: "{event_label}"'

        # .. the request and response of one invocation share the same CID ..
        response_cid = get_row_cid(page, rows[0])
        request_cid = get_row_cid(page, rows[1])
        assert response_cid == request_cid, \
            f'Expected one shared CID, got: "{response_cid}" and "{request_cid}"'

        # .. and separate invocations carry separate CIDs.
        oldest_cid = get_row_cid(page, rows[3])
        assert response_cid != oldest_cid, f'Expected distinct CIDs across invocations, got: "{response_cid}" twice'

# ################################################################################################################################

    def test_search_filters_rows(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)
        wait_for_soap_invoker_service(page, base_url)

        # Record everything the browser and Django report during this test ..
        diagnostics = attach_diagnostics(page)

        # .. create a loopback pair and invoke it with three distinct markers - the echo
        # .. service sends each marker back, so both events of one call carry it ..
        outconn = _create_ready_pair(page, base_url, server_port, 'search')

        for marker in ('invoice-created', 'invoice-paid', 'invoice-cancelled'):
            _invoke_echo_via_outconn(page, base_url, outconn['name'], marker)

        # .. open the audit log page and confirm all six events are there ..
        goto_audit_log(page, base_url, _Source, outconn['name'])

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 6, f'Expected 6 audit log rows, got {row_count}'

        # .. the search runs over the complete stored envelopes, so one marker matches
        # .. its invocation's request and response ..
        search(page, 'invoice-paid')
        wait_for_row_count(page, 2, diagnostics)

        # .. and the complete request behind the CID carries the matching marker ..
        rows = get_rows(page)
        request_envelope = open_cid_overlay(page, rows[1])
        assert 'invoice-paid' in request_envelope, \
            f'Expected the matching marker in the complete request, got: "{request_envelope}"'
        close_cid_overlay(page)

        # .. a query matching nothing shows the empty placeholder ..
        search(page, 'no-such-payload-anywhere')
        wait_for_empty(page, diagnostics)

        # .. clearing the query brings all six events back ..
        search(page, '')
        wait_for_row_count(page, 6, diagnostics)

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{format_diagnostics(diagnostics)}'

# ################################################################################################################################

    def test_cid_opens_complete_message(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)
        wait_for_soap_invoker_service(page, base_url)

        # Record everything the browser and Django report during this test ..
        diagnostics = attach_diagnostics(page)

        # .. build a marker long enough that no row could ever show it whole ..
        marker_parts:'strlist' = []

        for item_index in range(20):
            marker_parts.append(f'line-{item_index}-product-test-product-{item_index}-quantity-2')

        long_marker = 'order-test-order-1-' + '-'.join(marker_parts)

        # .. create a loopback pair and invoke it with that marker ..
        outconn = _create_ready_pair(page, base_url, server_port, 'complete')
        _invoke_echo_via_outconn(page, base_url, outconn['name'], long_marker)

        # .. open the audit log page ..
        goto_audit_log(page, base_url, _Source, outconn['name'])

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the row itself carries no envelope - the message is read in the pane ..
        request_row = rows[1]
        main_text = get_row_main_text(request_row)
        assert long_marker not in main_text, f'Expected no envelope on the row, got: "{main_text}"'

        # .. while the overlay behind the request's CID holds the envelope in full.
        editor_value = open_cid_overlay(page, request_row)

        assert long_marker in editor_value, \
            f'Expected the complete marker in the overlay, got: "{editor_value}"'
        assert 'Envelope' in editor_value, \
            f'Expected the complete envelope in the overlay, got: "{editor_value}"'

        close_cid_overlay(page)

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{format_diagnostics(diagnostics)}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Connection_Failure_Log_Patterns)
    def test_error_outcome(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A connection pointing at a closed port produces a response event
        with the error outcome and the connection error's details.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_soap_invoker_service(page, base_url)

        outconn_name = _Test_Name_Prefix + 'error'
        url_path = '/' + outconn_name

        # Create a connection pointing at a port nothing listens on ..
        _ = create_soap_outconn(page, base_url, outconn_name, f'http://127.0.0.1:{_Dead_Port}', {
            'url_path': url_path,
            'soap_action': _Echo_SOAP_Action,
        })

        # .. a dead connection cannot be warmed up, so the invocation is retried until
        # .. the connection error - rather than an unknown-connection one - arrives ..
        deadline = time.monotonic() + _Propagation_Timeout
        result = {} # type: anydict

        while time.monotonic() < deadline:

            result = invoke_soap_outconn_from_ide(page, base_url, outconn_name, _Echo_Operation,
                namespace=_Echo_Namespace,
                fields={'echoBack': 'error-outcome'},
            )

            if 'error' in result and 'Connection' in result['error']:
                break

            time.sleep(_Propagation_Poll_Interval)

        logger.info('[test_error_outcome] result=%s', result)

        assert 'Connection' in result['error'], f'Expected a connection error, got: {result}'

        # .. open the audit log page ..
        goto_audit_log(page, base_url, _Source, outconn_name)

        # .. at least one invocation reached the wrapper, producing its two events ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count >= 2, f'Expected at least 2 audit log rows, got {row_count}'

        # .. the request itself was sent out fine ..
        event_label = get_row_event(rows[1])
        assert event_label == _Event_Request_Sent_Label, \
            f'Expected event "{_Event_Request_Sent_Label}", got: "{event_label}"'

        outcome = get_row_outcome(page, rows[1])
        assert outcome == _Outcome_OK, f'Expected outcome "{_Outcome_OK}", got: "{outcome}"'

        # .. while the response carries the error outcome with the connection error's details ..
        event_label = get_row_event(rows[0])
        assert event_label == _Event_Response_Received_Label, \
            f'Expected event "{_Event_Response_Received_Label}", got: "{event_label}"'

        outcome = get_row_outcome(page, rows[0])
        assert outcome == _Outcome_Error, f'Expected outcome "{_Outcome_Error}", got: "{outcome}"'

        open_data(page, rows[0])
        wait_for_payload_text(page, 'Connection')

        # .. and both events share their invocation's CID.
        response_cid = get_row_cid(page, rows[0])
        request_cid = get_row_cid(page, rows[1])
        assert response_cid == request_cid, \
            f'Expected one shared CID, got: "{response_cid}" and "{request_cid}"'

# ################################################################################################################################

    @pytest.mark.expect_log_errors('An internal detail that must never reach the wire')
    def test_fault_outcome(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A fault envelope arrives with an HTTP error status, so the response event
        carries the error outcome and the complete response shows the fault itself.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)
        wait_for_soap_invoker_service(page, base_url)

        # Create a loopback pair whose channel always answers with a Receiver fault ..
        outconn = _create_ready_pair(page, base_url, server_port, 'fault', _Faulty_Service)

        # .. invoke it, retrying while the connection propagates to the server ..
        deadline = time.monotonic() + _Propagation_Timeout
        result = {} # type: anydict

        while time.monotonic() < deadline:

            result = invoke_soap_outconn_from_ide(page, base_url, outconn['name'], _Echo_Operation,
                namespace=_Echo_Namespace,
                fields={'echoBack': 'fault-outcome'},
            )

            if 'fault_code' in result:
                break

            time.sleep(_Propagation_Poll_Interval)

        logger.info('[test_fault_outcome] result=%s', result)

        assert result['fault_code'] == 'Server', f'Expected a Server fault, got: {result}'

        # .. open the audit log page ..
        goto_audit_log(page, base_url, _Source, outconn['name'])

        # .. the faulted invocation produced its two events ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the request itself was sent out fine ..
        event_label = get_row_event(rows[1])
        assert event_label == _Event_Request_Sent_Label, \
            f'Expected event "{_Event_Request_Sent_Label}", got: "{event_label}"'

        outcome = get_row_outcome(page, rows[1])
        assert outcome == _Outcome_OK, f'Expected outcome "{_Outcome_OK}", got: "{outcome}"'

        # .. while the response carries the error outcome ..
        event_label = get_row_event(rows[0])
        assert event_label == _Event_Response_Received_Label, \
            f'Expected event "{_Event_Response_Received_Label}", got: "{event_label}"'

        outcome = get_row_outcome(page, rows[0])
        assert outcome == _Outcome_Error, f'Expected outcome "{_Outcome_Error}", got: "{outcome}"'

        # .. and the complete response is the fault envelope as it arrived on the wire.
        response_envelope = open_cid_overlay(page, rows[0])
        assert 'Fault' in response_envelope, \
            f'Expected a fault envelope in the complete response, got: "{response_envelope}"'
        close_cid_overlay(page)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Ping_Log_Patterns)
    def test_ping_not_audited(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Pings never write audit events - only actual invocations do.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)
        wait_for_soap_invoker_service(page, base_url)

        # Create a loopback pair and send real ping traffic through the connection ..
        outconn = _create_ready_pair(page, base_url, server_port, 'ping')

        open_soap_outconn_page(page, base_url)
        ping_result = ping_soap_outconn(page, outconn['name'])

        logger.info('[test_ping_not_audited] ping_result=%s', ping_result)

        # .. yet the audit log page shows no events at all ..
        goto_audit_log(page, base_url, _Source, outconn['name'])

        body_text = page.inner_text('#audit-log-table-body')
        assert No_Events_Text in body_text, f'Expected "{No_Events_Text}" after pings only, got: "{body_text}"'

        # .. while one actual invocation produces its two events.
        _invoke_echo_via_outconn(page, base_url, outconn['name'], 'after-ping')

        goto_audit_log(page, base_url, _Source, outconn['name'])

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows after one invocation, got {row_count}'

# ################################################################################################################################
# ################################################################################################################################
