#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import sys

# Zato
from zato.cli import quickstart, start, stop, odb_delete, info

USAGE = """
Zato 1.0 - the open-source ESB and application server

TODO: Read the version off of somewhere in the line above
https:// TODO: Add URL here

Commands:

  zato start       Starts a given component
  zato stop        Stops a given component

  zato info        Shows information about a running component

  zato ca          Certificate Authority for use with Zato components
  zato odb         Manages the Operational Database

  zato create      Creates a new component
  zato quickstart  Quickly creates a ready to use Zato environment

All commands accept -h and --help parameters, e.g. 'zato start --help' will show help on using the 'zato start' command.

Refer to online documentation at http:// TODO: URL for more information and usage examples.
"""

class PrintHelp(object):
    def __init__(self, command):
        self.command = command

    def run(self, work_args):
        print(help[self.command])
        sys.exit(0)

commands = {
    'start': start.Start(),
    'stop': stop.Stop(),

    'info': info.Info(),

    'ca': PrintHelp('ca'),
    'ca create-ca': '',
    'ca create-lb-agent': '',
    'ca create-server': '',
    'ca create-zato-admin': '',

    'odb create': '',
    'odb delete': odb_delete.Delete(),

    'create': PrintHelp('create'),
    'create lb-agent': '',
    'create server': '',
    'create zato-admin': '',

    'quickstart': quickstart.Quickstart(),
}

def _help_only(argv):
    return len(argv) == 2 or len(argv) > 2 and argv[2] in ('--help', '-h')

def _unknown_command(command):
    print('Unknown command: {0}'.format(command))
    print(USAGE)
    sys.exit(2)

def _get_handler_work_args(argv):
    if _help_only(argv):
        if len(argv) == 2:
            work_args = []
        else:
            work_args = sys.argv[2:]

        command = argv[1]
        handler = commands.get(command, None)
        if not handler:
            _unknown_command('zato {0}'.format(command))

        return handler, work_args

    else:
        command1 = argv[1]
        command2 = ''

        if command1 in('quickstart', 'start', 'stop', 'info'):
            work_args = sys.argv[2:]
        else:
            if len(argv) >= 2:
                command2 = argv[2]
            work_args = sys.argv[3:]

        command = command1
        if command2:
            command += ' ' + command2

        handler = commands.get(command, None)
        if not handler:
            _unknown_command('zato {0}'.format(command))

    return handler, work_args

def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(2)

    handler, work_args = _get_handler_work_args(sys.argv)
    handler.run(work_args=work_args)
