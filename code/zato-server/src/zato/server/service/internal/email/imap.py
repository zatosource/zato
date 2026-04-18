# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from time import time
from traceback import format_exc

# Zato
from zato.common.api import EMAIL as EMail_Common, Zato_None
from zato.common.exception import BadRequest
from zato.server.service import AsIs, Bool, Int
from zato.server.service.internal import AdminService, ChangePasswordBase

# ################################################################################################################################
# ################################################################################################################################

_entity_type = 'email_imap'

# ################################################################################################################################
# ################################################################################################################################

def _item_by_id(items, id_):
    sid = str(id_)
    for item in items:
        if str(item.get('id')) == sid:
            return item
    return None

# ################################################################################################################################
# ################################################################################################################################

def _enrich_imap_list_item(item):
    out = dict(item)
    server_type = out.get('server_type')
    if not server_type:
        server_type = EMail_Common.IMAP.ServerType.Generic
        out['server_type'] = server_type
    out['server_type_human'] = EMail_Common.IMAP.ServerTypeHuman[server_type]
    if out.get('host') == Zato_None:
        out['host'] = ''
    gc = out.get('get_criteria', '')
    if not out.get('filter_criteria'):
        out['filter_criteria'] = gc
    return out

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of IMAP connections.
    """
    input = 'cluster_id'
    output = ('id', 'name', Bool('is_active'), 'host', Int('port'), Int('timeout'), Int('debug_level'), 'mode',
        'get_criteria', '-username', '-opaque1', '-server_type', '-server_type_human', AsIs('-tenant_id'),
        AsIs('-client_id'), '-filter_criteria')

    def handle(self):
        items = [_enrich_imap_list_item(dict(x)) for x in self.server.config_store.get_list(_entity_type)]
        self.response.payload = self._paginate_list(items)

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates an IMAP connection.
    """
    input = ('cluster_id', 'name', Bool('is_active'), 'host', Int('port'), Int('timeout'), Int('debug_level'),
        'mode', 'get_criteria', '-username', '-password', '-opaque1', '-server_type', AsIs('-tenant_id'),
        AsIs('-client_id'), '-filter_criteria')
    output = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.cluster_id = input.get('cluster_id') or self.server.cluster_id
        store = self.server.config_store

        if store.get(_entity_type, input.name):
            raise BadRequest(self.cid, 'An IMAP connection `{}` already exists in this cluster'.format(input.name))

        get_criteria = input.get('filter_criteria') or input.get_criteria
        host = input.host or Zato_None

        data = {
            'name': input.name,
            'is_active': input.is_active,
            'host': host,
            'port': int(input.port),
            'timeout': int(input.timeout),
            'debug_level': int(input.debug_level),
            'username': input.username or '',
            'password': input.password,
            'mode': input.mode,
            'get_criteria': get_criteria,
        }
        if input.get('opaque1') is not None:
            data['opaque1'] = input.opaque1
        if input.get('server_type') is not None:
            data['server_type'] = input.server_type
        if input.get('tenant_id') is not None:
            data['tenant_id'] = input.tenant_id
        if input.get('client_id') is not None:
            data['client_id'] = input.client_id

        store.set(_entity_type, input.name, data)
        saved = store.get(_entity_type, input.name) or data
        self.response.payload.id = saved.get('id', input.name)
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an IMAP connection.
    """
    input = ('id', 'cluster_id', 'name', Bool('is_active'), 'host', Int('port'), Int('timeout'),
        Int('debug_level'), 'mode', 'get_criteria', '-username', '-password', '-opaque1', '-server_type',
        AsIs('-tenant_id'), AsIs('-client_id'), '-filter_criteria')
    output = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.cluster_id = input.get('cluster_id') or self.server.cluster_id
        store = self.server.config_store

        old = _item_by_id(store.get_list(_entity_type), input.id)
        if not old:
            raise BadRequest(self.cid, 'No such an IMAP connection `{}` in this cluster'.format(input.name))

        old_name = old.get('name')
        if old_name != input.name:
            other = store.get(_entity_type, input.name)
            if other and str(other.get('id')) != str(input.id):
                raise BadRequest(self.cid, 'An IMAP connection `{}` already exists in this cluster'.format(input.name))

        get_criteria = input.get('filter_criteria') or input.get_criteria
        host = input.host or Zato_None

        data = dict(old)
        data.update({
            'id': old.get('id', input.id),
            'name': input.name,
            'is_active': input.is_active,
            'host': host,
            'port': int(input.port),
            'timeout': int(input.timeout),
            'debug_level': int(input.debug_level),
            'username': input.username or '',
            'mode': input.mode,
            'get_criteria': get_criteria,
        })
        if input.get('password') is not None:
            data['password'] = input.password
        if input.get('opaque1') is not None:
            data['opaque1'] = input.opaque1
        if input.get('server_type') is not None:
            data['server_type'] = input.server_type
        if input.get('tenant_id') is not None:
            data['tenant_id'] = input.tenant_id
        if input.get('client_id') is not None:
            data['client_id'] = input.client_id

        if old_name != input.name:
            store.delete(_entity_type, old_name)
        store.set(_entity_type, input.name, data)

        saved = store.get(_entity_type, input.name) or data
        self.response.payload.id = saved.get('id', input.id)
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an IMAP connection.
    """
    input = ('-id', '-name', '-should_raise_if_missing')

    def handle(self):
        input = self.request.input
        store = self.server.config_store
        input_id = input.get('id')
        input_name = input.get('name')

        if not (input_id or input_name):
            raise BadRequest(self.cid, 'Either id or name is required on input')

        item = None
        if input_id:
            item = _item_by_id(store.get_list(_entity_type), input_id)
        if not item and input_name:
            item = store.get(_entity_type, input_name)

        if not item:
            if input.get('should_raise_if_missing', True):
                attr_name = 'id' if input_id else 'name'
                attr_value = input_id if input_id else input_name
                raise BadRequest(self.cid, 'Could not find an IMAP connection instance with {} `{}`'.format(
                    attr_name, attr_value))
            return

        store.delete(_entity_type, item['name'])

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an IMAP connection.
    """
    password_required = False

    def handle(self):
        password = self.request.input.get('password', '')

        password_decrypted = self.server.decrypt(password) if password else password

        try:
            if self.password_required:
                if not password_decrypted:
                    raise Exception('Password must not be empty')

            instance_id = self.request.input.get('id')
            instance_name = self.request.input.name
            store = self.server.config_store

            item = None
            if instance_id:
                item = _item_by_id(store.get_list(_entity_type), instance_id)
            elif instance_name:
                item = store.get(_entity_type, instance_name)
            else:
                raise Exception('Either ID or name are required on input')

            if not item:
                raise Exception('Could not find instance with id:`{}` and name:`{}`'.format(instance_id, instance_name))

            name = item['name']
            data = dict(item)
            data['password'] = password_decrypted
            store.set(_entity_type, name, data)

            self.response.payload.id = item.get('id', instance_id)
        except Exception:
            self.logger.error('Could not update password, e:`%s`', format_exc())
            raise

# ################################################################################################################################
# ################################################################################################################################

class Ping(AdminService):
    """ Pings an IMAP connection to check its configuration.
    """
    input = 'id'
    output = '-info'

    def handle(self):
        item = _item_by_id(self.server.config_store.get_list(_entity_type), self.request.input.id)
        if not item:
            raise BadRequest(self.cid, 'Could not find IMAP connection with id `{}`'.format(self.request.input.id))

        start_time = time()

        if not self.email:
            self.response.payload.info = 'Could not ping connection; is component_enabled.email set to True in server.conf?'
        else:
            self.email.imap.get(item['name'], True).conn.ping()
            response_time = time() - start_time

            self.response.payload.info = 'Ping NOOP submitted, took:`{0:03.4f} s`, check server logs for details.'.format(
                response_time)

# ################################################################################################################################
