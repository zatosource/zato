# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from operator import itemgetter
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common.api import ZATO_ODB_POOL_NAME
from zato.common.exception import ZatoException
from zato.common.util.api import get_sql_engine_display_name
from zato.server.service import AsIs, Integer
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################
# ################################################################################################################################

_entity_type = 'outgoing_sql'

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns a list of outgoing SQL connections.
    """
    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_outgoing_sql_get_list_request'
        response_elem = 'zato_outgoing_sql_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'cluster_id', 'engine', 'host', Integer('port'), 'db_name', 'username',
            Integer('pool_size'))
        output_optional = ('extra', 'engine_display_name')

    def handle(self):
        items = self.server.rust_config_store.get_list(_entity_type)
        for item in items:
            extra = item.get('extra', '')
            if isinstance(extra, bytes):
                item['extra'] = extra.decode('utf8')
            item['engine_display_name'] = get_sql_engine_display_name(
                item.get('engine', ''), self.server.fs_sql_config)
        self.response.payload[:] = items

# ################################################################################################################################
# ################################################################################################################################

class Create(AdminService):
    """ Creates a new outgoing SQL connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_sql_create_request'
        response_elem = 'zato_outgoing_sql_create_response'
        input_required = ('name', 'is_active', 'cluster_id', 'engine', 'host', Integer('port'), 'db_name', 'username',
            Integer('pool_size'))
        input_optional = ('extra',)
        output_required = ('id', 'name', 'display_name')

    def handle(self):
        input = self.request.input

        extra = input.extra or ''
        if extra and '=' not in extra:
            raise ZatoException(self.cid,
                'extra should be a list of key=value parameters, possibly one-element long, instead of `{}`'.format(extra))

        data = {
            'name': input.name,
            'is_active': input.is_active,
            'engine': input.engine,
            'host': input.host,
            'port': input.port,
            'db_name': input.db_name,
            'username': input.username,
            'password': uuid4().hex,
            'pool_size': input.pool_size,
            'extra': extra,
        }

        name = input.name
        self.server.rust_config_store.set(_entity_type, name, data)

        self.response.payload.id = data.get('id', name)
        self.response.payload.name = name
        self.response.payload.display_name = get_sql_engine_display_name(input.engine, self.server.fs_sql_config)

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    """ Updates an outgoing SQL connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_sql_edit_request'
        response_elem = 'zato_outgoing_sql_edit_response'
        input_required = ('id', 'name', 'is_active', 'cluster_id', 'engine', 'host', Integer('port'), 'db_name', 'username',
            Integer('pool_size'))
        input_optional = ('extra',)
        output_required = ('id', 'name', 'display_name')

    def handle(self):
        input = self.request.input

        extra = input.extra or ''
        if extra and '=' not in extra:
            raise ZatoException(self.cid,
                'extra should be a list of key=value parameters, possibly one-element long, instead of `{}`'.format(extra))

        target_id = str(input.id)
        old_name = None
        existing = None
        for item in self.server.rust_config_store.get_list(_entity_type):
            if str(item.get('id')) == target_id:
                old_name = item['name']
                existing = self.server.rust_config_store.get(_entity_type, old_name)
                if not existing:
                    existing = dict(item)
                break
        if not old_name or not existing:
            raise Exception('Outgoing SQL connection with id `{}` not found'.format(target_id))

        existing.update({
            'id': input.id,
            'name': input.name,
            'is_active': input.is_active,
            'engine': input.engine,
            'host': input.host,
            'port': input.port,
            'db_name': input.db_name,
            'username': input.username,
            'pool_size': input.pool_size,
            'extra': extra,
        })

        if old_name != input.name:
            self.server.rust_config_store.delete(_entity_type, old_name)

        self.server.rust_config_store.set(_entity_type, input.name, existing)

        self.response.payload.id = existing.get('id', input.name)
        self.response.payload.name = input.name
        self.response.payload.display_name = get_sql_engine_display_name(input.engine, self.server.fs_sql_config)

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes an outgoing SQL connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_sql_delete_request'
        response_elem = 'zato_outgoing_sql_delete_response'
        input_required = ('id',)

    def handle(self):
        target_id = str(self.request.input.id)
        for item in self.server.rust_config_store.get_list(_entity_type):
            if str(item.get('id')) == target_id or item.get('name') == target_id:
                self.server.rust_config_store.delete(_entity_type, item['name'])
                return
        raise Exception('Outgoing SQL connection with id `{}` not found'.format(target_id))

# ################################################################################################################################
# ################################################################################################################################

class ChangePassword(AdminService):
    """ Changes the password of an outgoing SQL connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_sql_change_password_request'
        response_elem = 'zato_outgoing_sql_change_password_response'
        input_required = 'id', 'password1', 'password2'

    def handle(self):
        input = self.request.input
        target_id = str(input.id)
        items = self.server.rust_config_store.get_list(_entity_type)
        for item in items:
            if str(item.get('id')) == target_id or item.get('name') == target_id:
                item['password'] = input.password1
                self.server.rust_config_store.set(_entity_type, item['name'], item)
                return

