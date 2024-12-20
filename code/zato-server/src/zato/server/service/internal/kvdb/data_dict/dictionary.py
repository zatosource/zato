# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import re

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode

# Zato
from zato.common.api import KVDB
from zato.common.exception import ZatoException
from zato.common.util.api import dict_item_name
from zato.server.service import Int
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO
from zato.server.service.internal.kvdb.data_dict import DataDictService

class GetList(DataDictService):
    """ Returns a list of dictionary items.
    """
    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_kvdb_data_dict_dictionary_get_list_request'
        response_elem = 'zato_kvdb_data_dict_dictionary_get_list_response'
        output_required = 'id', 'system', 'key', 'value'

    def get_data(self):
        return self._get_dict_items()

    def handle(self):
        self.response.payload[:] = self.get_data()

class _CreateEdit(DataDictService):
    NAME_PATTERN = r'\w+' # noqa: W605
    NAME_RE = re.compile(NAME_PATTERN)

    class SimpleIO(AdminSIO):
        input_required = 'system', 'key', 'value'
        input_optional = 'id'
        output_optional = 'id'

    def _validate_entry(self, validate_item, id=None):
        for elem in('system', 'key'):
            name = self.request.input[elem]
            match = self.NAME_RE.match(name)
            if match and match.group() == name:
                continue
            else:
                msg = 'System and key may contain only letters, digits and an underscore, failed to validate `{}` ' + \
                       'against the regular expression {}'
                msg = msg.format(name, self.NAME_PATTERN)
                raise ZatoException(self.cid, msg)

        for item in self._get_dict_items():
            joined = KVDB.SEPARATOR.join((item['system'], item['key'], item['value']))
            if validate_item == joined and id != item['id']:
                msg = 'The triple of system:`{}`, key:`{}`, value:`{}` already exists'.format(
                    item['system'], item['key'], item['value'])
                raise ZatoException(self.cid, msg)

        return True

    def _get_item_name(self):
        return dict_item_name(self.request.input.system, self.request.input.key, self.request.input.value)

    def handle(self):

        if not self.server.kvdb.conn:
            return

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
    class SimpleIO(_CreateEdit.SimpleIO):
        request_elem = 'zato_kvdb_data_dict_dictionary_create_request'
        response_elem = 'zato_kvdb_data_dict_dictionary_create_response'

    def _handle(self, *ignored_args, **ignored_kwargs):
        pass

class Edit(_CreateEdit):
    """ Updates a dictionary entry.
    """
    class SimpleIO(_CreateEdit.SimpleIO):
        request_elem = 'zato_kvdb_data_dict_dictionary_edit_request'
        response_elem = 'zato_kvdb_data_dict_dictionary_edit_response'

    def _handle(self, id):

        if not self.server.kvdb.conn:
            return

        for item in self._get_translations():
            if item['id1'] == id or item['id2'] == id:
                existing_name = self._name(item['system1'], item['key1'], item['value1'], item['system2'], item['key2'])
                if item['id1'] == id:
                    hash_name = self._name(
                        self.request.input.system, self.request.input.key, self.request.input.value,
                        item['system2'], item['key2'])
                else:
                    hash_name = self._name(
                        item['system1'], item['key1'], item['value1'], self.request.input.system, self.request.input.key)

                if existing_name == hash_name and item['value2'] == self.request.input:
                    continue

                if existing_name != hash_name:
                    self.server.kvdb.conn.renamenx(existing_name, hash_name)

                if item['id2'] == id:
                    self.server.kvdb.conn.hset(hash_name, 'value2', self.request.input.value)

class Delete(DataDictService):
    """ Deletes a dictionary entry by its ID.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_kvdb_data_dict_dictionary_delete_request'
        response_elem = 'zato_kvdb_data_dict_dictionary_delete_response'
        input_required = 'id'
        output_optional = 'id'

    def handle(self):

        if not self.server.kvdb.conn:
            return

        id = str(self.request.input.id)
        self.server.kvdb.conn.hdel(KVDB.DICTIONARY_ITEM, id)
        for item in self._get_translations():
            if item['id1'] == id or item['id2'] == id:
                self.server.kvdb.conn.delete(
                    self._name(item['system1'], item['key1'], item['value1'], item['system2'], item['key2']))

        self.response.payload.id = self.request.input.id

class _DictionaryEntryService(DataDictService):
    """ Base class for returning a list of systems, keys and values.
    """
    def get_data(self, needs_systems=False, by_system=None, by_key=None):

        if not self.server.kvdb.conn:
            return

        for triple in self.server.kvdb.conn.hvals(KVDB.DICTIONARY_ITEM):

            triple = triple if isinstance(triple, unicode) else triple.decode('utf-8')
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
    class SimpleIO(AdminSIO):
        request_elem = 'zato_kvdb_data_dict_dictionary_get_system_list_request'
        response_elem = 'zato_kvdb_data_dict_dictionary_get_system_list_response'
        output_required = ('name',)

    def handle(self):
        self.response.payload[:] = ({'name':elem} for elem in sorted(set(self.get_data(True))))

class GetKeyList(_DictionaryEntryService):
    """ Returns a list of keys used in a system's dictionary.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_kvdb_data_dict_dictionary_get_key_list_request'
        response_elem = 'zato_kvdb_data_dict_dictionary_get_key_list_response'
        input_required = ('system',)
        output_required = ('name',)

    def handle(self):
        self.response.payload[:] = ({'name':elem} for elem in sorted(set(self.get_data(False, self.request.input.system))))

class GetValueList(_DictionaryEntryService):
    """ Returns a list of values used in a system dictionary's key.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_kvdb_data_dict_dictionary_get_value_list_request'
        response_elem = 'zato_kvdb_data_dict_dictionary_get_value_list_response'
        input_required = 'system', 'key'
        output_required = 'name'

    def handle(self):
        self.response.payload[:] = ({'name':elem} for elem in sorted(
            set(self.get_data(False, self.request.input.system, self.request.input.key))))

class GetLastID(AdminService):
    """ Returns the value of the last dictionary's ID or nothing at all if the key for holding its value doesn't exist.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_kvdb_data_dict_dictionary_get_last_id_request'
        response_elem = 'zato_kvdb_data_dict_dictionary_get_last_id_response'
        output_optional = Int('value')

    def handle(self):
        if not self.server.kvdb.conn:
            return

        self.response.payload.value = self.server.kvdb.conn.get(KVDB.DICTIONARY_ITEM_ID) or ''
