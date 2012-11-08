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
import argparse, time

# bzrlib
from bzrlib.lazy_import import lazy_import

lazy_import(globals(), """
    # quicli
    from quicli.progress import PercentageProgress
""")

# Zato
from zato.common import version as zato_version
    
"""
zato ca create load_balancer_agent/server/zato_admin .
zato create load_balancer/odb/server/zato_admin .
zato delete odb .
zato quickstart .
zato info .
zato start .
zato stop .
zato version
zato --version
"""

def main():
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument('path', help='Path to a directory')
    
    parser = argparse.ArgumentParser(prog='zato')
    parser.add_argument('--version', action='version', version=zato_version)
    
    subs = parser.add_subparsers()
    
    #
    # ca
    #
    ca = subs.add_parser('ca')
    ca_subs = ca.add_subparsers()
    ca_create = ca_subs.add_parser('create')
    ca_create_subs = ca_create.add_subparsers()
    ca_create_load_balancer_agent = ca_create_subs.add_parser('load_balancer_agent', parents=[base_parser])
    ca_create_server = ca_create_subs.add_parser('server', parents=[base_parser])
    ca_create_zato_admin = ca_create_subs.add_parser('zato_admin', parents=[base_parser])
    
    # 
    # create
    #
    create = subs.add_parser('create')
    create_subs = create.add_subparsers()
    create_load_balancer = create_subs.add_parser('load_balancer')
    create_odb = create_subs.add_parser('odb')
    create_server = create_subs.add_parser('server')
    create_zato_admin = create_subs.add_parser('zato_admin')
    
    #
    # delete
    #
    delete = subs.add_parser('delete')
    delete_subs = delete.add_subparsers()
    delete_odb = delete_subs.add_parser('odb', parents=[base_parser])
    
    #
    # info
    #
    info = subs.add_parser('info', parents=[base_parser])
    
    
    #
    # quickstart
    #
    quickstart = subs.add_parser('quickstart', parents=[base_parser])
    
    #
    # start
    #
    start = subs.add_parser('start', parents=[base_parser])
    
    #
    # stop
    #
    stop = subs.add_parser('stop', parents=[base_parser])
    
    #
    # version
    #
    version = subs.add_parser('version', parents=[base_parser])
    
    args = parser.parse_args()
    print(111)
