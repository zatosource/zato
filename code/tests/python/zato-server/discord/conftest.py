# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
import time
from base64 import b64encode
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# pytest
import pytest

# Zato
from zato.common.api import Discord

# Live environment
from live_environment.parts import Parts, tear_down
from live_environment.quickstart import Host, ZatoEnvironment

# Live Discord
from live_discord.simulator import DiscordSimulator

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_discord.simulator import Identify, ReceivedMessage
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict, anydictnone, anylistnone, iterator_, strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Directory = Path(__file__).parent
    Services_File = Directory / '_services.py'
    Template_File = Directory / '_enmasse_template.yaml'

    # The services the tests invoke
    Send_Service = 'test.discord.send'
    Send_Direct_Service = 'test.discord.send-direct'
    Invoke_Service = 'test.discord.invoke'
    Ping_Service = 'test.discord.ping'
    Get_Connection_Service = 'test.discord.get-connection'
    Create_Connection_Service = 'test.discord.create-connection'
    Edit_Connection_Service = 'test.discord.edit-connection'
    Delete_Connection_Service = 'test.discord.delete-connection'

    # The internal services the Dashboard invokes
    Generic_Ping_Service = 'zato.generic.connection.ping'
    Generic_Invoke_Service = 'zato.generic.connection.invoke'

    # The connection of the template
    Conn_Name = 'test.discord.main'
    Default_Channel = '200000000000000001'
    Timeout = 3

    # The token the simulator accepts
    Token = 'MTAwMDAwMDAwMDAwMDAwMDAwMQ.GaBcDe.ThisIsATestTokenForTheDiscordSimulator01'

    # How long a test waits for the server to reach a state - longer than the pause between handshake attempts
    Wait_Timeout = Discord.Default.Handshake_Pause * 4
    Poll_Interval = 0.1

# ################################################################################################################################
# ################################################################################################################################

class DiscordSuite:
    """ The simulator and the server of the session, with the clients the tests use.
    """

    def __init__(self, simulator:'DiscordSimulator', zato:'ZatoEnvironment') -> 'None':
        self.simulator = simulator
        self.zato = zato
        self.client:'AdminClient' = zato.client()
        self.server_address = f'http://{Host}:{zato.server_port}'

        # The connections tests created beyond the template's, removed after each test
        self.created_connections:'strlist' = []

# ################################################################################################################################

    def send(
        self,
        content:'str',
        channel_id:'str'='',
        embeds:'anylistnone'=None,
        files:'anylistnone'=None,
        allowed_mentions:'anydictnone'=None,
        conn_name:'str'=ModuleCtx.Conn_Name,
        ) -> 'anydict':
        """ Sends one message from a service on the server. Files are pairs of a file name and bytes.
        """
        request:'anydict' = {
            'conn_name': conn_name,
            'content': content,
            'channel_id': channel_id,
        }

        if embeds is not None:
            request['embeds'] = embeds

        if allowed_mentions is not None:
            request['allowed_mentions'] = allowed_mentions

        if files is not None:
            encoded = []
            for file_name, data in files:
                encoded.append([file_name, b64encode(data).decode('ascii')])
            request['files'] = encoded

        out = self.client.invoke(ModuleCtx.Send_Service, request)
        return out

# ################################################################################################################################

    def send_direct(self, user_id:'str', content:'str', conn_name:'str'=ModuleCtx.Conn_Name) -> 'anydict':
        request = {
            'conn_name': conn_name,
            'user_id': user_id,
            'content': content,
        }
        out = self.client.invoke(ModuleCtx.Send_Direct_Service, request)
        return out

# ################################################################################################################################

    def invoke_api(self, http_method:'str', path:'str', conn_name:'str'=ModuleCtx.Conn_Name) -> 'anydict':
        request = {
            'conn_name': conn_name,
            'http_method': http_method,
            'path': path,
        }
        out = self.client.invoke(ModuleCtx.Invoke_Service, request)
        return out

# ################################################################################################################################

    def ping(self, conn_name:'str'=ModuleCtx.Conn_Name) -> 'anydict':
        out = self.client.invoke(ModuleCtx.Ping_Service, {'conn_name': conn_name})
        return out

# ################################################################################################################################

    def dashboard_ping(self, conn_name:'str'=ModuleCtx.Conn_Name) -> 'anydict':
        """ Pings a connection the way the Dashboard does, through the internal ping service.
        """
        conn_id = self.get_connection(conn_name)['id']
        out = self.client.invoke(ModuleCtx.Generic_Ping_Service, {'id': conn_id})
        return out

# ################################################################################################################################

    def dashboard_send(self, content:'str', target:'str'='', conn_name:'str'=ModuleCtx.Conn_Name) -> 'anydict':
        """ Sends a message the way the Dashboard's invoker does, through the internal invoke service.
        """
        request = {
            'conn_type': 'chat-discord',
            'conn_name': conn_name,
            'request_data': content,
            'target': target,
        }
        out = self.client.invoke(ModuleCtx.Generic_Invoke_Service, request)
        return out

# ################################################################################################################################

    def get_connection(self, conn_name:'str'=ModuleCtx.Conn_Name) -> 'anydict':
        out = self.client.invoke(ModuleCtx.Get_Connection_Service, {'conn_name': conn_name})
        return out

