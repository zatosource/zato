# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
from pathlib import Path

# Zato
from live_windows.build import build_missing
from live_windows.containers import acquire_guests, build_ready_states, running_guests, stop_guests
from live_windows.enmasse import build_yaml
from live_windows.settings import Versions

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from argparse import Namespace

# ################################################################################################################################
# ################################################################################################################################

def _build(arguments:'Namespace') -> 'None':
    build_missing(arguments.versions, arguments.force)
    build_ready_states(arguments.versions)

# ################################################################################################################################

def _start(arguments:'Namespace') -> 'None':
    _ = acquire_guests(arguments.versions)

# ################################################################################################################################

def _stop(arguments:'Namespace') -> 'None':
    stop_guests(arguments.versions)

# ################################################################################################################################

def _status(arguments:'Namespace') -> 'None':
    for guest in running_guests():
        print(f'{guest.prefix} {guest.name} SMB on 127.0.0.1:{guest.port}', flush=True)

# ################################################################################################################################

def _enmasse(arguments:'Namespace') -> 'None':
    """ Writes the enmasse file of each running guest, each with the partner drop on the same guest.
    """
    output_dir = Path(arguments.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for guest in running_guests():
        definitions = build_yaml(guest, guest)
        path = output_dir / f'smb-win{guest.version}.yaml'
        _ = path.write_text(definitions)
        print(f'{guest.prefix} {path}', flush=True)

# ################################################################################################################################

_commands = {
    'build': _build,
    'start': _start,
    'stop': _stop,
    'status': _status,
    'enmasse': _enmasse,
}

# ################################################################################################################################

def main() -> 'None':

    parser = argparse.ArgumentParser(description='Windows Server guests for the live SMB tests')
    subparsers = parser.add_subparsers(dest='command', required=True)

    build_parser = subparsers.add_parser('build', help='Build the prepared disks and the ready states that are missing or out of date')
    _ = build_parser.add_argument('--force', action='store_true')

    start_parser = subparsers.add_parser('start', help='Resume the guests from their ready states')
    stop_parser = subparsers.add_parser('stop', help='Remove the guests and everything written to them')

    _ = subparsers.add_parser('status', help='List the running guests')

    enmasse_parser = subparsers.add_parser('enmasse', help='Write the enmasse file of each running guest')
    _ = enmasse_parser.add_argument('--output-dir', required=True)

    for version_parser in build_parser, start_parser, stop_parser:
        _ = version_parser.add_argument('--version', action='append', choices=Versions.All, dest='versions')

    arguments = parser.parse_args()

    if 'versions' in arguments:
        if not arguments.versions:
            arguments.versions = list(Versions.All)

    command = _commands[arguments.command]
    command(arguments)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
