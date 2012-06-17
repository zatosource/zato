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
import re
from contextlib import closing

# Zato
from zato.common import KVDB, ZatoException
from zato.server.service.internal import AdminService

class GetList(AdminService):
    """ Returns a list of translation systems.
    """
    class SimpleIO:
        output_required = ('name',)
        
    def get_data(self):
        out = []
        for name in sorted(self.server.kvdb.conn.smembers(KVDB.SYSTEM_LIST)):
            out.append({'name': name})
        return out

    def handle(self):
        self.response.payload[:] = self.get_data()

class Create(AdminService):
    """ Creates a new translation system.
    """
    SYSTEM_NAME_PATTERN = '\w+'
    SYSTEM_NAME_RE = re.compile(SYSTEM_NAME_PATTERN)

    class SimpleIO:
        input_required = ('name',)
        output_required = ('name',)

    def handle(self):
        name = self.request.input.name
        match = self.SYSTEM_NAME_RE.match(name)
        if match and match.group() == name:
            already_exists = self.server.kvdb.conn.sismember(KVDB.SYSTEM_LIST, name)
            if already_exists:
                msg = 'System [{}] already exists'.format(name)
                raise ZatoException(self.cid, msg)
            
            self.server.kvdb.conn.sadd(KVDB.SYSTEM_LIST, name)
            self.response.payload.name = name
        else:
            msg = "Name [{}] may contain only letters, digits and an underscore, the regular expression is {}".format(name, self.SYSTEM_NAME_PATTERN)
            raise ZatoException(self.cid, msg)

class Delete(AdminService):
    """ Deletes a translation system.
    """
    class SimpleIO:
        input_required = ('name',)
        output_required = ('name',)
        
    def handle(self):
        self.server.kvdb.conn.srem(KVDB.SYSTEM_LIST, self.request.input.name)
        self.response.payload.name = self.request.input.name
