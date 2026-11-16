# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import subprocess
import time
from tempfile import mkdtemp

# redis
from redis import Redis
from redis.exceptions import RedisError

# Zato
from zato.common.util.tcp import get_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Host = '127.0.0.1'

    # Where the search for a free port starts
    Port_Start = 42000

    # How long the server may take to accept commands after it starts, in seconds
    Ready_Timeout = 30.0
    Ready_Sleep = 0.1

    # How long the server may take to write its log and exit after a shutdown command, in seconds
    Stop_Timeout = 30.0

# ################################################################################################################################
# ################################################################################################################################

class RedisProcess:
    """ A Redis server of the tests' own, on a free port, which writes every command to its append-only file
    before it replies, so that a restart in the same directory keeps every stream, consumer group and pending entry.
    """

    def __init__(self) -> 'None':
        self.port = get_free_port(ModuleCtx.Port_Start)
        self.data_dir = mkdtemp(prefix='zato_test_redis_')
        self._process:'any_' = None

# ################################################################################################################################

    def server_environment(self) -> 'strstrdict':
        """ The variables through which the scheduler and the server connect to this Redis.
        """
        out:'strstrdict' = {
            'Zato_Scheduler_Redis_Host': ModuleCtx.Host,
            'Zato_Scheduler_Redis_Port': str(self.port),
            'Zato_Scheduler_Redis_Password': '',
        }
        return out

# ################################################################################################################################

    def new_connection(self) -> 'Redis':
        out = Redis(host=ModuleCtx.Host, port=self.port, decode_responses=True)
        return out

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the server in its data directory and waits until it accepts commands.
        """
        command = [
            'redis-server',
            '--bind', ModuleCtx.Host,
            '--port', str(self.port),
            '--dir', self.data_dir,
            '--save', '',
            '--appendonly', 'yes',
            '--appendfsync', 'always',
        ]

        self._process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        connection = self.new_connection()
        deadline = time.monotonic() + ModuleCtx.Ready_Timeout

        while True:

            # A server that exited, e.g. because its port was taken in the meantime, is not waited for ..
            if self._process.poll() is not None:
                raise Exception(f'Redis server exited with code {self._process.returncode}')

            # .. a server that answers is ready ..
            try:
                _ = connection.ping()
                break

            # .. and any other one is still starting.
            except RedisError:
                if time.monotonic() > deadline:
                    raise
                time.sleep(ModuleCtx.Ready_Sleep)

        connection.close()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the server, which writes its append-only file before it exits.
        """
        self._process.terminate()
        _ = self._process.wait(ModuleCtx.Stop_Timeout)
        self._process = None

# ################################################################################################################################

    def cleanup(self) -> 'None':
        """ Stops the server if it runs.
        """
        if self._process is not None:
            self.stop()

# ################################################################################################################################
# ################################################################################################################################

class SchedulerRedis:
    """ The Redis of the scheduler of the running suite, which its tests stop and start again.
    """
    process:'RedisProcess'

# ################################################################################################################################
# ################################################################################################################################
