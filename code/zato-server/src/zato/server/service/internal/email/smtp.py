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
from zato.common.api import SMTPMessage
from zato.common.exception import BadRequest
from zato.common.version import get_version
from zato.server.service import Bool, Int
from zato.server.service.internal import AdminService, ChangePasswordBase

# ################################################################################################################################
# ################################################################################################################################

_entity_type = 'email_smtp'
version = get_version()

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

class GetList(AdminService):
    """ Returns a list of SMTP connections.
    """
    input = 'cluster_id'
    output = ('id', 'name', Bool('is_active'), 'host', Int('port'), Int('timeout'), Bool('is_debug'), 'mode',
        'ping_address', '-username', '-opaque1')

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates an SMTP connection.
    """
    input = ('cluster_id', 'name', Bool('is_active'), 'host', Int('port'), Int('timeout'), Bool('is_debug'),
        'mode', 'ping_address', '-username', '-password', '-opaque1')
    output = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.cluster_id = input.get('cluster_id') or self.server.cluster_id
        store = self.server.config_store

        if store.get(_entity_type, input.name):
            raise BadRequest(self.cid, 'An SMTP connection `{}` already exists in this cluster'.format(input.name))

        data = {
            'name': input.name,
            'is_active': input.is_active,
            'host': input.host,
            'port': int(input.port),
            'timeout': int(input.timeout),
            'is_debug': input.is_debug,
            'username': input.username or '',
            'password': input.password,
            'mode': input.mode,
            'ping_address': input.ping_address,
        }
        if input.get('opaque1') is not None:
            data['opaque1'] = input.opaque1

        store.set(_entity_type, input.name, data)
        saved = store.get(_entity_type, input.name) or data
        self.response.payload.id = saved.get('id', input.name)
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an SMTP connection.
    """
    input = ('id', 'cluster_id', 'name', Bool('is_active'), 'host', Int('port'), Int('timeout'),
        Bool('is_debug'), 'mode', 'ping_address', '-username', '-password', '-opaque1')
    output = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.cluster_id = input.get('cluster_id') or self.server.cluster_id
        store = self.server.config_store

        old = _item_by_id(store.get_list(_entity_type), input.id)
        if not old:
            raise BadRequest(self.cid, 'No such an SMTP connection `{}` in this cluster'.format(input.name))

        old_name = old.get('name')
        if old_name != input.name:
            other = store.get(_entity_type, input.name)
            if other and str(other.get('id')) != str(input.id):
                raise BadRequest(self.cid, 'An SMTP connection `{}` already exists in this cluster'.format(input.name))

        data = dict(old)
        data.update({
            'id': old.get('id', input.id),
            'name': input.name,
            'is_active': input.is_active,
            'host': input.host,
            'port': int(input.port),
            'timeout': int(input.timeout),
            'is_debug': input.is_debug,
            'username': input.username or '',
            'mode': input.mode,
            'ping_address': input.ping_address,
        })
        if input.get('password') is not None:
            data['password'] = input.password
        if input.get('opaque1') is not None:
            data['opaque1'] = input.opaque1

        if old_name != input.name:
            store.delete(_entity_type, old_name)
        store.set(_entity_type, input.name, data)

        saved = store.get(_entity_type, input.name) or data
        self.response.payload.id = saved.get('id', input.id)
        self.response.payload.name = input.name

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an SMTP connection.
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
                raise BadRequest(self.cid, 'Could not find an SMTP connection instance with {} `{}`'.format(
                    attr_name, attr_value))
            return

        store.delete(_entity_type, item['name'])

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an SMTP connection.
    """
    password_required = False

    def handle(self):
        password1 = self.request.input.get('password1', '')
        password2 = self.request.input.get('password2', '')

        password1_decrypted = self.server.decrypt(password1) if password1 else password1
        password2_decrypted = self.server.decrypt(password2) if password2 else password2

        try:
            if self.password_required:
                if not password1_decrypted:
                    raise Exception('Password must not be empty')
                if not password2_decrypted:
                    raise Exception('Password must be repeated')

            if password1_decrypted != password2_decrypted:
                raise Exception('Passwords need to be the same')

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
            data['password'] = password1_decrypted
            store.set(_entity_type, name, data)

            self.response.payload.id = item.get('id', instance_id)
        except Exception:
            self.logger.error('Could not update password, e:`%s`', format_exc())
            raise

# ################################################################################################################################
# ################################################################################################################################

class Ping(AdminService):
    """ Pings an SMTP connection to check its configuration.
    """
    input = 'id'
    output = 'info'

    def handle(self):
        item = _item_by_id(self.server.config_store.get_list(_entity_type), self.request.input.id)
        if not item:
            raise BadRequest(self.cid, 'Could not find SMTP connection with id `{}`'.format(self.request.input.id))

        msg = SMTPMessage()
        msg.from_ = item['ping_address']
        msg.to = item['ping_address']
        msg.cc = item['ping_address']
        msg.bcc = item['ping_address']
        msg.subject = 'Zato SMTP ping (Α Β Γ Δ Ε Ζ Η)'
        msg.headers['Charset'] = 'utf-8'

        msg.body = 'Hello from {}\nUTF-8 test: Α Β Γ Δ Ε Ζ Η'.format(version).encode('utf-8')

        msg.attach('utf-8.txt', 'Α Β Γ Δ Ε Ζ Η Θ Ι Κ Λ Μ Ν Ξ Ο Π Ρ Σ Τ Υ Φ Χ Ψ Ω'.encode('utf-8'))
        msg.attach('ascii.txt', 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z')

        start_time = time()
        self.email.smtp.get(item['name'], True).conn.send(msg)
        response_time = time() - start_time

        self.response.payload.info = 'Ping submitted, took:`{0:03.4f} s`, check server logs for details.'.format(response_time)

# ################################################################################################################################
