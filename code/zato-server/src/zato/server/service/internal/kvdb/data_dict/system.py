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

class _SystemService(AdminService):
    def _get_systems(self):
        for id, name in self.server.kvdb.conn.hgetall(KVDB.SYSTEM_LIST).items():
            yield {'id':id, 'name':name}

class GetList(_SystemService):
    """ Returns a list of translation systems.
    """
    class SimpleIO:
        output_required = ('id', 'name',)
        
    def get_data(self):
        return self._get_systems()

    def handle(self):
        self.response.payload[:] = self.get_data()

class _CreateEdit(_SystemService):
    SYSTEM_NAME_PATTERN = '\w+'
    SYSTEM_NAME_RE = re.compile(SYSTEM_NAME_PATTERN)

    class SimpleIO:
        input_required = ('name',)
        input_optional = ('id',)
        output_required = ('id', 'name')
        
    def _validate_name(self, validate_exists=False):
        name = self.request.input.name
        match = self.SYSTEM_NAME_RE.match(name)
        if match and match.group() == name:
            if validate_exists:
                for item in self._get_systems():
                    if item['name'] == name:
                        msg = 'System [{}] already exists'.format(name)
                        raise ZatoException(self.cid, msg)
        else:
            msg = "System name may contain only letters, digits and an underscore, failed to validate [{}] against the regular expression {}".format(name, self.SYSTEM_NAME_PATTERN)
            raise ZatoException(self.cid, msg)
        
        return True
        
class Create(_CreateEdit):
    """ Creates a new translation system.
    """
    def handle(self):
        if self._validate_name():
            ids = self.server.kvdb.conn.hkeys(KVDB.SYSTEM_LIST)
            id = (max(int(elem) for elem in ids) + 1) if ids else 1
            self.server.kvdb.conn.hset(KVDB.SYSTEM_LIST, id, self.request.input.name)
            
            self.response.payload.id = id
            self.response.payload.name = self.request.input.name
        
class Edit(_CreateEdit):
    """ Updates a translation system..
    """
    def handle(self):
        if self._validate_name(True):
            self.server.kvdb.conn.hset(KVDB.SYSTEM_LIST, self.request.input.id, self.request.input.name)
            
            self.response.payload.id = self.request.input.id
            self.response.payload.name = self.request.input.name

class Delete(AdminService):
    """ Deletes a translation system.
    """
    class SimpleIO:
        input_required = ('id',)
        output_required = ('id',)
        
    def handle(self):
        self.server.kvdb.conn.hdel(KVDB.SYSTEM_LIST, self.request.input.id)
        self.response.payload.id = self.request.input.id