# ################################################################################################################################

    def create_connection(
        self,
        conn_name:'str',
        default_channel_id:'str'=ModuleCtx.Default_Channel,
        timeout:'int'=ModuleCtx.Timeout,
        token:'str'=ModuleCtx.Token,
        ) -> 'anydict':
        """ Creates a connection pointed at the simulator and remembers it for the cleanup after the test.
        """
        request = {
            'name': conn_name,
            'address': self.simulator.address,
            'timeout': timeout,
            'default_channel_id': default_channel_id,
            'token': token,
        }
        out = self.client.invoke(ModuleCtx.Create_Connection_Service, request)
        self.created_connections.append(conn_name)

        _ = self.wait_until_found(conn_name)
        return out

# ################################################################################################################################

    def edit_connection(self, changes:'anydict', conn_name:'str'=ModuleCtx.Conn_Name) -> 'anydict':
        request = {
            'conn_name': conn_name,
            'changes': changes,
        }
        out = self.client.invoke(ModuleCtx.Edit_Connection_Service, request)

        new_name = changes.get('name', conn_name)
        if new_name != conn_name:
            _ = self.wait_until_found(new_name)
            if conn_name in self.created_connections:
                self.created_connections.remove(conn_name)
                self.created_connections.append(new_name)

        return out

# ################################################################################################################################

    def delete_connection(self, conn_name:'str') -> 'anydict':
        out = self.client.invoke(ModuleCtx.Delete_Connection_Service, {'conn_name': conn_name})

        if conn_name in self.created_connections:
            self.created_connections.remove(conn_name)

        self.wait_until_gone(conn_name)
        return out

# ################################################################################################################################

    def wait_until_found(self, conn_name:'str', timeout:'float'=ModuleCtx.Wait_Timeout) -> 'anydict':
        """ Waits until the server has the connection.
        """
        deadline = time.monotonic() + timeout

        while True:
            out = self.get_connection(conn_name)

            if out['is_found']:
                return out

            if time.monotonic() > deadline:
                raise AssertionError(f'Connection {conn_name} not found within {timeout}s')

            time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

    def wait_until_gone(self, conn_name:'str', timeout:'float'=ModuleCtx.Wait_Timeout) -> 'None':
        """ Waits until the server no longer has the connection.
        """
        deadline = time.monotonic() + timeout

        while True:
            out = self.get_connection(conn_name)

            if not out['is_found']:
                return

            if time.monotonic() > deadline:
                raise AssertionError(f'Connection {conn_name} still present after {timeout}s')

            time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

    def wait_until_ready(self, conn_name:'str'=ModuleCtx.Conn_Name, timeout:'float'=ModuleCtx.Wait_Timeout) -> 'anydict':
        """ Waits until the connection's handshake has completed.
        """
        deadline = time.monotonic() + timeout

        while True:
            out = self.get_connection(conn_name)

            if out['is_found'] and out['is_ready'] and not out['stop_reason']:
                return out

            if time.monotonic() > deadline:
                raise AssertionError(f'Connection {conn_name} not ready within {timeout}s -> {out}')

            time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

    def wait_for_identifies(self, min_count:'int', timeout:'float'=ModuleCtx.Wait_Timeout) -> 'list[Identify]':
        out = self.simulator.wait_for_identifies(min_count, timeout)
        return out

# ################################################################################################################################

    def wait_for_messages(self, min_count:'int', timeout:'float'=ModuleCtx.Wait_Timeout) -> 'list[ReceivedMessage]':
        out = self.simulator.wait_for_messages(min_count, timeout)
        return out

# ################################################################################################################################

    def clean_up_connections(self) -> 'None':
        """ Deletes every connection a test created.
        """
        for conn_name in list(self.created_connections):
            _ = self.delete_connection(conn_name)

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
def discord() -> 'iterator_':
    """ The simulator and one server with the suite's connection, for the whole session.
    """
    parts = Parts()

    try:
        simulator = DiscordSimulator(ModuleCtx.Token)
        simulator.start()
        parts.add('Discord simulator', simulator.stop)

        directory = tempfile.mkdtemp(prefix='zato_discord_')
        zato = ZatoEnvironment(directory, password_prefix='test.discord')
        parts.add('Zato', zato.stop)
        zato.create()

        zato.start({})
        zato.deploy('test_discord_services.py', _read_services())

        # The enmasse import runs in a subprocess that inherits this environment
        os.environ.update(simulator.environment())
        _ = zato.import_yaml('discord.yaml', _read_template())

        suite = DiscordSuite(simulator, zato)
        _ = suite.wait_until_ready()

    # An incomplete setup stops what it started
    except BaseException:
        tear_down(parts)
        raise

    yield suite

    tear_down(parts)

# ################################################################################################################################

@pytest.fixture(autouse=True)
def clean_state(discord:'DiscordSuite') -> 'iterator_':
    """ Each test starts with a cleared simulator, with the template's connection ready and with no other connections.
    """
    discord.simulator.reset()
    _ = discord.wait_until_ready()

    yield

    discord.clean_up_connections()
    discord.simulator.reset()

# ################################################################################################################################
# ################################################################################################################################
