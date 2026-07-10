# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class PowerAutomateTestListFlows(Service):
    """ Lists all the flows through a named Power Automate connection.
    """
    name = 'test.power.automate.list-flows'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        conn = self.microsoft.power_platform[conn_name]
        result = conn.list_flows()

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class PowerAutomateTestGetFlow(Service):
    """ Returns details of a single flow.
    """
    name = 'test.power.automate.get-flow'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        flow_id = self.request.raw_request['flow_id']

        conn = self.microsoft.power_platform[conn_name]
        result = conn.get_flow(flow_id)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class PowerAutomateTestEnableFlow(Service):
    """ Turns a flow on.
    """
    name = 'test.power.automate.enable-flow'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        flow_id = self.request.raw_request['flow_id']

        conn = self.microsoft.power_platform[conn_name]
        conn.enable_flow(flow_id)

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################

class PowerAutomateTestDisableFlow(Service):
    """ Turns a flow off.
    """
    name = 'test.power.automate.disable-flow'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        flow_id = self.request.raw_request['flow_id']

        conn = self.microsoft.power_platform[conn_name]
        conn.disable_flow(flow_id)

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################

class PowerAutomateTestListRuns(Service):
    """ Returns the run history of a flow.
    """
    name = 'test.power.automate.list-runs'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        flow_id = self.request.raw_request['flow_id']

        conn = self.microsoft.power_platform[conn_name]
        result = conn.list_runs(flow_id)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class PowerAutomateTestGetRun(Service):
    """ Returns details of a single run of a flow.
    """
    name = 'test.power.automate.get-run'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        flow_id = self.request.raw_request['flow_id']
        run_id = self.request.raw_request['run_id']

        conn = self.microsoft.power_platform[conn_name]
        result = conn.get_run(flow_id, run_id)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class PowerAutomateTestCancelRun(Service):
    """ Cancels a run of a flow.
    """
    name = 'test.power.automate.cancel-run'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        flow_id = self.request.raw_request['flow_id']
        run_id = self.request.raw_request['run_id']

        conn = self.microsoft.power_platform[conn_name]
        conn.cancel_run(flow_id, run_id)

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################

class PowerAutomateTestResubmitRun(Service):
    """ Resubmits a run of a flow.
    """
    name = 'test.power.automate.resubmit-run'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        flow_id = self.request.raw_request['flow_id']
        run_id = self.request.raw_request['run_id']

        conn = self.microsoft.power_platform[conn_name]
        conn.resubmit_run(flow_id, run_id)

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################

class PowerAutomateTestGetTriggerUrl(Service):
    """ Returns the callback URL of a flow's HTTP request trigger.
    """
    name = 'test.power.automate.get-trigger-url'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        flow_id = self.request.raw_request['flow_id']

        conn = self.microsoft.power_platform[conn_name]
        result = conn.get_trigger_url(flow_id)

        self.response.payload = json.dumps({'url': result})

# ################################################################################################################################
# ################################################################################################################################

class PowerAutomateTestTrigger(Service):
    """ Runs an instant flow by sending a payload to its HTTP request trigger.
    """
    name = 'test.power.automate.trigger'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        flow_id = self.request.raw_request['flow_id']
        payload = self.request.raw_request['payload']

        conn = self.microsoft.power_platform[conn_name]
        result = conn.trigger(flow_id, payload)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class PowerAutomateTestTriggerUrl(Service):
    """ Runs an instant flow by sending a payload directly to a trigger's callback URL.
    """
    name = 'test.power.automate.trigger-url'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        url = self.request.raw_request['url']
        payload = self.request.raw_request['payload']

        conn = self.microsoft.power_platform[conn_name]
        result = conn.trigger_url(url, payload)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class PowerAutomateTestInvoke(Service):
    """ Invokes any Power Automate endpoint through the generic invoke method.
    """
    name = 'test.power.automate.invoke'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        method = self.request.raw_request['method']
        path = self.request.raw_request['path']

        conn = self.microsoft.power_platform[conn_name]
        result = conn.invoke(method, path)

        self.response.payload = json.dumps(result)

# ################################################################################################################################
# ################################################################################################################################

class PowerAutomateTestPing(Service):
    """ Pings a Power Automate connection.
    """
    name = 'test.power.automate.ping'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']

        conn = self.microsoft.power_platform[conn_name]
        conn.ping()

        self.response.payload = json.dumps({'ok': True})

# ################################################################################################################################
# ################################################################################################################################
