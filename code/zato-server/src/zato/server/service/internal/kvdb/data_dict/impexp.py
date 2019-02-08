# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from base64 import b64decode

# anyjson
from anyjson import loads

# Python 2/3 compatibility
from future.utils import iteritems

# Zato
from zato.common import KVDB
from zato.common.util import dict_item_name, translation_name
from zato.server.service.internal import AdminSIO
from zato.server.service.internal.kvdb.data_dict import DataDictService

class Import(DataDictService):
    """ Imports a bz2-compressed JSON document containing data dictionaries replacing any other existing ones.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_kvdb_data_dict_impexp_import_request'
        response_elem = 'zato_kvdb_data_dict_impexp_import_response'
        input_required = ('data',)

    def handle(self):
        data = self.request.input.data
        data = b64decode(data)
        data = data.decode('bz2')
        data = loads(data)
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

            if data['last_translation_id']:
                p.set(KVDB.TRANSLATION_ID, data['last_translation_id'])

            for item in data['dict_list']:
                p.hset(KVDB.DICTIONARY_ITEM, item['id'], dict_item_name(item['system'], item['key'], item['value']))

            for item in data['translation_list']:
                key = item.keys()[0]
                for value_key, value in iteritems(item[key]):
                    p.hset(key, value_key, value)

            p.execute()
