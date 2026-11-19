# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Runs inside the container of a guest, with the Python of the image, and saves the memory and device state of the guest
to a file through the QMP socket of QEMU.

Usage: python3 - <socket path> <file URI> <timeout in seconds>
"""

# stdlib
import json
import socket
import sys
from time import monotonic, sleep

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Any

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How often the progress of the migration is checked, in seconds
    Poll_Interval = 0.2

    # The states in which a migration ends
    Completed = 'completed'
    Failed    = 'failed', 'cancelled'

# ################################################################################################################################
# ################################################################################################################################

class QMPClient:
    """ Sends commands to QEMU over its QMP socket and returns their results, skipping the events that QEMU sends on its own.
    """
    def __init__(self, path:'str') -> 'None':
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect(path)
        self.stream = self.socket.makefile('rw', encoding='utf8')

        # QEMU greets each new client and accepts commands once the client negotiated its capabilities
        _ = self._read_reply()
        _ = self.call('qmp_capabilities')

    def _read_reply(self) -> 'Any':
        while True:
            line = self.stream.readline()
            message = json.loads(line)
            if 'event' not in message:
                return message

    def call(self, command:'str', **arguments:'Any') -> 'Any':
        request = {
            'execute': command,
            'arguments': arguments,
        }
        line = json.dumps(request)

        _ = self.stream.write(f'{line}\n')
        self.stream.flush()

        reply = self._read_reply()

        if 'error' in reply:
            raise Exception(f'QMP command {command} failed -> {reply}')

        out = reply['return']
        return out

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':

    socket_path = sys.argv[1]
    uri = sys.argv[2]
    timeout = float(sys.argv[3])

    client = QMPClient(socket_path)

    # The guest stops first, so that the saved state is the state of one moment ..
    _ = client.call('stop')

    # .. and its memory and devices are written to the file. QEMU flushes the disk before the migration completes,
    # and the guest stays stopped until the container is removed.
    _ = client.call('migrate', uri=uri)

    start = monotonic()

    while True:

        result = client.call('query-migrate')
        status = result['status']

        if status == ModuleCtx.Completed:
            break

        if status in ModuleCtx.Failed:
            raise Exception(f'Saving the state ended in state {status} -> {result}')

        elapsed = monotonic() - start

        if elapsed > timeout:
            raise Exception(f'The state was not saved within {timeout}s -> {result}')

        sleep(ModuleCtx.Poll_Interval)

    elapsed = monotonic() - start
    print(f'State saved to {uri} in {elapsed:.1f}s', flush=True)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
