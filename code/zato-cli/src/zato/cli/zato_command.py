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
from zato.cli import ca_create_ca as ca_create_ca_mod, ca_create_lb_agent as ca_create_lb_agent_mod, \
     ca_create_server as ca_create_server_mod, ca_create_zato_admin as ca_create_zato_admin_mod, \
     component_version as component_version_mod, create_cluster as create_cluster_mod, \
     create_lb as create_lb_mod, create_odb as create_odb_mod, create_server as create_server_mod, \
     create_zato_admin as create_zato_admin_mod, crypto as crypto_mod, delete_odb as delete_odb_mod, \
     quickstart as quickstart_mod, start as start_mod, FromConfigFile
from zato.common import version as zato_version
    
"""
# zato ca create ca .
# zato ca create lb_agent .
# zato ca create server .
# zato ca create zato_admin .
# zato component-version .
# zato create load_balancer .
# zato create odb .
# zato create cluster
# zato create server .
# zato create zato_admin .
# zato decrypt . --secret
# zato delete odb .
# zato encrypt . --secret
zato from-config ./zato.config.file
# zato quickstart create .
zato info . # TODO: replace .lb-dir with .zato-info['component']
zato services export . token
zato services import . dump
!!! zato start .
zato stop .
zato update crypto . --priv-key ./path --pub-key ./path --cert ./path
zato update password .
zato --batch
zato --store-config
# zato --store-log
# zato --version
"""

def add_opts(parser, opts):
    """ Adds parser-specific options.
    """
    for opt in opts:
        parser.add_argument(opt['name'], help=opt['help'])

