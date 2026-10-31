# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The controller of an active-standby pair of Zato servers. It checks the active server through its ping endpoint,
# and after a given number of consecutive failed checks, it starts the standby container and then stops the old one.
# It checks the server process only, never the database, so a database outage of any length starts no new server.

# stdlib
import argparse
import json
import subprocess
import sys
import time
from http.client import OK
from urllib.error import URLError
from urllib.request import Request, urlopen

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# How long the old container may take to stop gracefully before Docker kills it, in seconds.
_stop_timeout_seconds = 10

# ################################################################################################################################
# ################################################################################################################################

def _write_event(events_path:'str', event:'str', **details:'object') -> 'None':
    """ Appends one event of the controller to its events file as a JSON line.
    """
    record:'anydict' = {'event': event, 'time': time.time()}
    record.update(details)

    with open(events_path, 'a') as events_file:
        _ = events_file.write(json.dumps(record) + '\n')

# ################################################################################################################################

def _is_server_up(ping_url:'str', timeout_seconds:'float') -> 'bool':
    """ Tells whether the server answers its ping endpoint within the timeout.
    """
    request = Request(ping_url, method='GET')

    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            out = response.status == OK
    except (OSError, URLError):
        out = False

    return out

# ################################################################################################################################

def _docker(*args:'str') -> 'subprocess.CompletedProcess[str]':
    out = subprocess.run(['docker', *args], capture_output=True, text=True, check=False)
    return out

# ################################################################################################################################

def run_controller(
    ping_url:'str',
    active_container:'str',
    standby_container:'str',
    interval_seconds:'float',
    max_failures:'int',
    events_path:'str',
) -> 'int':
    """ Checks the active server until it fails max_failures checks in a row, then starts the standby container
    and stops the old one. Returns the exit code of the process.
    """
    _write_event(events_path, 'started', ping_url=ping_url, active=active_container, standby=standby_container)

    failure_count = 0

    while True:

        if _is_server_up(ping_url, interval_seconds):
            failure_count = 0
        else:
            failure_count += 1
            _write_event(events_path, 'check_failed', failure_count=failure_count)

            if failure_count >= max_failures:
                break

        time.sleep(interval_seconds)

    # The standby is started first, so that the pair is without a server for as short a time as possible ..
    result = _docker('start', standby_container)
    _write_event(events_path, 'standby_started', returncode=result.returncode, stderr=result.stderr)

    if result.returncode != 0:
        return result.returncode

    # .. and the old server is stopped, or killed if it cannot be stopped, which is the case of a paused container.
    result = _docker('stop', '--time', str(_stop_timeout_seconds), active_container)

    if result.returncode != 0:
        result = _docker('kill', active_container)

    _write_event(events_path, 'old_stopped', returncode=result.returncode, stderr=result.stderr)

    return 0

# ################################################################################################################################

def main() -> 'int':

    parser = argparse.ArgumentParser(description='Active-standby controller of Zato servers')
    _ = parser.add_argument('--ping-url', required=True)
    _ = parser.add_argument('--active', required=True)
    _ = parser.add_argument('--standby', required=True)
    _ = parser.add_argument('--interval', type=float, default=1.0)
    _ = parser.add_argument('--failures', type=int, default=3)
    _ = parser.add_argument('--events', required=True)

    args = parser.parse_args()

    out = run_controller(args.ping_url, args.active, args.standby, args.interval, args.failures, args.events)
    return out

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    sys.exit(main())

# ################################################################################################################################
# ################################################################################################################################
