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

# Zato
from zato.common import KVDB, ZatoException
from zato.common.util import multikeysort
from zato.server.service.internal.kvdb.data_dict import DataDictService

class GetList(DataDictService):
    """ Returns a list of translations.
    """
    class SimpleIO:
        output_required = ('id', 'system1', 'key1', 'value1', 'system2', 'key2', 'value2')
        
    def get_data(self):
        return multikeysort(self._get_translations(), ['system1', 'key1', 'value1', 'system2', 'key2', 'value2'])

    def handle(self):
        self.response.payload[:] = self.get_data()

class Create(DataDictService):
    """ Creates translations translations between dictionary entries. Note that
    the reverse mapping is always created.
    """
    class SimpleIO:
        input_required = ('id', 'system1', 'key1', 'value1', 'system2', 'key2', 'value2')
        output_required = ('id',)
        
    def handle(self):
        system1 = self.request.input.system1
        key1 = self.request.input.key1
        value1 = self.request.input.value1
        system2 = self.request.input.system2
        key2 = self.request.input.key2
        value2 = self.request.input.value2
        item_ids = {'id1':None, 'id2':None}
        existing_ids = []
        
        hash_name = KVDB.SEPARATOR.join((KVDB.TRANSLATION, system1, key1, value1, system2, key2))
        if self.server.kvdb.conn.exists(hash_name):
            msg = 'A mapping between system1:[{}], key1:[{}], value1:[{}] and system2:[{}], key2:[{}] already exists'.format(
                system1, key1, value1, system2, key2)
            self.logger.error(msg)
            raise ZatoException(self.cid, msg)
        
        for item in self._get_dict_items():
            for idx in('1', '2'):
                system = self.request.input.get('system' + idx)
                key = self.request.input.get('key' + idx)
                value = self.request.input.get('value' + idx)
                
                if system == item['system'] and key == item['key'] and value == item['value']:
                    item_ids['id' + idx] = item['id']
         
        # This is a sanity check, in theory the input data can't possibly be outside
        # of what's in the KVDB.DICTIONARY_ITEM key
        for idx in('1', '2'):
            if not item_ids['id' + idx]:
                msg = 'Could not find the ID for system:[{}], key:[{}], value:[{}]'.format(
                    self.request.input.get('system' + idx), self.request.input.get('key' + idx),
                    self.request.input.get('value' + idx))
                raise ZatoException(self.cid, msg)

        for item in self._get_translations():
            existing_ids.append(item['id'])
            
        id = (max(int(elem) for elem in existing_ids) + 1) if existing_ids else 1
        
        self.server.kvdb.conn.hset(hash_name, 'id', id)
        self.server.kvdb.conn.hset(hash_name, 'item1', item_ids['id1'])
        self.server.kvdb.conn.hset(hash_name, 'item2', item_ids['id2'])
        self.server.kvdb.conn.hset(hash_name, 'value2', value2)
        
        self.response.payload.id = id


class Delete(DataDictService):
    """ Deletes a translation between dictionary entries.
    """
    class SimpleIO:
        input_required = ('id',)
        
    def handle(self):
        for item in self._get_translations():
            if int(item['id']) == self.request.input.id:
                delete_key = KVDB.SEPARATOR.join((KVDB.TRANSLATION, item['system1'], item['key1'], item['value1'], item['system2'], item['key2']))
                self.server.kvdb.conn.delete(delete_key)