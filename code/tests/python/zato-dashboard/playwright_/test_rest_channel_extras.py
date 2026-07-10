# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import time
from http.client import OK, TOO_MANY_REQUESTS

# Zato
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from requests import Response
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

from rest_channel import create_channel, deploy_service_file, fill_channel_form, invoke_channel, invoke_until_status, \
    open_channel_page, wait_for_channel_row, wait_for_service_in_dialog

from zato.common.test.playwright_pubsub import open_create_dialog, submit_create_form

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.extras.' + rand_string() + '.'

_Echo_Service = 'demo.echo'

_Gateway_Service_Name = 'helpers.service-gateway'
_Gateway_Url_Path = '/zato/gateway/{service}'

# How many requests the rate-limited channel allows per minute in the test
_Rate_Limit_Per_Minute = 3

# How long to keep sending requests while waiting for a rate limit rule to take effect
_Rate_Limit_Wait_Timeout = 30

_Gateway_Service_Source = '''
# -*- coding: utf-8 -*-

# Zato
from zato.server.service import Service

class ServiceGateway(Service):
    """ Dispatches incoming requests to the service named in the URL path for REST channel tests.
    """

    name = 'helpers.service-gateway'

    def handle(self):
        service_name = self.request.http.params['service']
        self.response.payload = self.invoke(service_name, self.request.payload)
'''.lstrip()

# ################################################################################################################################
# ################################################################################################################################

def _invoke_until_rate_limited(server_port:'int', url_path:'str') -> 'Response':
    """ Keeps invoking a channel until a 429 arrives, which covers the propagation delay
    of freshly saved rate limiting rules. Returns the last response.
    """

    deadline = time.monotonic() + _Rate_Limit_Wait_Timeout

    while True:
        out = invoke_channel(server_port, url_path, data='{"rate": "check"}')

        # Stop as soon as the limit kicks in ..
        if out.status_code == TOO_MANY_REQUESTS:
            break

        # .. or when the deadline passes, in which case the caller's assertion fails with details.
        if time.monotonic() >= deadline:
            break

        time.sleep(0.2)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRESTChannelExtras:
    """ Tests for the invoke overlay, rate limiting and the service gateway of REST channels.
    """

# ################################################################################################################################

    def test_invoke_overlay(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Creates a channel and invokes it through the per-row Invoke overlay,
        then confirms the overlay's response matches a direct HTTP call.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'overlay'
        url_path = '/test/rest/overlay/' + rand_string()

        request_payload = {'phrase': 'Invoked through the overlay'}
        request_body = json.dumps(request_payload)

        # Create the channel ..
        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'data_format': 'json',
        })

        # .. open the Invoke overlay for its row ..
        page.evaluate(f'$.fn.zato.http_soap.invoke("{channel_id}")')
        page.wait_for_selector('#invoker-modal-overlay:not(.hidden)', state='visible', timeout=5000)

        # .. type in the request ..
        escaped = request_body.replace('\\', '\\\\').replace("'", "\\'")
        page.evaluate(f"$.fn.zato.invoker._request_pane.setValue('{escaped}')")

        # .. click Invoke ..
        page.click('#invoker-modal-invoke-button')

        # .. wait for the status line to show a result ..
        page.wait_for_function(
            '''() => {
                let status = document.querySelector("#invoker-modal-status");
                if (!status) return false;
                let text = status.textContent;
                return text && text.indexOf("Invoking") === -1 && text.trim().length > 0;
            }''',
            timeout=15000
        )

        # .. read the raw response the overlay displays ..
        overlay_response = page.evaluate('$("#invoker-modal-response-pane").data("raw-response")')

        logger.info('[test_invoke_overlay] overlay_response=%s', overlay_response)

        overlay_parsed = json.loads(overlay_response)
        assert overlay_parsed == request_payload, f'Expected the request echoed back, got: {overlay_parsed}'

        # .. and a direct HTTP call returns the same document.
        response = invoke_channel(server_port, url_path, data=request_body)
        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

        direct_parsed = response.json()
        assert direct_parsed == overlay_parsed, \
            f'Expected the overlay and direct responses to match, got: {direct_parsed} vs. {overlay_parsed}'

