# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import threading
import time
from http.client import OK
from urllib.error import URLError
from urllib.request import urlopen

# redis
from redis import Redis

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.process_util import kill_process_tree
from zato.common.typing_ import cast_
from zato.common.util.tcp import get_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strlist, strstrdict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The root of the checkout - this file sits six levels below it.
_zato_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', '..'))

# Where a build of the scheduler is looked for, the release build first.
_binary_paths = (
    os.path.join(_zato_base_dir, 'code', 'zato-rust', 'zato_scheduler_core', 'target', 'release', '_zato_scheduler'),
    os.path.join(_zato_base_dir, 'code', 'zato-rust', 'zato_scheduler_core', 'target', 'debug', '_zato_scheduler'),
)

# The variables the server and the scheduler share.
Stream_Prefix_Variable = 'Zato_Scheduler_Stream_Prefix'
HTTP_Port_Variable     = 'Zato_Scheduler_HTTP_Port'

_redis_host = 'localhost'
_redis_port = 6379

# The Redis the scheduler talks to, unless the environment says otherwise.
_redis_defaults = {
    'Zato_Scheduler_Redis_Host':     _redis_host,
    'Zato_Scheduler_Redis_Port':     str(_redis_port),
    'Zato_Scheduler_Redis_Password': '',
    'Zato_Scheduler_Log_Level':      'info',
}

# Where the HTTP API port search starts.
_http_port_start = 41000

_start_timeout = 30
_poll_interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

def find_binary() -> 'str':
    """ The path of the scheduler binary - raises when nothing was built.
    """
    for path in _binary_paths:
        if os.path.isfile(path):
            if os.access(path, os.X_OK):
                out = path
                break
    else:
        candidates = ', '.join(_binary_paths)
        raise Exception(f'Could not find the scheduler binary, looked in: {candidates}')

    return out

# ################################################################################################################################
# ################################################################################################################################

class SchedulerProcess:
    """ The scheduler binary run against one server, on Redis streams of its own. Creating and starting it are separate steps.
    """

    def __init__(self) -> 'None':
        self.stream_prefix = 'zato:scheduler:test-' + CryptoManager.generate_hex_string()
        self.http_port = get_free_port(_http_port_start)

        self._process:'any_' = None

        # Every line the binary printed, for a failing run to read back.
        self.output_lines:'strlist' = []

# ################################################################################################################################

    def server_environment(self) -> 'strstrdict':
        """ What the server under test starts with.
        """
        out:'strstrdict' = {
            Stream_Prefix_Variable: self.stream_prefix,
            HTTP_Port_Variable:     str(self.http_port),
        }

        return out

# ################################################################################################################################

    def _drain_output(self, process:'any_') -> 'None':
        """ Keeps the binary's pipe from filling up and puts every line where it can be read back from.
        """
        for line in iter(process.stdout.readline, b''):
            text = line.decode('utf8', errors='replace').rstrip()
            self.output_lines.append(text)
            print(f'[SCHEDULER] {text}')

# ################################################################################################################################

    def _wait_for_api(self) -> 'None':
        """ Polls the HTTP API until it answers.
        """
        url = f'http://127.0.0.1:{self.http_port}/metrics'
        deadline = time.monotonic() + _start_timeout
        ready = False

        while time.monotonic() < deadline:

            try:
                with urlopen(url, timeout=5) as response:
                    ready = response.status == OK

            # Not answering yet.
            except URLError:
                ready = False

            if ready:
                break

            time.sleep(_poll_interval)

        if not ready:
            output = '\n'.join(self.output_lines)
            raise Exception(f'The scheduler API at {url} did not answer within {_start_timeout}s, output:\n{output}')

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the binary in a session of its own and waits for its API.
        """
        binary = find_binary()

        environment = dict(os.environ)
        _ = environment.pop('COVERAGE_PROCESS_START', None)

        for name, value in _redis_defaults.items():
            _ = environment.setdefault(name, value)

        environment.update(self.server_environment())

        self._process = subprocess.Popen(
            [binary],
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

        output_thread = threading.Thread(target=self._drain_output, args=(self._process,), daemon=True)
        output_thread.start()

        try:
            self._wait_for_api()
        except Exception:
            self.stop()
            raise

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Ends the binary, if it runs. The streams stay.
        """
        kill_process_tree(self._process)
        self._process = None

# ################################################################################################################################

    def delete_streams(self) -> 'None':
        """ Removes this scheduler's streams from Redis.
        """
        redis_connection = Redis(host=_redis_host, port=_redis_port, decode_responses=True)

        pattern = self.stream_prefix + ':stream:*'
        keys = redis_connection.keys(pattern)
        keys = cast_('anylist', keys)

        if keys:
            _ = redis_connection.delete(*keys)

# ################################################################################################################################

    def cleanup(self) -> 'None':
        """ Ends the binary and removes its streams.
        """
        self.stop()
        self.delete_streams()

# ################################################################################################################################
# ################################################################################################################################
