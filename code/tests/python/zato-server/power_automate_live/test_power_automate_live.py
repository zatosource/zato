# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# PyPI
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.power_automate_live')

# The main connection with valid credentials
_conn_name = 'test.power.automate.main'

# The connection whose client secret the token endpoint rejects
_bad_credentials_conn_name = 'test.power.automate.bad-credentials'

# ################################################################################################################################
# ################################################################################################################################

class _AdminClient:
    """ Minimal admin client for invoking Zato services.
    """

    def __init__(self, base_url:'str', password:'str') -> 'None':
        self.base_url = base_url
        self.password = password

    def invoke(self, service_name:'str', payload:'anydict') -> 'anydict':
        from base64 import b64encode
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen

        url = f'{self.base_url}/zato/api/invoke/{service_name}'
        body = json.dumps(payload).encode()

        credentials = f'admin.invoke:{self.password}'
        auth = b64encode(credentials.encode()).decode()

        request = Request(url, data=body, method='POST')
        request.add_header('Authorization', f'Basic {auth}')
        request.add_header('Content-Type', 'application/json')

        try:
            with urlopen(request) as response:
                raw = response.read()
        except HTTPError as error:
            raw = error.read()
            error_text = raw.decode('utf-8', errors='replace')
            raise Exception(f'{service_name} returned HTTP {error.code}: {error_text}')

        if not raw:
            return {}

        out = json.loads(raw)
        return out

# ################################################################################################################################
# ################################################################################################################################

class TestPowerAutomateFlows:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_list_flows(self, zato_server:'anydict') -> 'None':
        """ All the flows in the environment are returned.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.power.automate.list-flows', {
            'conn_name': _conn_name,
        })

        flows = result['value']
        flow_names = {flow['name'] for flow in flows}

        assert 'flow-invoice-approval' in flow_names
        assert 'flow-customer-notifications' in flow_names

        # Check that a flow carries its full details ..
        for flow in flows:
            if flow['name'] == 'flow-invoice-approval':
                assert flow['properties']['displayName'] == 'Invoice approval'
                assert flow['properties']['state'] == 'Started'

# ################################################################################################################################

    def test_get_flow(self, zato_server:'anydict') -> 'None':
        """ A single flow is returned with its details.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.power.automate.get-flow', {
            'conn_name': _conn_name,
            'flow_id': 'flow-invoice-approval',
        })

        assert result['name'] == 'flow-invoice-approval'
        assert result['properties']['displayName'] == 'Invoice approval'

# ################################################################################################################################

    def test_get_flow_not_found(self, zato_server:'anydict') -> 'None':
        """ Asking for a flow that does not exist raises an error.
        """
        client = self._get_client(zato_server)

        with pytest.raises(Exception) as exception_info:
            _ = client.invoke('test.power.automate.get-flow', {
                'conn_name': _conn_name,
                'flow_id': 'flow-does-not-exist',
            })

        assert 'HTTP' in str(exception_info.value)

# ################################################################################################################################

    def test_enable_and_disable_flow(self, zato_server:'anydict') -> 'None':
        """ Enabling and disabling a flow changes its state.
        """
        client = self._get_client(zato_server)

        # The flow starts out stopped ..
        result = client.invoke('test.power.automate.get-flow', {
            'conn_name': _conn_name,
            'flow_id': 'flow-customer-notifications',
        })
        assert result['properties']['state'] == 'Stopped'

        # .. enable it and confirm it is started now ..
        result = client.invoke('test.power.automate.enable-flow', {
            'conn_name': _conn_name,
            'flow_id': 'flow-customer-notifications',
        })
        assert result['ok'] is True

        result = client.invoke('test.power.automate.get-flow', {
            'conn_name': _conn_name,
            'flow_id': 'flow-customer-notifications',
        })
        assert result['properties']['state'] == 'Started'

        # .. and disable it again, back to its original state.
        result = client.invoke('test.power.automate.disable-flow', {
            'conn_name': _conn_name,
            'flow_id': 'flow-customer-notifications',
        })
        assert result['ok'] is True

        result = client.invoke('test.power.automate.get-flow', {
            'conn_name': _conn_name,
            'flow_id': 'flow-customer-notifications',
        })
        assert result['properties']['state'] == 'Stopped'

