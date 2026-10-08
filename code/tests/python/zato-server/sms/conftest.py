# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# pytest
import pytest

# Zato
from zato.common.api import SMS
from zato.common.util.mcp_oauth import Server_Address_Env_Key

# Live environment
from live_environment.parts import Parts, tear_down
from live_environment.quickstart import find_free_port, Host, ZatoEnvironment

# Live SMS
from live_sms.suite import SimulatorSuite

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_sms.base import SMSSimulator
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import any_, anydict, anylist, iterator_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Directory = Path(__file__).parent
    Services_File = Directory / '_services.py'
    Template_File = Directory / '_enmasse_template.yaml'

    # The service every channel points to and the services the tests drive the suite through
    Target_Service = 'test.sms.target'
    Send_Service = 'test.sms.send'
    Ping_Service = 'test.sms.ping'
    Set_Behaviour_Service = 'test.sms.set-behaviour'
    Get_Received_Service = 'test.sms.get-received'
    Clear_Service = 'test.sms.clear'

    # The internal service a scheduler job runs to poll a channel
    Poll_Service = SMS.Scheduler.Dispatch_Service

    # The connections of the template, by provider
    Outgoing_Prefix = 'test.sms.out.'
    Webhook_Prefix = 'test.sms.in.'
    Polling_Prefix = 'test.sms.poll.'

    # How long a test waits for events to reach the target
    Wait_Timeout = 15.0
    Poll_Interval = 0.1

    # How long the Redis the server uses is given to come up
    Redis_Wait_Timeout = 30.0

    # A refusal count meaning that the target refuses everything until it is told otherwise
    Refuse_Everything = -1

    # The error the target raises while it refuses
    Refused_Error_Text = 'The target refuses this event'

# ################################################################################################################################
# ################################################################################################################################

def _start_redis(port:'int') -> 'any_':
    """ Starts a throwaway Redis with no persistence in its own session and waits for its port.
    """
    command = ['redis-server', '--port', str(port), '--save', '', '--appendonly', 'no']
    out = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

    deadline = time.monotonic() + ModuleCtx.Redis_Wait_Timeout

    while time.monotonic() < deadline:
        with socket.socket() as probe:
            probe.settimeout(1)
            if probe.connect_ex((Host, port)) == 0:
                return out
        time.sleep(0.2)

    out.kill()
    raise Exception(f'Redis did not open port {port} within {ModuleCtx.Redis_Wait_Timeout}s')

# ################################################################################################################################
# ################################################################################################################################

class SMSSuite:
    """ The four simulators and the one server of the session, with what a test reaches for.
    """

    def __init__(self, simulators:'SimulatorSuite', zato:'ZatoEnvironment') -> 'None':
        self.simulators = simulators
        self.zato = zato
        self.client:'AdminClient' = zato.client()
        self.server_address = f'http://{Host}:{zato.server_port}'

# ################################################################################################################################

    def outgoing(self, provider:'str') -> 'str':
        out = ModuleCtx.Outgoing_Prefix + provider
        return out

    def webhook_channel(self, provider:'str') -> 'str':
        out = ModuleCtx.Webhook_Prefix + provider
        return out

    def polling_channel(self, provider:'str') -> 'str':
        out = ModuleCtx.Polling_Prefix + provider
        return out

# ################################################################################################################################

    def webhook_url(self, channel_name:'str') -> 'str':
        """ The address a provider's console is given for a channel, the same one the server signs callbacks over.
        """
        out = self.server_address + SMS.Webhook_Path_Prefix + channel_name
        return out

# ################################################################################################################################

    def simulator(self, provider:'str') -> 'SMSSimulator':
        out = self.simulators.by_provider(provider)
        return out

# ################################################################################################################################

    def send(self, provider:'str', to:'str', body:'str', from_:'str'='') -> 'anydict':
        """ Sends one message through the provider's outgoing connection from a service on the server.
        """
        request = {
            'conn_name': self.outgoing(provider),
            'to': to,
            'body': body,
        }

        if from_:
            request['from_'] = from_

        out = self.client.invoke(ModuleCtx.Send_Service, request)
        return out

