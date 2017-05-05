# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc
from uuid import uuid4

# Zato
from zato.common import ZatoException, ZATO_ODB_POOL_NAME
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import SQLConnectionPool, Cluster
from zato.common.odb.query import out_sql_list
from zato.server.service import Integer
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO


class _SQLService(object):
    """ A common class for various SQL-related services.
    """

    def notify_worker_threads(self, params, action=OUTGOING.SQL_CREATE_EDIT.value):
        """ Notify worker threads of new or updated parameters.
        """
        params['action'] = action
        self.broker_client.publish(params)

    def validate_extra(self, cid, extra):
        if extra and not b'=' in extra:
            raise ZatoException(
                cid, 'extra should be a list of key=value parameters, possibly one-element long, instead of [{}]'.format(extra.decode('utf-8')))


class GetList(AdminService):
    """ Returns a list of outgoing SQL connections.
    """
    _filter_by = SQLConnectionPool.name,

    class SimpleIO(GetListAdminSIO):
        request_elem = 'zato_outgoing_sql_get_list_request'
        response_elem = 'zato_outgoing_sql_get_list_response'
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'cluster_id', 'engine', 'host', Integer(
            'port'), 'db_name', 'username', Integer('pool_size'))
        output_optional = ('extra',)

    def get_data(self, session):
        return self._search(out_sql_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)


class Create(AdminService, _SQLService):
    """ Creates a new outgoing SQL connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_sql_create_request'
        response_elem = 'zato_outgoing_sql_create_response'
        input_required = ('name', 'is_active', 'cluster_id', 'engine', 'host', Integer(
            'port'), 'db_name', 'username', Integer('pool_size'))
        input_optional = ('extra',)
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.password = uuid4().hex
        input.extra = input.extra.encode('utf-8') if input.extra else b''

        self.validate_extra(self.cid, input.extra.decode('utf-8'))

        with closing(self.odb.session()) as session:
            existing_one = session.query(SQLConnectionPool.id).\
                filter(SQLConnectionPool.cluster_id == input.cluster_id).\
                filter(SQLConnectionPool.name == input.name).\
                first()

            if existing_one:
                raise Exception('An outgoing SQL connection [{0}] already exists on this cluster'.format(input.name))

            try:
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).first()
                item = SQLConnectionPool(cluster=cluster)
                item.name = input.name
                item.is_active = input.is_active
                #item.cluster_id = input.cluster_id
                item.engine = input.engine
                item.host = input.host
                item.port = input.port
                item.db_name = input.db_name
                item.username = input.username
                item.password = input.password
                item.pool_size = input.pool_size
                item.extra = input.extra

                session.add(item)
                session.commit()

                self.notify_worker_threads(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception, e:
                msg = 'Could not create an outgoing SQL connection, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise


class Edit(AdminService, _SQLService):
    """ Updates an outgoing SQL connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_sql_edit_request'
        response_elem = 'zato_outgoing_sql_edit_response'
        input_required = ('id', 'name', 'is_active', 'cluster_id', 'engine', 'host', Integer(
            'port'), 'db_name', 'username', Integer('pool_size'))
        input_optional = ('extra',)
        output_required = ('id', 'name')

    def handle(self):
        input = self.request.input
        input.extra = input.extra.encode('utf-8') if input.extra else ''

        self.validate_extra(self.cid, input.extra)

        with closing(self.odb.session()) as session:
            existing_one = session.query(SQLConnectionPool.id).\
                filter(SQLConnectionPool.cluster_id == input.cluster_id).\
                filter(SQLConnectionPool.name == input.name).\
                filter(SQLConnectionPool.id != input.id).\
                first()

            if existing_one:
                raise Exception('An outgoing SQL connection [{0}] already exists on this cluster'.format(input.name))

            try:
                item = session.query(SQLConnectionPool).filter_by(id=input.id).one()
                old_name = item.name
                item.name = input.name
                item.is_active = input.is_active
                item.cluster_id = input.cluster_id
                item.engine = input.engine
                item.host = input.host
                item.port = input.port
                item.db_name = input.db_name
                item.username = input.username
                item.pool_size = input.pool_size
                item.extra = input.extra

                session.add(item)
                session.commit()

                input.password = item.password
                input.old_name = old_name
                self.notify_worker_threads(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name

            except Exception, e:
                msg = 'Could not update the outgoing SQL connection, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise


class Delete(AdminService, _SQLService):
    """ Deletes an outgoing SQL connection.
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_sql_delete_request'
        response_elem = 'zato_outgoing_sql_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(SQLConnectionPool).\
                    filter(SQLConnectionPool.id == self.request.input.id).\
                    one()
                old_name = item.name

                session.delete(item)
                session.commit()

                self.notify_worker_threads({'name': old_name}, OUTGOING.SQL_DELETE.value)

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the outgoing SQL connection, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise


class ChangePassword(ChangePasswordBase):
    """ Changes the password of an outgoing SQL connection. The underlying implementation
    will actually stop and recreate the connection using the new password.
    """
    class SimpleIO(ChangePasswordBase.SimpleIO):
        request_elem = 'zato_outgoing_sql_change_password_request'
        response_elem = 'zato_outgoing_sql_change_password_response'

    def handle(self):
        def _auth(instance, password):
            instance.password = password

        self._handle(SQLConnectionPool, _auth, OUTGOING.SQL_CHANGE_PASSWORD.value)


class Ping(AdminService):
    """ Pings an SQL database
    """
    class SimpleIO(AdminSIO):
        request_elem = 'zato_outgoing_sql_ping_request'
        response_elem = 'zato_outgoing_sql_ping_response'
        input_required = ('id',)
        output_optional = ('response_time',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(SQLConnectionPool).\
                    filter(SQLConnectionPool.id == self.request.input.id).\
                    one()

                self.response.payload.response_time = str(self.outgoing.sql.get(item.name, False).pool.ping())

            except Exception, e:
                session.rollback()
                msg = 'Could not ping the outgoing SQL connection, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise


class AutoPing(AdminService):
    """ Invoked periodically from the scheduler - pings all the existing SQL connections.
    """

    def handle(self):
        try:
            self.server.sql_pool_store[ZATO_ODB_POOL_NAME].pool.ping()
        except Exception, e:
            self.logger.warn('Could not ping ODB, e:`%s`', format_exc(e))

        for item in self.invoke(GetList.get_name(), {'cluster_id': self.server.cluster_id})['zato_outgoing_sql_get_list_response']:
            try:
                self.invoke(Ping.get_name(), {'id': item['id']})
            except Exception, e:
                self.logger.warn('Could not ping SQL pool `%s`, config:`%s`, e:`%s`', item['name'], item, format_exc(e))
