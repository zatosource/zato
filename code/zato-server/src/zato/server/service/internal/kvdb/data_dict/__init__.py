# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode
from zato.common.ext.future.utils import iteritems

# Zato
from zato.common.api import KVDB
from zato.common.exception import ZatoException
from zato.common.util.api import multikeysort, translation_name
from zato.server.service.internal import AdminService

class DataDictService(AdminService):
    def __init__(self, *args, **kwargs):
        super(DataDictService, self).__init__(*args, **kwargs)
        self._dict_items = []

    def _name(self, system1, key1, value1, system2, key2):
        return translation_name(system1, key1, value1, system2, key2)

    def _get_dict_item(self, id):
        """ Returns a dictionary entry by its ID.
        """
        for item in self._get_dict_items():
            if item['id'] == str(id):
                return item
        else:
            msg = 'Could not find the dictionary by its ID:`{}`'.format(id)
            raise ZatoException(self.cid, msg)

    def _get_dict_items_raw(self):
        """ Yields dictionary items without formatting them into Python dictionaries.
        """
        conn = self.server.kvdb.conn
        if conn:
            for id, item in iteritems(conn.hgetall(KVDB.DICTIONARY_ITEM)):
                yield id, item

    def _get_dict_items(self):
        """ Yields nicely formatted dictionary items defined in the KVDB.
        """
        if not self._dict_items:
            conn = self.server.kvdb.conn
            if conn:
                for id, item in iteritems(conn.hgetall(KVDB.DICTIONARY_ITEM)):
                    item = item if isinstance(item, unicode) else item.decode('utf8')
                    system, key, value = item.split(KVDB.SEPARATOR)
                    self._dict_items.append({'id':str(id), 'system':system, 'key':key, 'value':value})
            self._dict_items = multikeysort(self._dict_items, ['system', 'key', 'value'])

        for item in self._dict_items:
            yield item

    def _get_dict_item_id(self, system, key, value):
        """ Returns a dictionary entry ID by its system, key and value.
        """
        for item in self._get_dict_items():
            if item['system'] == system and item['key'] == key and item['value'] == value:
                return item['id']

    def _get_translations(self):
        """ Yields nicely formatted translations defined in the KVDB.
        """
        conn = self.server.kvdb.conn

        if conn:
            for item in conn.keys(KVDB.TRANSLATION + KVDB.SEPARATOR + '*'):
                vals = conn.hgetall(item)
                item = item if isinstance(item, unicode) else item.decode('utf8')
                item = item.split(KVDB.SEPARATOR)

                value2 = vals.get('value2')
                value2 = value2 if isinstance(value2, unicode) else value2.decode('utf-8')

                yield {'system1':item[1], 'key1':item[2], 'value1':item[3], 'system2':item[4],
                       'key2':item[5], 'id':str(vals.get('id')), 'value2':value2,
                       'id1':str(vals.get('id1')), 'id2':str(vals.get('id2')),}