# ################################################################################################################################

    def ping(self, provider:'str') -> 'anydict':
        out = self.client.invoke(ModuleCtx.Ping_Service, {'conn_name': self.outgoing(provider)})
        return out

# ################################################################################################################################

    def poll(self, provider:'str') -> 'None':
        """ Runs one poll of the provider's polling channel, the way the scheduler job does.
        """
        request = {SMS.Scheduler.Extra_Conn_Name: self.polling_channel(provider)}
        _ = self.client.invoke(ModuleCtx.Poll_Service, request)

# ################################################################################################################################

    def set_behaviour(self, refuse_count:'int') -> 'None':
        _ = self.client.invoke(ModuleCtx.Set_Behaviour_Service, {'refuse_count': refuse_count})

# ################################################################################################################################

    def get_received(self) -> 'anylist':
        response = self.client.invoke(ModuleCtx.Get_Received_Service, {})
        out = response['received']
        return out

# ################################################################################################################################

    def wait_for_received(self, count:'int', timeout:'float'=ModuleCtx.Wait_Timeout) -> 'anylist':
        """ Waits until the target recorded at least that many events.
        """
        deadline = time.monotonic() + timeout

        while True:
            out = self.get_received()

            if len(out) >= count:
                return out

            if time.monotonic() > deadline:
                raise AssertionError(f'Expected {count} event(s) within {timeout}s, the target has {len(out)}: {out}')

            time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

    def clear(self) -> 'None':
        _ = self.client.invoke(ModuleCtx.Clear_Service, {})

# ################################################################################################################################

    def register_callbacks(self) -> 'None':
        """ Points each simulator at its webhook channel, the way a user enters the URL in a provider's console.
        """
        for item in self.simulators.all:
            url = self.webhook_url(self.webhook_channel(item.provider))
            item.register_callback(url)

# ################################################################################################################################
# ################################################################################################################################

def _read_template() -> 'str':
    out = ModuleCtx.Template_File.read_text()
    return out

# ################################################################################################################################

def _read_services() -> 'str':
    out = ModuleCtx.Services_File.read_text()
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def sms() -> 'iterator_':
    """ The simulators, a Redis and one server with the suite's connections, for the whole session.
    """
    parts = Parts()

    try:
        simulators = SimulatorSuite()
        simulators.start()
        parts.add('SMS simulators', simulators.stop)

        # The Redis the channels remember seen events in
        redis_port = find_free_port()
        redis_process = _start_redis(redis_port)
        parts.add('redis-server', redis_process.kill)

        directory = tempfile.mkdtemp(prefix='zato_sms_')
        zato = ZatoEnvironment(directory, password_prefix='test.sms')
        parts.add('Zato', zato.stop)
        zato.create(redis_port=redis_port)

        # The server builds each channel's webhook URL from this address, which is what the simulators sign over
        server_environment = {
            Server_Address_Env_Key: f'http://{Host}:{zato.server_port}',
        }

        zato.start(server_environment)
        zato.deploy('test_sms_services.py', _read_services())

        # The enmasse import runs in a subprocess that inherits this environment
        os.environ.update(simulators.environment())
        _ = zato.import_yaml('sms.yaml', _read_template())

        suite = SMSSuite(simulators, zato)
        suite.register_callbacks()

    # A setup cut short tears down what it started
    except BaseException:
        tear_down(parts)
        raise

    yield suite

    tear_down(parts)

# ################################################################################################################################

@pytest.fixture(autouse=True)
def clean_state(sms:'SMSSuite') -> 'iterator_':
    """ Every test starts with simulators that recorded nothing and push to the webhook channels,
    and with a target that accepts everything.
    """
    sms.simulators.reset()
    sms.register_callbacks()
    sms.clear()

    yield

    sms.clear()

# ################################################################################################################################
# ################################################################################################################################
