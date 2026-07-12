# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time

# Zato
from zato.common.test.playwright_pubsub import navigate_to_page, open_create_dialog_via_js

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.playwright')

_Permission_Page_Url = '/zato/pubsub/permission/?cluster=1'

# How long the browser-side fetch may wait before it is considered starved
_Fetch_Abort_Ms = 8000

# The fetch must complete well under the abort budget when workers are free
_Max_Allowed_Seconds = 5.0

# ################################################################################################################################
# ################################################################################################################################

class TestLiveFormUpdatesWorkerPinning:
    """ With two create dialogs open in two tabs, the dashboard must still serve further requests immediately.
    Each open dialog runs the live form updates mechanism, so if that mechanism pins a worker,
    two dialogs exhaust the two sync gunicorn workers and every other request starves.
    """

    def test_requests_are_served_while_two_dialogs_are_open(
        self,
        logged_in_page:'any_',
        zato_dashboard:'anydict',
        playwright_context:'any_',
        ) -> 'None':

        page_first = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Open the first create dialog - this starts live form updates for tab one ..
        navigate_to_page(page_first, base_url, _Permission_Page_Url)
        open_create_dialog_via_js(page_first, 'permission')

        # .. open a second tab in the same, already logged-in context ..
        page_second = playwright_context.new_page()

        try:
            # .. and open a second create dialog there - live form updates for tab two.
            navigate_to_page(page_second, base_url, _Permission_Page_Url)
            open_create_dialog_via_js(page_second, 'permission')

            # Give both live updates connections a moment to be established
            time.sleep(2)

            # With both dialogs open, any further request must still be served immediately.
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
                }''' % (_Fetch_Abort_Ms, _Permission_Page_Url)
            )

            logger.info('two-dialog fetch result=%r', result)

            elapsed_seconds = result['elapsed_ms'] / 1000.0

            assert result['ok'], f'Request starved with two dialogs open, result: {result}'
            assert elapsed_seconds < _Max_Allowed_Seconds, f'Request took {elapsed_seconds:.3f}s, result: {result}'

        finally:
            page_second.close()

# ################################################################################################################################
# ################################################################################################################################