# ################################################################################################################################

    def test_rate_limiting(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Defines a small per-minute rate limit for the loopback address, verifies requests
        past the limit get 429, then clears the counters and verifies requests pass again.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'rate-limit'
        url_path = '/test/rest/rate-limit/' + rand_string()

        # Create the channel and confirm it responds ..
        channel_id = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'data_format': 'json',
        })

        response = invoke_channel(server_port, url_path, data='{"rate": "before"}')
        assert response.status_code == OK, f'Expected OK before rate limiting, got {response.status_code}'

        # .. open the rate limiting page for the channel ..
        _ = page.goto(f'{base_url}/zato/http-soap/rate-limiting/{channel_id}/?cluster=1')
        page.wait_for_selector('#rate-limiting-container .rate-limiting-rule', state='visible', timeout=10000)

        # .. add the loopback CIDR as a pill ..
        page.fill('.rate-limiting-pill-input', '127.0.0.0/8')
        page.press('.rate-limiting-pill-input', 'Enter')
        page.wait_for_selector('.rate-limiting-pill', state='visible', timeout=5000)

        # .. configure a generous token bucket and a tiny fixed window ..
        page.fill('[data-field="rate"]', '100')
        page.fill('[data-field="burst"]', '100')
        page.fill('[data-field="limit"]', str(_Rate_Limit_Per_Minute))
        page.select_option('[data-field="window_unit"]', 'minute')

        # .. save and wait for the confirmation ..
        page.click('.rate-limiting-save-group input[type="submit"]')
        page.wait_for_selector('#rate-limiting-status:has-text("OK, saved")', state='visible', timeout=10000)

        # .. keep sending requests until the limit kicks in ..
        response = _invoke_until_rate_limited(server_port, url_path)

        assert response.status_code == TOO_MANY_REQUESTS, \
            f'Expected TOO_MANY_REQUESTS past the limit, got {response.status_code}: {response.text}'
        assert 'Too many requests' in response.text, f'Expected "Too many requests" in the body, got: {response.text}'

        # .. the 429 tells the client when to retry ..
        retry_after = response.headers['Retry-After']
        assert retry_after, 'Expected a Retry-After header on the 429 response'

        # .. clear the counters through the page ..
        page.click('.rate-limiting-rule-header a:has-text("Clear counters")')

        # .. and requests pass again.
        response = invoke_until_status(server_port, url_path, OK, data='{"rate": "after-clear"}')
        assert response.status_code == OK, f'Expected OK after clearing counters, got {response.status_code}: {response.text}'

# ################################################################################################################################

    def test_gateway_service(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Selects the service gateway in the create dialog, verifies the JS reveals
        the gateway services textarea and rewrites the URL path, then submits and confirms
        the GW badge and a live gateway invocation.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']
        server_dir = zato_dashboard['server_dir']

        channel_name = _Test_Name_Prefix + 'gateway'

        # Hot-deploy the gateway dispatcher service ..
        service_file_path = deploy_service_file(server_dir, 'test_rest_gateway.py', _Gateway_Service_Source)

        try:
            # .. wait until it can be selected ..
            wait_for_service_in_dialog(page, base_url, _Gateway_Service_Name)

            # .. open the create dialog ..
            open_channel_page(page, base_url)
            open_create_dialog(page)

            # .. fill the name and select the gateway service ..
            fill_channel_form(page, {
                'name': channel_name,
                'service': _Gateway_Service_Name,
                'security_value': 'ZATO_NONE',
                'data_format': 'json',
            })

            # .. the JS reveals the gateway services textarea ..
            page.wait_for_selector('#gateway-service-list-row-create', state='visible', timeout=5000)

            # .. and rewrites the URL path ..
            url_path_value = page.input_value('#id_url_path')
            assert url_path_value == _Gateway_Url_Path, \
                f'Expected the URL path rewritten to "{_Gateway_Url_Path}", got: "{url_path_value}"'

            # .. allow the echo service through the gateway ..
            page.fill('#id_gateway_service_list', _Echo_Service)

            # .. submit and wait for the row ..
            submit_create_form(page)
            row = wait_for_channel_row(page, channel_name)

            # .. the GW badge is shown on the row ..
            badge = row.query_selector('span.gateway-badge')
            assert badge is not None, 'Expected a GW badge on the gateway channel row'

            # .. and a live call through the gateway reaches the echo service.
            request_body = '{"phrase": "Through the gateway"}'
            gateway_url_path = f'/zato/gateway/{_Echo_Service}'

            response = invoke_until_status(server_port, gateway_url_path, OK, data=request_body)
            assert response.status_code == OK, f'Expected OK through the gateway, got {response.status_code}: {response.text}'

            parsed = response.json()
            assert parsed == {'phrase': 'Through the gateway'}, f'Expected the request echoed back, got: {parsed}'

        finally:
            os.remove(service_file_path)

# ################################################################################################################################
# ################################################################################################################################
