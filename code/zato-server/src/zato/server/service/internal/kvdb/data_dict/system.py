# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

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
from contextlib import closing

# Zato
from zato.common import KVDB
from zato.server.service.internal import AdminService

class GetList(AdminService):
    """ Returns a list of translation systems.
    """
    class SimpleIO:
        output_required = ('name',)
        
    def get_data(self):
        return self.server.kvdb.conn.lrange(KVDB.SYSTEM_LIST, 0, -1)

    def handle(self):
        self.response.payload[:] = self.get_data()

class Create(AdminService):
    """ Creates a new translation system.
    """
    class SimpleIO:
        input_required = ('name',)
        output_required = ('name',)

    def handle(self):
        already_exists = self.server.kvdb.conn.sismember(KVDB.SYSTEM_LIST, self.request.input.name)
        print(3333, already_exists)
        
        self.response.payload.name = self.request.input.name

