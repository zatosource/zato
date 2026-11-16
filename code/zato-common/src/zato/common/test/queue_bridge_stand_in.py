# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Redis server of a live suite and a stand-in for the queue bridge, which answers each command
# that the workers of the server send through the command stream.

# stdlib
import logging
import socket
from subprocess import DEVNULL, Popen
from tempfile import mkdtemp
from threading import Event, Thread
from time import monotonic, sleep

# Redis
from redis import Redis
from redis.exceptions import RedisError

# Zato
from zato.common.typing_ import cast_
from zato.server.queue_bridge.client import ModuleCtx as ClientCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, strstrdict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Host = '127.0.0.1'

    # The variables from which the queue bridge client of each worker takes the address of its Redis server
    Env_Host = 'Zato_Queue_Bridge_Redis_Host'
    Env_Port = 'Zato_Queue_Bridge_Redis_Port'

    # The prefix of the directory of the Redis server, which the removal of the state of an interrupted run recognizes
    Directory_Prefix = 'zato_multi_cpu_redis_'

    # How long a started Redis server has to accept connections, in seconds
    Ready_Timeout = 30.0
    Ready_Sleep = 0.05

    # How long one read of the command stream blocks, in milliseconds
    Command_Block_Ms = 100

    # How many commands one read returns at most
    Command_Count = 100

    # The status of every reply, with which the client of a worker reports success
    Status_OK = 'ok'

    # How long the stand-in has to end, in seconds
    Stop_Timeout = 5.0

# ################################################################################################################################
# ################################################################################################################################

def _get_free_port() -> 'int':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((ModuleCtx.Host, 0))
        out = sock.getsockname()[1]

    return out

# ################################################################################################################################
# ################################################################################################################################

class QueueBridgeStandIn:
    """ Runs a Redis server of its own and answers each command of the command stream with a reply of success,
    keeping the commands it answered.
    """
    _process: 'Popen[bytes]'
    _thread: 'Thread'

    def __init__(self) -> 'None':
        self.port = _get_free_port()
        self.directory = mkdtemp(prefix=ModuleCtx.Directory_Prefix)
        self.commands:'list[strstrdict]' = []
        self._should_stop = Event()

# ################################################################################################################################

    def new_redis(self) -> 'Redis':
        out = Redis(host=ModuleCtx.Host, port=self.port, decode_responses=True)
        return out

# ################################################################################################################################

    def server_environment(self) -> 'strstrdict':
        """ The variables through which the workers of the server connect to the Redis server of the stand-in.
        """
        out = {
            ModuleCtx.Env_Host: ModuleCtx.Host,
            ModuleCtx.Env_Port: str(self.port),
        }
        return out

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the Redis server, without persistence and in the directory of the stand-in, and the thread
        that answers the commands.
        """
        command = ['redis-server', '--port', str(self.port), '--bind', ModuleCtx.Host, '--dir', self.directory,
            '--save', '', '--appendonly', 'no']

        self._process = Popen(command, stdout=DEVNULL, stderr=DEVNULL)
        self._wait_until_ready(self._process)

        self._thread = Thread(target=self._answer_commands, name='queue-bridge-stand-in', daemon=True)
        self._thread.start()

        logger.info('Queue bridge stand-in on Redis port %s', self.port)

# ################################################################################################################################

    def _wait_until_ready(self, process:'Popen[bytes]') -> 'None':
        redis = self.new_redis()
        deadline = monotonic() + ModuleCtx.Ready_Timeout

        while monotonic() < deadline:

            # A server that exited, for instance because its port was taken in the meantime, is not waited for ..
            if process.poll() is not None:
                raise Exception(f'Redis server exited with code {process.returncode}')

            # .. a server that answers is ready ..
            try:
                _ = redis.ping()
                return

            # .. and any other one is still starting.
            except RedisError:
                sleep(ModuleCtx.Ready_Sleep)

        raise Exception(f'Redis server did not become ready within {ModuleCtx.Ready_Timeout}s')

# ################################################################################################################################

    def _answer_commands(self) -> 'None':
        """ Reads every command from the beginning of the command stream and adds a reply of success
        under its correlation ID to the reply stream, which the reply group of every worker receives.
        """
        redis = self.new_redis()
        last_id = '0'

        while not self._should_stop.is_set():

            result = cast_('anylist', redis.xread(
                {ClientCtx.Command_Stream: last_id},
                count=ModuleCtx.Command_Count,
                block=ModuleCtx.Command_Block_Ms,
            ))

            for _stream_name, messages in result:
                for message_id, fields in messages:
                    last_id = message_id
                    self.commands.append(fields)

                    _ = redis.xadd(ClientCtx.Reply_Stream, {
                        'correlation_id': fields['correlation_id'],
                        'status': ModuleCtx.Status_OK,
                        'data': '{}',
                    })

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Ends the thread that answers the commands and the Redis server.
        """
        self._should_stop.set()
        self._thread.join(ModuleCtx.Stop_Timeout)

        self._process.terminate()
        _ = self._process.wait(ModuleCtx.Stop_Timeout)

# ################################################################################################################################
# ################################################################################################################################