# ################################################################################################################################
# ################################################################################################################################

class TestPowerAutomateRuns:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_list_runs(self, zato_server:'anydict') -> 'None':
        """ The run history of a flow is returned.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.power.automate.list-runs', {
            'conn_name': _conn_name,
            'flow_id': 'flow-invoice-approval',
        })

        runs = result['value']
        run_names = {run['name'] for run in runs}

        assert 'run-invoice-001' in run_names
        assert 'run-invoice-002' in run_names

# ################################################################################################################################

    def test_get_run(self, zato_server:'anydict') -> 'None':
        """ A single run is returned with its details.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.power.automate.get-run', {
            'conn_name': _conn_name,
            'flow_id': 'flow-invoice-approval',
            'run_id': 'run-invoice-001',
        })

        assert result['name'] == 'run-invoice-001'
        assert result['properties']['status'] == 'Succeeded'

# ################################################################################################################################

    def test_cancel_run(self, zato_server:'anydict') -> 'None':
        """ Cancelling a run changes its status to Cancelled.
        """
        client = self._get_client(zato_server)

        result = client.invoke('test.power.automate.cancel-run', {
            'conn_name': _conn_name,
            'flow_id': 'flow-invoice-approval',
            'run_id': 'run-invoice-002',
        })
        assert result['ok'] is True

        result = client.invoke('test.power.automate.get-run', {
            'conn_name': _conn_name,
            'flow_id': 'flow-invoice-approval',
            'run_id': 'run-invoice-002',
        })
        assert result['properties']['status'] == 'Cancelled'

# ################################################################################################################################

    def test_resubmit_run(self, zato_server:'anydict') -> 'None':
        """ Resubmitting a run adds a new run to the flow's history.
        """
        client = self._get_client(zato_server)

        # Count the runs before the resubmission ..
        result = client.invoke('test.power.automate.list-runs', {
            'conn_name': _conn_name,
            'flow_id': 'flow-invoice-approval',
        })
        run_count_before = len(result['value'])

        # .. resubmit one of them ..
        result = client.invoke('test.power.automate.resubmit-run', {
            'conn_name': _conn_name,
            'flow_id': 'flow-invoice-approval',
            'run_id': 'run-invoice-001',
        })
        assert result['ok'] is True

        # .. and confirm there is one more run now.
        result = client.invoke('test.power.automate.list-runs', {
            'conn_name': _conn_name,
            'flow_id': 'flow-invoice-approval',
        })
        run_count_after = len(result['value'])

        assert run_count_after == run_count_before + 1

# ################################################################################################################################
# ################################################################################################################################

