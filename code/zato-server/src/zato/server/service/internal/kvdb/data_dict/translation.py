# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from hashlib import sha1, sha256

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode

# Zato
from zato.common.api import KVDB
from zato.common.exception import ZatoException
from zato.common.util.api import hexlify, multikeysort
from zato.server.service import Int
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO
from zato.server.service.internal.kvdb.data_dict import DataDictService

class _DeletingService(DataDictService):
    """ Subclasses of this class know how to delete a translation.
    """
    def delete(self, id):

        if not self.server.kvdb.conn:
            return

        for item in self._get_translations():
            if int(item['id']) == id:
                delete_key = KVDB.SEPARATOR.join((KVDB.TRANSLATION, item['system1'], item['key1'], item['value1'], item['system2'], item['key2']))
                self.server.kvdb.conn.delete(delete_key)

class GetList(DataDictService):
    """ Returns a list of translations.
    """
    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_kvdb_data_dict_translation_get_list_request'
        response_elem = 'zato_kvdb_data_dict_translation_get_list_response'
        output_required = ('id', 'system1', 'key1', 'value1', 'system2', 'key2', 'value2', 'id1', 'id2')

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
        if not self.server.kvdb.conn:
            return

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

        item_ids = self._get_item_ids()
        hash_name = self._name(system1, key1, value1, system2, key2)

        if self._validate_name(hash_name, system1, key1, value1, system2, key2, self.request.input.get('id')):
            self.response.payload.id = self._handle(hash_name, item_ids)

    def _handle(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented by a subclass')

    def _set_hash_fields(self, hash_name, item_ids):

        if not self.server.kvdb.conn:
            return

        self.server.kvdb.conn.hset(hash_name, 'id1', item_ids['id1'])
        self.server.kvdb.conn.hset(hash_name, 'id2', item_ids['id2'])
        self.server.kvdb.conn.hset(hash_name, 'value2', self.request.input.value2)

class Create(_CreateEdit):
    """ Creates a translation between dictionary entries.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_kvdb_data_dict_translation_create_request'
        response_elem = 'zato_kvdb_data_dict_translation_create_response'
        input_required = ('system1', 'key1', 'value1', 'system2', 'key2', 'value2')
        output_required = ('id',)

    def _handle(self, hash_name, item_ids):

        if not self.server.kvdb.conn:
            return

        id = self.server.kvdb.conn.incr(KVDB.TRANSLATION_ID)
        self.server.kvdb.conn.hset(hash_name, 'id', id)
        self._set_hash_fields(hash_name, item_ids)
        return id

class Edit(_CreateEdit):
    """ Updates a translation between dictionary entries.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_kvdb_data_dict_translation_edit_request'
        response_elem = 'zato_kvdb_data_dict_translation_edit_response'
        input_required = ('id', 'system1', 'key1', 'value1', 'system2', 'key2', 'value2')
        output_required = ('id',)

    def _handle(self, hash_name, item_ids):

        if not self.server.kvdb.conn:
            return

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
    class SimpleIO(AdminSIO):
        request_elem = 'zato_kvdb_data_dict_translation_delete_request'
        response_elem = 'zato_kvdb_data_dict_translation_delete_response'
        input_required = ('id',)

    def handle(self):
        self.delete(self.request.input.id)

class Translate(AdminService):
    """ Translates keys and values between systems.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_kvdb_data_dict_translation_translate_request'
        response_elem = 'zato_kvdb_data_dict_translation_translate_response'
        input_required = ('system1', 'key1', 'value1', 'system2', 'key2')
        output_optional = ('value2', 'repr', 'hex', 'sha1', 'sha256')

    def handle(self):
        result = self.translate(self.request.input.system1, self.request.input.key1, self.request.input.value1,
            self.request.input.system2, self.request.input.key2)

        if result:
            result = result if isinstance(result, unicode) else result.decode('utf-8')
            result_bytes = result.encode('utf8')
            self.response.payload.value2 = result
            self.response.payload.repr = repr(result)
            self.response.payload.hex = hexlify(result)
            self.response.payload.sha1 = sha1(result_bytes).hexdigest()
            self.response.payload.sha256 = sha256(result_bytes).hexdigest()

class GetLastID(AdminService):
    """ Returns the value of the last dictionary's ID or nothing at all if the key for holding its value doesn't exist.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_kvdb_data_dict_translation_get_last_id_request'
        response_elem = 'zato_kvdb_data_dict_translation_get_last_id_response'
        output_optional = (Int('value'),)

    def handle(self):
        if not self.server.kvdb.conn:
            return

        self.response.payload.value = self.server.kvdb.conn.get(KVDB.TRANSLATION_ID)
