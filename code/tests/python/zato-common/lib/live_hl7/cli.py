# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from argparse import ArgumentParser, Namespace

# Live HL7
from live_hl7.compose import has_docker
from live_hl7.credentials import get_password
from live_hl7.registry import get_system, group_names, system_names
from live_hl7.runner import describe, extra_environment_from_process, logs, start, start_group, stop, stop_group
from live_hl7.state import list_states, read_state

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_hl7.system import Handle

# ################################################################################################################################
# ################################################################################################################################

def _print_handle(handle:'Handle') -> 'None':
    """ The system's ports and, when it has one, where its UI is and who logs in.
    """
    for purpose, port in handle.ports.items():
        print(f'  {purpose:<14} {port}', flush=True)

    system = get_system(handle.system)
    url = system.ui_url(handle)

    if url:
        print(f'  UI             {url}', flush=True)
        print(f'  Login          {system.ui_username}', flush=True)

        if handle.password != get_password():
            print(f'  Password       {handle.password}', flush=True)

# ################################################################################################################################

def _command_start(arguments:'Namespace') -> 'None':
    handle = start(arguments.system, extra_environment=extra_environment_from_process())
    _print_handle(handle)

    if not arguments.follow:
        return

    print('', flush=True)
    print('Following the logs, Ctrl+C leaves the system running', flush=True)
    print('', flush=True)

    get_system(handle.system).follow_logs(handle)

# ################################################################################################################################

def _command_stop(arguments:'Namespace') -> 'None':
    stop(arguments.system)

# ################################################################################################################################

def _command_status(arguments:'Namespace') -> 'None':
    systems = list_states()

    if not systems:
        print('No live HL7 system is running standalone', flush=True)
        return

    for system in systems:
        state = read_state(system)
        ports = state['ports']

        print(f'{system} - {state["project_name"]} - since {state["started_at"]}', flush=True)

        for purpose, port in ports.items():
            print(f'  {purpose:<14} {port}', flush=True)

# ################################################################################################################################

def _command_logs(arguments:'Namespace') -> 'None':
    output = logs(arguments.system, arguments.service)
    print(output, flush=True)

# ################################################################################################################################

def _command_describe(arguments:'Namespace') -> 'None':
    output = describe(arguments.system)
    print(output, flush=True)

# ################################################################################################################################

def _command_start_group(arguments:'Namespace') -> 'None':
    handles = start_group(arguments.group)

    for handle in handles:
        print(f'{handle.system}', flush=True)
        _print_handle(handle)

# ################################################################################################################################

def _command_stop_group(arguments:'Namespace') -> 'None':
    stop_group(arguments.group)

# ################################################################################################################################

def _build_parser() -> 'ArgumentParser':
    systems = system_names()
    groups = group_names()

    parser = ArgumentParser(prog='live_hl7', description='Starts and stops the live HL7 systems, without Zato.')
    commands = parser.add_subparsers(dest='command', required=True)

    start_parser = commands.add_parser('start', help='Start one system standalone and return once it is ready')
    _ = start_parser.add_argument('system', choices=systems)
    _ = start_parser.add_argument('--follow', action='store_true', help='Then follow its logs until interrupted')
    start_parser.set_defaults(handler=_command_start)

    stop_parser = commands.add_parser('stop', help='Stop one standalone system')
    _ = stop_parser.add_argument('system', choices=systems)
    stop_parser.set_defaults(handler=_command_stop)

    status_parser = commands.add_parser('status', help='List the standalone systems that are running')
    status_parser.set_defaults(handler=_command_status)

    logs_parser = commands.add_parser('logs', help='Print the logs of one standalone system')
    _ = logs_parser.add_argument('system', choices=systems)
    _ = logs_parser.add_argument('service', nargs='?', default='')
    logs_parser.set_defaults(handler=_command_logs)

    describe_parser = commands.add_parser('describe', help='Print what one system is and where it listens')
    _ = describe_parser.add_argument('system', choices=systems)
    describe_parser.set_defaults(handler=_command_describe)

    start_group_parser = commands.add_parser('start-group', help='Start every system of one scenario group')
    _ = start_group_parser.add_argument('group', choices=groups)
    start_group_parser.set_defaults(handler=_command_start_group)

    stop_group_parser = commands.add_parser('stop-group', help='Stop every running system of one scenario group')
    _ = stop_group_parser.add_argument('group', choices=groups)
    stop_group_parser.set_defaults(handler=_command_stop_group)

    return parser

# ################################################################################################################################

def main() -> 'None':
    parser = _build_parser()
    arguments = parser.parse_args()

    # Nothing here runs without docker and, describe aside, without the password ..
    if not has_docker():
        print('docker compose is not available', file=sys.stderr, flush=True)
        sys.exit(1)

    if arguments.command != 'describe':
        _ = get_password()

    # .. and each command is a function of its own.
    arguments.handler(arguments)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
