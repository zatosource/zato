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

# Zato
from zato.common import KVDB, ZatoException
from zato.server.service.internal import AdminService

# Zato Redis key layout
# TODO: Document it properly

#
# zato:kvdb:data-dict:item:id: '1'
#
# zato:kvdb:data-dict:item
# {
#  '1': 'ESB:::curreny::EUR',
#  '2': 'ESB:::currency:::JPY',
#  '3': 'ESB:::country_code:::CH',
#  '4': 'CRM:::CURRENCY:::978',
# }

#
# zato:kvdb:data-dict:translation:id: '1'
#
# 'zato:kvdb:data-dict:translation:::ESB:::currency:::EUR:::CRM:::CURRENCY':{'id':'1', 'item1':'1', 'item2':'4', 'value2':'978'}


class DataDictService(AdminService):
    def __init__(self, *args, **kwargs):
        super(DataDictService, self).__init__(*args, **kwargs)
        self._dict_items = []
        
    def _get_dict_items(self):
        if not self._dict_items:
            for id, item in self.server.kvdb.conn.hgetall(KVDB.DICTIONARY_ITEM).items():
                system, key, value = item.split(KVDB.SEPARATOR)
                self._dict_items.append({'id':id, 'system':system, 'key':key, 'value':value})
        for item in self._dict_items:
            yield item
            
    def _get_item_id(self, system, key, value):
        for item in self._get_dict_items():
            if item['system'] == system and item['key'] == key and item['value'] == value:
                return item['id']
            
    def _get_translations(self):
        for item in self.server.kvdb.conn.keys(KVDB.TRANSLATION + KVDB.SEPARATOR + '*'):
            vals = self.server.kvdb.conn.hgetall(item)
            item = item.split(KVDB.SEPARATOR)
            yield {'system1':item[1], 'key1':item[2], 'value1':item[3], 'system2':item[4], 
                   'key2':item[5], 'id':str(vals.get('id')), 'value2':vals.get('value2'),
                   'id1':str(vals.get('id1')), 'id2':str(vals.get('id2')),}