def get_parser():
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument('--store-log', help='Whether to store an execution log', action='store_true')
    base_parser.add_argument('--verbose', help='Show verbose output', action='store_true')
    base_parser.add_argument('--store-config', 
        help='Whether to store config options in a file for a later use', action='store_true')
    
    parser = argparse.ArgumentParser(prog='zato')
    parser.add_argument('--version', action='version', version=zato_version)
    
    subs = parser.add_subparsers()
    
    #
    # ca
    #
    ca = subs.add_parser('ca', description='Basic certificate authority (CA) management')
    ca_subs = ca.add_subparsers()
    ca_create = ca_subs.add_parser('create', description='Creates crypto material for Zato components')
    ca_create_subs = ca_create.add_subparsers()

    ca_create_ca = ca_create_subs.add_parser('ca', 
        description='Create a new certificate authority ', parents=[base_parser])
    ca_create_ca.set_defaults(command='ca_create_ca')
    ca_create_ca.add_argument('path', help='Path to an empty directory to hold the CA')
    add_opts(ca_create_ca, ca_create_ca_mod.Create.opts)
    
    ca_create_lb_agent = ca_create_subs.add_parser('lb_agent', 
        description='Create crypto material for a Zato load-balancer agent', parents=[base_parser])
    ca_create_lb_agent.set_defaults(command='ca_create_lb_agent')
    ca_create_lb_agent.add_argument('path', help='Path to a CA directory')
    add_opts(ca_create_lb_agent, ca_create_lb_agent_mod.Create.opts)
        
    ca_create_server = ca_create_subs.add_parser('server', 
       description='Create crypto material for a Zato server', parents=[base_parser])
    ca_create_server.set_defaults(command='ca_create_server')
    ca_create_server.add_argument('path', help='Path to a CA directory')
    add_opts(ca_create_server, ca_create_server_mod.Create.opts)

    ca_create_zato_admin = ca_create_subs.add_parser('zato_admin', 
        description='Create crypto material for a Zato web console', parents=[base_parser])
    ca_create_zato_admin.set_defaults(command='ca_create_zato_admin')
    ca_create_zato_admin.add_argument('path', help='Path to a CA directory')
    add_opts(ca_create_zato_admin, ca_create_zato_admin_mod.Create.opts)

    # 
    # component-version
    #
    component_version = subs.add_parser('component-version',
        description='Shows the version of a Zato component installed in a given directory', 
        parents=[base_parser])
    component_version.set_defaults(command='component_version')
    component_version.add_argument('path', help='Path to a Zato component')
    add_opts(component_version, component_version_mod.ComponentVersion.opts)
    
    # 
    # create
    #
    create = subs.add_parser('create', description='Creates new Zato components')
    create_subs = create.add_subparsers()
    
    create_cluster = create_subs.add_parser('cluster', parents=[base_parser], description='Creates a new Zato cluster in the ODB')
    create_cluster.set_defaults(command='create_cluster')
    add_opts(create_cluster, create_cluster_mod.Create.opts)
    
    create_lb = create_subs.add_parser('load_balancer', parents=[base_parser], 
        description='Creates a new Zato load-balancer')
    create_lb.add_argument('path', help='Path to an empty directory to install the load-balancer in')
    create_lb.set_defaults(command='create_lb')
    add_opts(create_lb, create_lb_mod.Create.opts)
    
    create_odb = create_subs.add_parser('odb', parents=[base_parser], description='Creates a new Zato ODB (Operational Database)')
    create_odb.set_defaults(command='create_odb')
    add_opts(create_odb, create_odb_mod.Create.opts)
    
    create_server = create_subs.add_parser('server', parents=[base_parser], description='Creates a new Zato server')
    create_server.add_argument('path', help='Path to an empty directory to install the server in')
    create_server.set_defaults(command='create_server')
    add_opts(create_server, create_server_mod.Create.opts)
    
    create_zato_admin = create_subs.add_parser('zato_admin', parents=[base_parser], description='Creates a new Zato Admin web console')
    create_zato_admin.add_argument('path', help='Path to an empty directory to install a new Zato Admin web console in')
    create_zato_admin.set_defaults(command='create_zato_admin')
    add_opts(create_zato_admin, create_zato_admin_mod.Create.opts)

    #
    # decrypt
    #
    decrypt = subs.add_parser('decrypt', parents=[base_parser], description='Decrypts secrets using a private key')
    decrypt.add_argument('path', help='Path to the private key in PEM')
    decrypt.set_defaults(command='decrypt')
    add_opts(decrypt, crypto_mod.Decrypt.opts)
    
    #
    # delete
    #
    delete = subs.add_parser('delete', description='Deletes Zato components')
    delete_subs = delete.add_subparsers()
    delete_odb = delete_subs.add_parser('odb', parents=[base_parser], description='Deletes a Zato ODB')
    delete_odb.set_defaults(command='delete_odb')
    add_opts(delete_odb, delete_odb_mod.Delete.opts)
    
    #
    # encrypt
    #
    encrypt = subs.add_parser('encrypt', parents=[base_parser], description='Encrypts secrets using a public key')
    encrypt.add_argument('path', help='Path to the public key in PEM')
    encrypt.set_defaults(command='encrypt')
    add_opts(encrypt, crypto_mod.Encrypt.opts)
    
    #
    # info
    #
    info = subs.add_parser('info', description='Detailed information regarding a chosen Zato component',
        parents=[base_parser])
        
    #
    # from-config-file
    #
    from_config = subs.add_parser('from-config', description='Run commands from a config file', parents=[base_parser])
    from_config.set_defaults(command='from_config')
    
    #
    # quickstart
    #
    quickstart = subs.add_parser('quickstart', description='Quickly set up and manage Zato clusters', parents=[base_parser])
    quickstart_subs = quickstart.add_subparsers()
    
    quickstart_create = quickstart_subs.add_parser('create', description=quickstart_mod.Create.__doc__, parents=[base_parser])
    quickstart_create.add_argument('path', help='Path to an empty directory for the quickstart cluster')
    quickstart_create.set_defaults(command='quickstart_create')
    add_opts(quickstart_create, quickstart_mod.Create.opts)
    
    #
    # start
    #
    start_desc = """Starts a Zato component installed in the 'path'. The same command is used for starting servers, load-balancer agents and Zato Admin instances.
'path' must point to an existing directory into which the given component has been installed.

Examples:
  Assuming a Zato server has been installed in /opt/zato/server1, the command to start the server is 'zato start /opt/zato/server1'.
  If a load-balancer's agent has been installed in /home/zato/lb-agent1, the command to start it is 'zato start /home/zato/lb-agent1'.
"""
    start = subs.add_parser('start', description=start_desc, parents=[base_parser], formatter_class=argparse.RawDescriptionHelpFormatter)
    start.add_argument('path', help='Path to the Zato component to be started')
    start.set_defaults(command='start')
    
    #
    # stop
    #
    stop = subs.add_parser('stop', description='Stops a Zato component', parents=[base_parser])

    return parser

def main():
    command_class = {
        'ca_create_ca': ca_create_ca_mod.Create,
        'ca_create_lb_agent': ca_create_lb_agent_mod.Create,
        'ca_create_server': ca_create_server_mod.Create,
        'ca_create_zato_admin': ca_create_zato_admin_mod.Create,
        'component_version': component_version_mod.ComponentVersion,
        'create_cluster': create_cluster_mod.Create,
        'create_lb': create_lb_mod.Create,
        'create_odb': create_odb_mod.Create,
        'create_server': create_server_mod.Create,
        'create_zato_admin': create_zato_admin_mod.Create,
        'delete_odb': delete_odb_mod.Delete,
        'decrypt': crypto_mod.Decrypt,
        'encrypt': crypto_mod.Encrypt,
        'from_config_file': FromConfigFile,
        'quickstart_create': quickstart_mod.Create,
        'start': start_mod.Start,
    }
    args = get_parser().parse_args()
    command_class[args.command](args).run(args)
