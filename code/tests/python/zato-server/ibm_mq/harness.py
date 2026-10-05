# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import subprocess
from base64 import b64encode
from time import monotonic
from uuid import uuid4

# redis
from redis import Redis

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, anylist, strdict

# ################################################################################################################################
# ################################################################################################################################

# The repository root, four directories up from this test module
_repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # Redis streams the bridge communicates through
    Command_Stream = 'zato:queue_bridge:stream:command'
    Reply_Stream   = 'zato:queue_bridge:stream:reply'
    Request_Stream = 'zato:queue_bridge:stream:request'

    # The prefix of a channel's recv stream, the channel's id follows
    Recv_Stream_Prefix = 'zato:queue_bridge:stream:recv:'

    # Consumer group details for the reply stream, the same the server uses
    Consumer_Group = 'server'
    Consumer_Name  = 'server-0'

    # Where the bridge binary and the MQ client library live
    Bridge_Binary  = os.path.join(_repo_dir, 'code', 'bin', '_zato_queue_bridge')
    MQ_Client_Lib  = os.path.join(_repo_dir, 'lib', 'mqm', 'lib64', 'libmqm_r.so')

    # How long to wait for the bridge to request its config after starting
    Startup_Timeout = 30

    # How long to wait for a synchronous reply to a command
    Reply_Timeout = 30

    # How long to wait for a recv event to arrive
    Recv_Timeout = 30

# ################################################################################################################################
# ################################################################################################################################

class QueueBridgeHarness:
    """ Plays the Zato server's role against the queue bridge binary - it starts the bridge as a subprocess,
    answers its config request with a reload command and exchanges commands, replies and recv events with it.
    """

    def __init__(self) -> 'None':
        self.redis = Redis(decode_responses=True)
        self.process:'subprocess.Popen | None' = None
        self.request_last_id = '0-0'

        # Channel names to the recv streams the bridge publishes their messages to
        self.recv_streams:'strdict' = {}

        # Recv streams to the ID of the last event read from each
        self.recv_last_ids:'strdict' = {}

# ################################################################################################################################

    def _clean_streams(self) -> 'None':
        """ Removes the bridge streams left over from previous runs so each run starts clean.
        """
        _ = self.redis.delete(
            ModuleCtx.Command_Stream,
            ModuleCtx.Reply_Stream,
            ModuleCtx.Request_Stream,
            *self.recv_streams.values(),
        )

# ################################################################################################################################

    def _ensure_reply_group(self) -> 'None':
        """ Creates the consumer group this harness reads command replies through.
        """
        try:
            _ = self.redis.xgroup_create(ModuleCtx.Reply_Stream, ModuleCtx.Consumer_Group, id='$', mkstream=True)
        except Exception as e:
            if 'BUSYGROUP' in str(e):
                pass
            else:
                raise

# ################################################################################################################################

    def _wait_for_config_request(self) -> 'None':
        """ Blocks until the bridge asks for its configuration, which also means
        its command stream consumer group exists and commands will be delivered.
        """
        deadline = monotonic() + ModuleCtx.Startup_Timeout

        while monotonic() < deadline:
            result = cast_('anylist', self.redis.xread({ModuleCtx.Request_Stream: self.request_last_id}, count=10, block=1000))

            for _stream_name, messages in result:
                for message_id, fields in messages:
                    self.request_last_id = message_id
                    if fields['command'] == 'request_config':
                        return

        raise Exception('Queue bridge did not request its config in time')