# ################################################################################################################################
# ################################################################################################################################

class Ping(AdminService):
    """ Pings an SQL database
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_sql_ping_request'
        response_elem = 'zato_outgoing_sql_ping_response'
        input_required = 'id', 'should_raise_on_error'
        output_optional = 'id', 'response_time'

    def handle(self):
        target_id = str(self.request.input.id)
        items = self.server.rust_config_store.get_list(_entity_type)

        item_name = None
        for item in items:
            if str(item.get('id')) == target_id or item.get('name') == target_id:
                item_name = item['name']
                break

        if not item_name:
            raise Exception('Could not find SQL connection with id `{}`'.format(target_id))

        try:
            ping = self.outgoing.sql.get(item_name, False).pool.ping
            self.response.payload.id = self.request.input.id
            response_time = ping(self.server.fs_sql_config)
            if response_time:
                self.response.payload.response_time = str(response_time)
        except Exception as e:
            log_msg = 'SQL connection `{}` could not be pinged, e:`{}`'
            if self.request.input.should_raise_on_error:
                self.logger.warning(log_msg.format(item_name, format_exc()))
                raise e
            else:
                self.logger.warning(log_msg.format(item_name, e.args[0]))

# ################################################################################################################################
# ################################################################################################################################

class AutoPing(AdminService):
    """ Invoked periodically from the scheduler - pings all the existing SQL connections.
    """
    def handle(self):
        try:
            self.server.sql_pool_store[ZATO_ODB_POOL_NAME].pool.ping(self.server.fs_sql_config)
        except Exception:
            self.logger.warning('Could not ping ODB, e:`%s`', format_exc())

        response = self.invoke(GetList.get_name(), {'cluster_id':self.server.cluster_id})
        response = response['zato_outgoing_sql_get_list_response']

        for item in response:
            if not item.get('is_active'):
                continue
            try:
                self.invoke(Ping.get_name(), {
                    'id': item['id'],
                    'should_raise_on_error': False,
                })
            except Exception:
                self.logger.warning('Could not auto-ping SQL pool `%s`, config:`%s`, e:`%s`', item['name'], item, format_exc())

# ################################################################################################################################
# ################################################################################################################################

class GetEngineList(AdminService):
    """ Returns a list of all engines defined in sql.conf.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_sql_get_engine_list_request'
        response_elem = 'zato_outgoing_sql_get_engine_list_response'
        output_required = (AsIs('id'), 'name')
        output_repeated = True

    def get_data(self):
        out = []
        for id, value in self.server.fs_sql_config.items():
            out.append({
                'id': id,
                'name': value['display_name']
            })
        return sorted(out, key=itemgetter('name'))

    def handle(self):
        self.response.payload[:] = self.get_data()

# ################################################################################################################################
# ################################################################################################################################
