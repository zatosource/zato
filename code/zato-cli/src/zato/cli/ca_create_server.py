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

# Zato
from zato.cli import CACreateCommand, common_ca_create_opts

class Create(CACreateCommand):
    opts = [
        {'name':'cluster_name', 'help':'Cluster name'},
        {'name':'server_name', 'help':'Server name'},
        {'name':'--organizational-unit', 'help':'Organizational unit name (defaults to cluster_name:server_name)'},
    ]
    opts += common_ca_create_opts

    def get_file_prefix(self, file_args):
        return '{cluster_name}-{server_name}'.format(**file_args)

    def get_organizational_unit(self, args):
        return args.cluster_name + ':' + args.server_name

    def execute(self, args, show_output=True):
        return self._execute(args, 'v3_client_server', show_output)