# ################################################################################################################################

    def start(self, channels:'anylist', outgoing:'anylist') -> 'None':
        """ Starts the bridge subprocess and feeds it the given connection config.
        """
        if not os.path.exists(ModuleCtx.Bridge_Binary):
            raise Exception(f'Queue bridge binary not found at `{ModuleCtx.Bridge_Binary}`, run `make queue-bridge-build` first')

        if not os.path.exists(ModuleCtx.MQ_Client_Lib):
            raise Exception(f'IBM MQ client library not found at `{ModuleCtx.MQ_Client_Lib}`, run `make mq-client` first')

        # Each channel's messages arrive on a recv stream of its own ..
        for channel in channels:
            stream = f'{ModuleCtx.Recv_Stream_Prefix}{channel["id"]}'
            self.recv_streams[channel['name']] = stream
            self.recv_last_ids[stream] = '0-0'

        # .. start from clean streams so nothing from previous runs interferes ..
        self._clean_streams()
        self._ensure_reply_group()

        # .. start the bridge itself ..
        env = dict(os.environ)
        env['Zato_MQ_Client_Lib'] = ModuleCtx.MQ_Client_Lib
        env['Zato_Queue_Bridge_Log_Level'] = 'info'

        self.process = subprocess.Popen(
            [ModuleCtx.Bridge_Binary],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # .. wait until it asks for its config ..
        self._wait_for_config_request()

        # .. and answer with a reload command carrying the test connections.
        reply = self.invoke('reload', {'channels': channels, 'outgoing': outgoing})

        if reply['status'] != 'ok':
            raise Exception(f'Queue bridge did not accept the initial reload: {reply}')

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the bridge subprocess.
        """
        if self.process:
            self.process.terminate()
            _ = self.process.wait(timeout=10)
            self.process = None

# ################################################################################################################################

    def invoke(self, command:'str', payload:'anydictnone' = None) -> 'anydict':
        """ Sends one command to the bridge and blocks until its reply arrives.
        """
        correlation_id = uuid4().hex
        payload_json = json.dumps(payload) if payload is not None else '{}'

        _ = self.redis.xadd(ModuleCtx.Command_Stream, {
            'command': command,
            'correlation_id': correlation_id,
            'payload': payload_json,
        })

        deadline = monotonic() + ModuleCtx.Reply_Timeout

        while monotonic() < deadline:
            result = cast_('anylist', self.redis.xreadgroup(
                groupname=ModuleCtx.Consumer_Group,
                consumername=ModuleCtx.Consumer_Name,
                streams={ModuleCtx.Reply_Stream: '>'},
                count=10,
                block=1000,
            ))

            if not result:
                continue

            for _stream_name, messages in result:
                for message_id, fields in messages:
                    _ = self.redis.xack(ModuleCtx.Reply_Stream, ModuleCtx.Consumer_Group, message_id)
                    if fields['correlation_id'] == correlation_id:
                        out = {'status': fields['status'], 'data': fields['data']}
                        return out

        out = {'status': 'timeout', 'data': ''}
        return out

# ################################################################################################################################

    def ping(self, conn_name:'str') -> 'anydict':
        """ Pings a named outgoing connection through the bridge.
        """
        out = self.invoke('ping', {'conn_name': conn_name})
        return out

# ################################################################################################################################

    def send_message(self, conn_name:'str', data:'bytes') -> 'anydict':
        """ Sends a message through a named outgoing connection.
        """
        data_b64 = b64encode(data).decode('ascii')

        out = self.invoke('send_message', {'conn_name': conn_name, 'data': data_b64})
        return out

# ################################################################################################################################

    def send_reply(
        self,
        channel_name:'str',
        reply_to_queue:'str',
        reply_to_queue_manager:'str',
        message_id:'str',
        data:'bytes',
        ) -> 'anydict':
        """ Sends a reply to the reply-to queue of a message received through a channel.
        """
        data_b64 = b64encode(data).decode('ascii')
        payload = {
            'channel_name': channel_name,
            'reply_to_queue': reply_to_queue,
            'reply_to_queue_manager': reply_to_queue_manager,
            'message_id': message_id,
            'data': data_b64,
        }

        out = self.invoke('send_reply', payload)
        return out

# ################################################################################################################################

    def wait_for_recv_event(self, channel_name:'str') -> 'anydict':
        """ Blocks until the bridge publishes the next recv event of a channel and returns its fields.
        """
        stream = self.recv_streams[channel_name]
        deadline = monotonic() + ModuleCtx.Recv_Timeout

        while monotonic() < deadline:
            result = cast_('anylist', self.redis.xread({stream: self.recv_last_ids[stream]}, count=1, block=1000))

            for _stream_name, messages in result:
                for message_id, fields in messages:
                    self.recv_last_ids[stream] = message_id

                    out = dict(fields)
                    return out

        raise Exception(f'No recv event arrived from the queue bridge in time for channel `{channel_name}`')

# ################################################################################################################################
# ################################################################################################################################
