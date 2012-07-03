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
from operator import attrgetter

# Zato
from zato.common import KVDB, ZatoException
from zato.server.service.internal import AdminService
from zato.server.service.internal.kvdb.data_dict import DataDictService

class GetList(DataDictService):
    """ Returns a list of dictionary items.
    """
    class SimpleIO:
        output_required = ('id', 'system', 'key', 'value')
        
    def get_data(self):
        return self._get_dict_items()

    def handle(self):
        self.response.payload[:] = self.get_data()

class _CreateEdit(DataDictService):
    NAME_PATTERN = '\w+'
    NAME_RE = re.compile(NAME_PATTERN)
    
    class SimpleIO:
        input_required = ('system', 'key', 'value')
        input_optional = ('id',)
        output_optional = ('id',)
        
    def _validate_entry(self, validate_item, id=None):
        for elem in('system', 'key'):
            name = self.request.input[elem]
            match = self.NAME_RE.match(name)
            if match and match.group() == name:
                continue
            else:
                msg = "System and key may contain only letters, digits and an underscore, failed to validate [{}] against the regular expression {}".format(name, self.NAME_PATTERN)
                raise ZatoException(self.cid, msg)
        
        for item in self._get_dict_items():
            joined = KVDB.SEPARATOR.join((item['system'], item['key'], item['value']))
            if validate_item == joined and id != item['id']:
                msg = 'The triple of system:[{}], key:[{}], value:[{}] already exists'.format(item['system'], item['key'], item['value'])
                raise ZatoException(self.cid, msg)

        return True

    def _get_item_name(self):
        return KVDB.SEPARATOR.join((self.request.input.system, self.request.input.key, self.request.input.value))

    def handle(self):
        item = self._get_item_name()

        if self.request.input.get('id'):
            id = self.request.input.id
        else:
            id = self.server.kvdb.conn.incr(KVDB.DICTIONARY_ITEM_ID)
            
        id = str(id)
            
        if self._validate_entry(item, id):
            self._handle(id)
        
        self.server.kvdb.conn.hset(KVDB.DICTIONARY_ITEM, id, item)    
        self.response.payload.id = id
        
    def _handle(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by a subclass')

class Create(_CreateEdit):
    """ Creates a new dictionary entry.
    """
    def _handle(self, *ignored_args, **ignored_kwargs):
        pass
        
class Edit(_CreateEdit):
    """ Updates a dictionary entry.
    """
    def _handle(self, id):
        for item in self._get_translations():
            if item['id1'] == id or item['id2'] == id:
                existing_name = self._name(item['system1'], item['key1'], item['value1'], item['system2'], item['key2'])
                if item['id1'] == id:
                    hash_name = self._name(self.request.input.system, self.request.input.key, self.request.input.value, item['system2'], item['key2'])
                else:
                    hash_name = self._name(item['system1'], item['key1'], item['value1'], self.request.input.system, self.request.input.key)
                    
                if existing_name == hash_name and item['value2'] == self.request.input:
                    continue
                
                if existing_name != hash_name:
                    self.server.kvdb.conn.renamenx(existing_name, hash_name)

                if item['id2'] == id:
                    self.server.kvdb.conn.hset(hash_name, 'value2', self.request.input.value)

class Delete(DataDictService):
    """ Deletes a dictionary entry by its ID.
    """
    class SimpleIO:
        input_required = ('id',)
        output_required = ('id',)
        
    def handle(self):
        id = str(self.request.input.id)
        self.server.kvdb.conn.hdel(KVDB.DICTIONARY_ITEM, id)
        for item in self._get_translations():
            if item['id1'] == id or item['id2'] == id:
                self.server.kvdb.conn.delete(self._name(item['system1'], item['key1'], item['value1'], item['system2'], item['key2']))
                
        self.response.payload.id = self.request.input.id
        
class _DictionaryEntryService(DataDictService):
    """ Base class for returning a list of systems, keys and values.
    """
    def get_data(self, needs_systems=False, by_system=None, by_key=None):
        for triple in self.server.kvdb.conn.hvals(KVDB.DICTIONARY_ITEM):
            system, key, value = triple.split(KVDB.SEPARATOR)
            if needs_systems:
                yield system
            elif by_system:
                if by_key:
                    if system == by_system and key == by_key:
                        yield value
                elif system == by_system:
                    yield key

class GetSystemList(_DictionaryEntryService):
    """ Returns a list of systems used in dictionaries.
    """
    class SimpleIO:
        output_required = ('name',)
        
    def handle(self):
        self.response.payload[:] = ({'name':elem} for elem in sorted(set(self.get_data(True))))

class GetKeyList(_DictionaryEntryService):
    """ Returns a list of keys used in a system's dictionary.
    """
    class SimpleIO:
        input_required = ('system',)
        output_required = ('name',)
        
    def handle(self):
        self.response.payload[:] = ({'name':elem} for elem in sorted(set(self.get_data(False, self.request.input.system))))

class GetValueList(_DictionaryEntryService):
    """ Returns a list of values used in a system dictionary's key.
    """
    class SimpleIO:
        input_required = ('system', 'key')
        output_required = ('name',)
        
    def handle(self):
        self.response.payload[:] = ({'name':elem} for elem in sorted(set(self.get_data(False, self.request.input.system, self.request.input.key))))

class GetLastID(AdminService):
    """ Returns the value of the last dictionary's ID or nothing at all if the key
    for holding its value doesn't exist.
    """
    class SimpleIO:
        output_optional = ('value',)
        
    def handle(self):
        self.response.payload.value = self.server.kvdb.conn.get(KVDB.DICTIONARY_ITEM_ID) or ''
