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

# anyjson
from anyjson import loads

# Zato
from zato.common import KVDB
from zato.common.util import dict_item_name, translation_name
from zato.server.service.internal.kvdb.data_dict import DataDictService

class Import(DataDictService):
    """ Imports a bz2-compressed JSON document containing data dictionaries replacing
    any other existing ones.
    """
    class SimpleIO:
        input_required = ('data',)
        
    def handle(self):
        data = loads(self.request.input.data.decode('base64').decode('bz2'))
        with self.server.kvdb.conn.pipeline() as p:
            p.delete(KVDB.DICTIONARY_ITEM_ID)
            p.delete(KVDB.DICTIONARY_ITEM)
            p.delete(KVDB.TRANSLATION_ID)
            
            for item in self._get_translations():
                key = translation_name(item['system1'], item['key1'], item['value1'], item['system2'], item['key2'])
                p.delete(key)
                
            # Another proof software engineering and philosophy have /a lot/ in common!
            data = data['data'] 
            
            p.set(KVDB.DICTIONARY_ITEM_ID, data['last_dict_id'])
            p.set(KVDB.TRANSLATION_ID, data['last_translation_id'])
            
            for item in data['dict_list']:
                p.hset(KVDB.DICTIONARY_ITEM, item['id'], dict_item_name(item['system'], item['key'], item['value']))
                
            for item in data['translation_list']:
                key = item.keys()[0]
                for value_key, value in item[key].items():
                    p.hset(key, value_key, value)
                
            p.execute()
