# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The controller of an active-standby pair of Zato servers. It checks the active server through its ping endpoint,
# and after a given number of consecutive failed checks, it starts the standby container and then stops the old one.
# The two servers then exchange their roles and the controller checks the new active one, for as long as it runs.
# It checks the server process only, never the database, so a database outage of any length starts no new server.

# stdlib
import argparse
import json
import subprocess
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

class ControlledServer:
    """ One server of the pair - its container and the URL of its ping endpoint.
    """
    def __init__(self, container:'str', ping_url:'str') -> 'None':
        self.container = container
        self.ping_url = ping_url

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

def _is_running(container:'str') -> 'bool':
    """ Tells whether the process of a server container still runs, including a container that is paused.
    """
    result = _docker('inspect', '--format', '{{.State.Running}}', container)
    out = result.stdout.strip() == 'true'
    return out

# ################################################################################################################################

def _wait_for_failure(server:'ControlledServer', interval_seconds:'float', max_failures:'int', events_path:'str') -> 'None':
    """ Returns once the active server has failed max_failures checks in a row. A server that is still starting,
    e.g. waiting for its database, answers no check and fails one only if its process has exited, whereas after
    its first answer, each check that it does not answer is a failure.
    """
    failure_count = 0
    has_answered = False

    while True:

        if _is_server_up(server.ping_url, interval_seconds):
            failure_count = 0
            has_answered = True

        elif has_answered or not _is_running(server.container):
            failure_count += 1
            _write_event(events_path, 'check_failed', container=server.container, failure_count=failure_count)

            if failure_count >= max_failures:
                return

        time.sleep(interval_seconds)

# ################################################################################################################################

def _start_standby(server:'ControlledServer', interval_seconds:'float', events_path:'str') -> 'None':
    """ Starts the standby container, and starts it again after each failure, as the pair has no server until it runs.
    """
    attempt = 0

    while True:
        attempt += 1

        result = _docker('start', server.container)
        _write_event(events_path, 'standby_started',
            container=server.container, attempt=attempt, returncode=result.returncode, stderr=result.stderr)

        if result.returncode == 0:
            return

        time.sleep(interval_seconds)

# ################################################################################################################################

def _stop_old(server:'ControlledServer', events_path:'str') -> 'None':
    """ Stops the old server, or kills it if it cannot be stopped, which is the case of a paused container.
    """
    result = _docker('stop', '--time', str(_stop_timeout_seconds), server.container)

    if result.returncode != 0:
        result = _docker('kill', server.container)

    _write_event(events_path, 'old_stopped', container=server.container, returncode=result.returncode, stderr=result.stderr)

# ################################################################################################################################

def run_controller(
    active:'ControlledServer',
    standby:'ControlledServer',
    interval_seconds:'float',
    max_failures:'int',
    events_path:'str',
) -> 'None':
    """ Checks the active server until it fails max_failures checks in a row, then starts the standby container,
    stops the old one, and checks the new active server in the same way, until the process is stopped.
    """
    _write_event(events_path, 'started', active=active.container, standby=standby.container)

    while True:
        _wait_for_failure(active, interval_seconds, max_failures, events_path)

        # The standby is started first, so that the pair is without a server for as short a time as possible ..
        _start_standby(standby, interval_seconds, events_path)

        # .. the old server is stopped ..
        _stop_old(active, events_path)

        # .. and the servers exchange their roles.
        active, standby = standby, active
        _write_event(events_path, 'switched', active=active.container, standby=standby.container)

# ################################################################################################################################

def main() -> 'None':

    parser = argparse.ArgumentParser(description='Active-standby controller of Zato servers')
    _ = parser.add_argument('--active', required=True)
    _ = parser.add_argument('--active-ping-url', required=True)
    _ = parser.add_argument('--standby', required=True)
    _ = parser.add_argument('--standby-ping-url', required=True)
    _ = parser.add_argument('--interval', type=float, default=1.0)
    _ = parser.add_argument('--failures', type=int, default=3)
    _ = parser.add_argument('--events', required=True)

    args = parser.parse_args()

    active = ControlledServer(args.active, args.active_ping_url)
    standby = ControlledServer(args.standby, args.standby_ping_url)

    run_controller(active, standby, args.interval, args.failures, args.events)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