class TestPowerAutomateTrigger:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_get_trigger_url(self, zato_server:'anydict') -> 'None':
        """ The callback URL of a flow's HTTP request trigger is returned.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.power.automate.get-trigger-url', {
            'conn_name': _conn_name,
            'flow_id': 'flow-invoice-approval',
        })

        url = result['url']

        assert 'flow-invoice-approval/invoke' in url
        assert 'sig=' in url

# ################################################################################################################################

    def test_trigger(self, zato_server:'anydict') -> 'None':
        """ Triggering a flow by its ID sends the payload to the flow's trigger and starts a new run.
        """
        from _power_automate_server import PowerAutomateTestHandler

        client = self._get_client(zato_server)

        payload = {'invoice_id': 'INV-2026-0042', 'amount': 1250.50}

        result = client.invoke('test.power.automate.trigger', {
            'conn_name': _conn_name,
            'flow_id': 'flow-invoice-approval',
            'payload': payload,
        })

        # A new run was started ..
        assert result['run_id'].startswith('run-new-')

        # .. and the payload arrived at the trigger unchanged.
        received = PowerAutomateTestHandler.received_trigger_payloads[-1]

        assert received['flow_id'] == 'flow-invoice-approval'
        assert received['payload'] == payload

# ################################################################################################################################

    def test_trigger_url(self, zato_server:'anydict') -> 'None':
        """ Triggering a flow directly through its callback URL works without a flow ID lookup.
        """
        from _power_automate_server import PowerAutomateTestHandler

        client = self._get_client(zato_server)

        # First, look up the callback URL ..
        result = client.invoke('test.power.automate.get-trigger-url', {
            'conn_name': _conn_name,
            'flow_id': 'flow-customer-notifications',
        })
        url = result['url']

        # .. then post a payload directly to it.
        payload = {'customer_id': 'CUST-0017', 'message': 'Welcome aboard'}

        result = client.invoke('test.power.automate.trigger-url', {
            'conn_name': _conn_name,
            'url': url,
            'payload': payload,
        })

        assert result['run_id'].startswith('run-new-')

        received = PowerAutomateTestHandler.received_trigger_payloads[-1]

        assert received['flow_id'] == 'flow-customer-notifications'
        assert received['payload'] == payload

# ################################################################################################################################
# ################################################################################################################################

class TestPowerAutomateInvoke:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_generic_invoke(self, zato_server:'anydict') -> 'None':
        """ Any endpoint can be invoked through the generic invoke method.
        """
        environment_id = zato_server['environment_id']

        client = self._get_client(zato_server)
        result = client.invoke('test.power.automate.invoke', {
            'conn_name': _conn_name,
            'method': 'GET',
            'path': f'/providers/Microsoft.ProcessSimple/environments/{environment_id}/flows',
        })

        flows = result['value']
        flow_names = {flow['name'] for flow in flows}

        assert 'flow-invoice-approval' in flow_names

# ################################################################################################################################
# ################################################################################################################################

class TestPowerAutomatePing:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_ping(self, zato_server:'anydict') -> 'None':
        """ .ping() succeeds against the live environment.
        """
        client = self._get_client(zato_server)
        result = client.invoke('test.power.automate.ping', {
            'conn_name': _conn_name,
        })

        assert result['ok'] is True

# ################################################################################################################################
# ################################################################################################################################

class TestPowerAutomateSecurity:

    def _get_client(self, zato_server:'anydict') -> '_AdminClient':
        return _AdminClient(zato_server['base_url'], zato_server['invoke_password'])

# ################################################################################################################################

    def test_bad_credentials_are_rejected(self, zato_server:'anydict') -> 'None':
        """ A connection with an invalid client secret cannot obtain a token.
        """
        client = self._get_client(zato_server)

        with pytest.raises(Exception) as exception_info:
            _ = client.invoke('test.power.automate.list-flows', {
                'conn_name': _bad_credentials_conn_name,
            })

        assert 'HTTP' in str(exception_info.value)

# ################################################################################################################################

    def test_token_refresh_after_invalidation(self, zato_server:'anydict') -> 'None':
        """ When the token a client holds is invalidated server-side, the client transparently obtains
        a new one and retries, so the caller never notices.
        """
        from _power_automate_server import PowerAutomateTestHandler

        client = self._get_client(zato_server)

        # First, make a call so the connection holds a token ..
        result = client.invoke('test.power.automate.list-flows', {
            'conn_name': _conn_name,
        })
        assert 'value' in result

        # .. now invalidate all the tokens the environment has issued ..
        PowerAutomateTestHandler.invalidate_tokens()

        # .. and confirm the next call still succeeds - the connection re-authenticated on its own.
        result = client.invoke('test.power.automate.list-flows', {
            'conn_name': _conn_name,
        })

        flows = result['value']
        flow_names = {flow['name'] for flow in flows}

        assert 'flow-invoice-approval' in flow_names

# ################################################################################################################################
# ################################################################################################################################
