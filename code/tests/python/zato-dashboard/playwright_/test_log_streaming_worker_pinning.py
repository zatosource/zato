# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import time

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.playwright')

# The service IDE starts the log streaming mechanism automatically on page load
_IDE_Page_Url = '/zato/service/ide/service/demo.my-service/?cluster=1'

# A cheap page that the probe fetch requests while both IDE tabs are open
_Probe_Page_Url = '/zato/pubsub/topic/?cluster=1'

# How long the browser-side fetch may wait before it is considered starved
_Fetch_Abort_Ms = 8000

# The fetch must complete well under the abort budget when workers are free
_Max_Allowed_Seconds = 5.0

# A tiny service that is hot-deployed to make the server emit a recognizable log line
_Probe_Service_Template = """# -*- coding: utf-8 -*-

# Zato
from zato.server.service import Service

class LogStreamingProbe(Service):
    name = 'test.log-streaming.probe.{suffix}'

    def handle(self):
        self.response.payload = 'ok'
"""

# ################################################################################################################################
# ################################################################################################################################

def _open_ide(page:'any_', base_url:'str') -> 'None':
    """ Opens the service IDE and waits until the page is rendered.
    """

    _ = page.goto(f'{base_url}{_IDE_Page_Url}')
    _ = page.wait_for_selector('#invoke-service', state='visible', timeout=15000)

# ################################################################################################################################
# ################################################################################################################################

class TestLogStreamingWorkerPinning:
    """ With the service IDE open in two tabs, the dashboard must still serve further requests immediately.
    Each IDE page starts the log streaming mechanism on load, so if that mechanism pins a worker,
    two IDE tabs exhaust the two sync gunicorn workers and every other request starves.
    """

    def test_requests_are_served_while_two_ide_tabs_are_open(
        self,
        logged_in_page:'any_',
        zato_dashboard:'anydict',
        playwright_context:'any_',
        ) -> 'None':

        page_first = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Open the IDE in the first tab - this starts log streaming for tab one ..
        _open_ide(page_first, base_url)

        # .. open a second tab in the same, already logged-in context ..
        page_second = playwright_context.new_page()

        try:
            # .. and open the IDE there too - log streaming for tab two.
            _open_ide(page_second, base_url)

            # Give both log streaming connections a moment to be established
            time.sleep(2)

            # With both IDE tabs open, any further request must still be served immediately.
            # The fetch below aborts after _Fetch_Abort_Ms, which only happens if all workers are occupied.
            result = page_first.evaluate(
                '''async () => {
                    const controller = new AbortController();
                    const timer = setTimeout(() => controller.abort(), %d);
                    const start = performance.now();
                    try {
                        const response = await fetch('%s', {signal: controller.signal, cache: 'no-store'});
                        await response.text();
                        clearTimeout(timer);
                        return {ok: true, status: response.status, elapsed_ms: performance.now() - start};
                    } catch (error) {
                        clearTimeout(timer);
                        return {ok: false, error: String(error), elapsed_ms: performance.now() - start};
                    }
                }''' % (_Fetch_Abort_Ms, _Probe_Page_Url)
            )

            logger.info('two-ide-tab fetch result=%r', result)

            elapsed_seconds = result['elapsed_ms'] / 1000.0

            assert result['ok'], f'Request starved with two IDE tabs open, result: {result}'
            assert elapsed_seconds < _Max_Allowed_Seconds, f'Request took {elapsed_seconds:.3f}s, result: {result}'

        finally:
            page_second.close()

# ################################################################################################################################
# ################################################################################################################################

class TestLogStreamingDelivery:
    """ Log lines emitted by the server must reach the browser console of an open service IDE page.
    """

    def test_log_lines_reach_browser_console(
        self,
        logged_in_page:'any_',
        zato_dashboard:'anydict',
        ) -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_dir = zato_dashboard['server_dir']

        # Console lines rendered by the log streaming mechanism
        rendered_lines = [] # type: list

        def _on_console(message:'any_') -> 'None':
            rendered_lines.append(message.text)

        page.on('console', _on_console)

        try:
            # Open the IDE - its init auto-starts the poll loop and enables streaming on the server ..
            _open_ide(page, base_url)

            # .. give the enable toggle and the first polls a moment to run ..
            page.wait_for_timeout(3000)

            # .. make the server log a line we can recognize - the hot-deploy logger is one of
            # .. the streamed loggers, so deploying a service produces a streamed log line ..
            suffix = CryptoManager.generate_hex_string(16)
            service_file_name = f'log_streaming_probe_{suffix}.py'
            service_file_path = os.path.join(server_dir, 'pickup', 'incoming', 'services', service_file_name)

            with open(service_file_path, 'w') as service_file:
                _ = service_file.write(_Probe_Service_Template.format(suffix=suffix))

            # .. and wait until that line has travelled server -> Redis stream -> poll -> console.
            # .. The waiting must go through Playwright so browser console events keep being dispatched.
            deadline = time.time() + 30

            while time.time() < deadline:
                for line in rendered_lines:
                    if service_file_name in line:
                        logger.info('log line rendered in browser console: %r', line)
                        return
                page.wait_for_timeout(500)

            raise AssertionError(f'No server log line was rendered in the browser console, lines: {rendered_lines}')

        finally:
            page.remove_listener('console', _on_console)

# ################################################################################################################################
# ################################################################################################################################
