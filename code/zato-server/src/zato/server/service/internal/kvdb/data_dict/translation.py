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
from hashlib import sha1, sha256

# Zato
from zato.common import KVDB, ZatoException
from zato.common.util import grouper, multikeysort
from zato.server.service.internal import AdminService
from zato.server.service.internal.kvdb.data_dict import DataDictService

class _DeletingService(DataDictService):
    """ Subclasses of this class know how to delete a translation.
    """
    def delete(self, id):
        for item in self._get_translations():
            if int(item['id']) == id:
                delete_key = KVDB.SEPARATOR.join((KVDB.TRANSLATION, item['system1'], item['key1'], item['value1'], item['system2'], item['key2']))
                self.server.kvdb.conn.delete(delete_key)

class GetList(DataDictService):
    """ Returns a list of translations.
    """
    class SimpleIO:
        output_required = ('id', 'system1', 'key1', 'value1', 'system2', 'key2', 'value2')
        
    def get_data(self):
        return multikeysort(self._get_translations(), ['system1', 'key1', 'value1', 'system2', 'key2', 'value2'])

    def handle(self):
        self.response.payload[:] = self.get_data()
        
class _CreateEdit(DataDictService):
    """ A base class for both Create and Edit actions.
    """
    def _validate_name(self, name, system1, key1, value1, system2, key2, id):
        """ Makes sure the translation doesn't already exist.
        """
        def _exception():
            msg = 'A mapping between system1:[{}], key1:[{}], value1:[{}] and system2:[{}], key2:[{}] already exists'.format(
                system1, key1, value1, system2, key2)
            self.logger.error(msg)
            raise ZatoException(self.cid, msg)

        if self.server.kvdb.conn.exists(name):
            # No ID means it's a Create so it's a genuine match of an existing mapping
            if not id:
                _exception()
            
            # We've got an ID so it's an Edit and we need ignore it if we're
            # editing ourself.
            existing_id = self.server.kvdb.conn.hget(name, 'id')
            if not str(existing_id) == str(id):
                _exception()

        return True
        
    def _get_item_ids(self):
        """ Returns IDs of the dictionary entries used in the translation.
        """
        item_ids = {'id1':None, 'id2':None}
        
        for idx in('1', '2'):
            system = self.request.input.get('system' + idx)
            key = self.request.input.get('key' + idx)
            value = self.request.input.get('value' + idx)
            item_ids['id' + idx] = self._get_dict_item_id(system, key, value)
         
        # This is a sanity check, in theory the input data can't possibly be outside
        # of what's in the KVDB.DICTIONARY_ITEM key
        for idx in('1', '2'):
            if not item_ids['id' + idx]:
                msg = 'Could not find the ID for system:[{}], key:[{}], value:[{}]'.format(
                    self.request.input.get('system' + idx), self.request.input.get('key' + idx),
                    self.request.input.get('value' + idx))
                raise ZatoException(self.cid, msg)
            
        return item_ids
    
    def handle(self):
        system1 = self.request.input.system1
        key1 = self.request.input.key1
        value1 = self.request.input.value1
        system2 = self.request.input.system2
        key2 = self.request.input.key2
        value2 = self.request.input.value2
        
        item_ids = self._get_item_ids()
        hash_name = self._name(system1, key1, value1, system2, key2)
        
        if self._validate_name(hash_name, system1, key1, value1, system2, key2, self.request.input.get('id')):
            self.response.payload.id = self._handle(hash_name, item_ids)
            
    def _handle(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by a subclass')
    
    def _set_hash_fields(self, hash_name, item_ids):
        self.server.kvdb.conn.hset(hash_name, 'id1', item_ids['id1'])
        self.server.kvdb.conn.hset(hash_name, 'id2', item_ids['id2'])
        self.server.kvdb.conn.hset(hash_name, 'value2', self.request.input.value2)
            
class Create(_CreateEdit):
    """ Creates a translation between dictionary entries.
    """
    class SimpleIO:
        input_required = ('id', 'system1', 'key1', 'value1', 'system2', 'key2', 'value2')
        output_required = ('id',)
        
    def _handle(self, hash_name, item_ids):
        id = self.server.kvdb.conn.incr(KVDB.TRANSLATION_ID)
        self.server.kvdb.conn.hset(hash_name, 'id', id)
        self._set_hash_fields(hash_name, item_ids)
        return id
    
class Edit(_CreateEdit):
    """ Updates a translation between dictionary entries.
    """
    class SimpleIO:
        input_required = ('id', 'system1', 'key1', 'value1', 'system2', 'key2', 'value2')
        output_required = ('id',)
        
    def _handle(self, hash_name, item_ids):
        for item in self._get_translations():
            if item['id'] == str(self.request.input.id):
                existing_name = self._name(item['system1'], item['key1'], item['value1'], item['system2'], item['key2'])
                if existing_name != hash_name:
                    self.server.kvdb.conn.renamenx(existing_name, hash_name)
                    self._set_hash_fields(hash_name, item_ids)
                break

        return self.request.input.id

class Delete(_DeletingService):
    """ Deletes a translation between dictionary entries.
    """
    class SimpleIO:
        input_required = ('id',)
        
    def handle(self):
        self.delete(self.request.input.id)

class Translate(AdminService):
    class SimpleIO:
        input_required = ('system1', 'key1', 'value1', 'system2', 'key2')
        output_optional = ('value2', 'repr', 'hex', 'sha1', 'sha256')
        
    def handle(self):
        result = self.translate(self.request.input.system1, self.request.input.key1, self.request.input.value1, 
            self.request.input.system2, self.request.input.key2)
        
        if result:
            self.response.payload.value2 = result
            self.response.payload.repr = repr(result)
            self.response.payload.hex = ' '.join([elem1+elem2 for (elem1, elem2) in grouper(2, result.encode('hex'))])
            self.response.payload.sha1 = sha1(result).hexdigest()
            self.response.payload.sha256 = sha256(result).hexdigest()
