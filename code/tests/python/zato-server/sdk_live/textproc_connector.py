# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.sdk import Connector, Field
from zato.common.sdk import runner
from zato.common.sdk.runner import RunnerClient

# ################################################################################################################################
# ################################################################################################################################

# How long to wait for the runner process to start accepting connections, in seconds.
_startup_timeout = 15

# ################################################################################################################################
# ################################################################################################################################

class TextProcConnector(Connector):
    """ Wraps a Python library that cannot live in the server process - the stock runner runs
    the library's module in a clean interpreter and this connector talks to it over a local socket.
    """
    type = 'textproc'

    # Configuration schema - which interpreter runs the runner and which module the runner exposes.
    python_path = Field.Text()
    module_path = Field.Text()

# ################################################################################################################################

    def create_client(self) -> 'RunnerClient':

        # Run the stock runner as a supervised helper process, in a clean interpreter -
        # the runner depends on the standard library only, so any interpreter can run it by path.
        command = [self.config.python_path, runner.__file__, '{port}', self.config.module_path]
        process = self.start_process(command)

        client = RunnerClient('127.0.0.1', process.port)

        # The interpreter needs a moment before the runner accepts connections.
        deadline = time.monotonic() + _startup_timeout

        while True:
            try:
                _ = client.call('ping')
            except OSError:
                if time.monotonic() > deadline:
                    raise Exception(f'The runner did not start within {_startup_timeout}s')
                time.sleep(0.2)
            else:
                break

        self.logger.info('Runner started for `%s` (pid %s)', self.name, process.pid)
        return client

# ################################################################################################################################

    def ping(self, client:'RunnerClient') -> 'None':
        _ = client.call('ping')

# ################################################################################################################################

    def transform(self, text:'str') -> 'str':
        out = self.client.call('transform', text)
        return out

# ################################################################################################################################
# ################################################################################################################################
