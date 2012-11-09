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

# Zato
from zato.cli import ca_create_ca as ca_create_ca_mod
from zato.common import version as zato_version
    
"""
zato ca create ca/load_balancer_agent/server/zato_admin .
zato create load_balancer/odb/server/zato_admin .
zato delete odb .
zato quickstart create/start .
zato info .
zato start .
zato stop .
zato version .
#zato --version
"""

def get_parser():
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument('path', help='Path to a directory')
    base_parser.add_argument('--store-log', help='Whether to store an execution log', action='store_true')
    base_parser.add_argument('--verbose', help='Show verbose output', action='store_true')
    base_parser.add_argument('--store-options', 
        help='Whether to store options in a file for a later use', action='store_true')
    
    parser = argparse.ArgumentParser(prog='zato')
    parser.add_argument('--version', action='version', version=zato_version)
    
    subs = parser.add_subparsers()
    
    #
    # ca
    #
    ca = subs.add_parser('ca')
    ca_subs = ca.add_subparsers()
    ca_create = ca_subs.add_parser('create', help='Create crypto material for a Zato component')
    ca_create_subs = ca_create.add_subparsers()

    ca_create_ca = ca_create_subs.add_parser('ca', 
        help='Create a new certificate authority ', parents=[base_parser])
    ca_create_ca.set_defaults(command='ca_create_ca')
        
    for opt in ca_create_ca_mod.CreateCA.opts:
        ca_create_ca.add_argument(opt['name'], help=opt['help'])
    
    ca_create_lb_agent = ca_create_subs.add_parser('lb_agent', 
        help='Create crypto material for a Zato load-balancer agent', parents=[base_parser])
    ca_create_lb_agent.set_defaults(command='ca_create_lb_agent')
        
    ca_create_server = ca_create_subs.add_parser('server', 
       help='Create crypto material for a Zato server', parents=[base_parser])
    ca_create_server.set_defaults(command='ca_create_server')
       
    ca_create_zato_admin = ca_create_subs.add_parser('zato_admin', 
        help='Create crypto material for a Zato web console', parents=[base_parser])
    ca_create_zato_admin.set_defaults(command='ca_create_zato_admin')
    
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
    
    return parser

def main():
    command_class = {
        'ca_create_ca': ca_create_ca_mod.CreateCA
    }
    
    args = get_parser().parse_args()
    class_ = command_class[args.command]
    class_(args).execute(args)

