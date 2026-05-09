# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing
from operator import itemgetter
from traceback import format_exc
from uuid import uuid4

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode

# Zato
from zato.common.api import ZATO_ODB_POOL_NAME
from zato.common.exception import ZatoException
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import Cluster, SQLConnectionPool
from zato.common.odb.query import out_sql_list
from zato.common.util.api import get_sql_engine_display_name
from zato.server.service import AsIs, Integer
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO

class _SQLService:
    """ A common class for various SQL-related services.
    """
    def notify_server(self, params, action=OUTGOING.SQL_CREATE_EDIT.value):
        """ Notify the server of new or updated parameters.
        """
        params['action'] = action
        self.config_dispatcher.publish(params)

    def validate_extra(self, cid, extra):
        if extra and not '=' in extra:
            raise ZatoException(cid,
                'extra should be a list of key=value parameters, possibly one-element long, instead of `{}`'.format(
                    extra))

class GetList(AdminService):
    """ Returns a list of outgoing SQL connections.
    """
    _filter_by = SQLConnectionPool.name,

    input = 'cluster_id',
    output = 'id', 'name', 'is_active', 'cluster_id', 'engine', 'host', Integer('port'), 'db_name', 'username', \
        Integer('pool_size'), '-extra', '-engine_display_name'

    def get_data(self, session):
        return self._search(out_sql_list, session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            data = self.get_data(session)
            for item in data:
                item.extra = item.extra.decode('utf8') if isinstance(item.extra, bytes) else item.extra
                item.engine_display_name = get_sql_engine_display_name(item.engine, self.server.fs_sql_config)
            self.response.payload[:] = data

class Create(AdminService, _SQLService):
    """ Creates a new outgoing SQL connection.
    """
    input = 'name', 'is_active', 'cluster_id', 'engine', 'host', Integer('port'), 'db_name', 'username', \
        Integer('pool_size'), '-extra'
    output = 'id', 'name', 'display_name'

    def handle(self):
        input = self.request.input
        input.password = uuid4().hex
        input.extra = input.extra.encode('utf-8') if input.extra else b''

        self.validate_extra(self.cid, input.extra.decode('utf-8'))

        with closing(self.odb.session()) as session:
            existing_one = session.query(SQLConnectionPool.id).\
                filter(SQLConnectionPool.cluster_id==input.cluster_id).\
                filter(SQLConnectionPool.name==input.name).\
                first()

            if existing_one:
                raise Exception('An outgoing SQL connection [{0}] already exists on this cluster'.format(input.name))

            try:
                cluster = session.query(Cluster).filter_by(id=input.cluster_id).one()
                item = SQLConnectionPool(cluster=cluster)
                item.name = input.name
                item.is_active = input.is_active
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

                # Make sure not to use bytes when notifying other threads
                input.extra = input.extra.decode('utf8') if isinstance(input.extra, bytes) else input.extra

                self.notify_server(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name
                self.response.payload.display_name = get_sql_engine_display_name(input.engine, self.server.fs_sql_config)

            except Exception:
                self.logger.error('SQL connection could not be created, e:`{}`', format_exc())
                session.rollback()

                raise

class Edit(AdminService, _SQLService):
    """ Updates an outgoing SQL connection.
    """
    input = 'id', 'name', 'is_active', 'cluster_id', 'engine', 'host', Integer('port'), 'db_name', 'username', \
        Integer('pool_size'), '-extra'
    output = 'id', 'name', 'display_name'

    def handle(self):
        input = self.request.input
        input.extra = input.extra.encode('utf-8') if input.extra else b''

        self.validate_extra(self.cid, input.extra.decode('utf-8'))

        with closing(self.odb.session()) as session:
            existing_one = session.query(SQLConnectionPool.id).\
                filter(SQLConnectionPool.cluster_id==input.cluster_id).\
                filter(SQLConnectionPool.name==input.name).\
                filter(SQLConnectionPool.id!=input.id).\
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
                item.extra = input.extra.encode('utf8') if isinstance(input.extra, unicode) else input.extra

                session.add(item)
                session.commit()

                input.password = item.password
                input.old_name = old_name

                # Make sure not to use bytes when notifying other threads
                input.extra = input.extra.decode('utf8') if isinstance(input.extra, bytes) else input.extra

                self.notify_server(input)

                self.response.payload.id = item.id
                self.response.payload.name = item.name
                self.response.payload.display_name = get_sql_engine_display_name(input.engine, self.server.fs_sql_config)

            except Exception:
                self.logger.error('SQL connection could not be updated, e:`{}`', format_exc())
                session.rollback()

                raise

class Delete(AdminService, _SQLService):
    """ Deletes an outgoing SQL connection.
    """
    input = 'id',

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(SQLConnectionPool).\
                    filter(SQLConnectionPool.id==self.request.input.id).\
                    one()
                old_name = item.name

                session.delete(item)
                session.commit()

                self.notify_server({'name':old_name}, OUTGOING.SQL_DELETE.value)

            except Exception:
                session.rollback()
                self.logger.error('SQL connection could not be deleted, e:`{}`', format_exc())

                raise

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an outgoing SQL connection.
    """
    def handle(self):
        def _auth(instance, password):
            instance.password = password

        self._handle(SQLConnectionPool, _auth, OUTGOING.SQL_CHANGE_PASSWORD.value)

class Ping(AdminService):
    """ Pings an SQL database
    """
    input = 'id', 'should_raise_on_error'
    output = '-id', '-response_time'

    def handle(self):

        with closing(self.odb.session()) as session:
            try:
                item = session.query(SQLConnectionPool).\
                    filter(SQLConnectionPool.id==self.request.input.id).\
                    one()

                ping = self.outgoing.sql.get(item.name, False).pool.ping

                self.response.payload.id = self.request.input.id
                response_time = ping(self.server.fs_sql_config)
                if response_time:
                    self.response.payload.response_time = str(response_time)

            except Exception as e:

                # Always roll back ..
                session.rollback()

                # .. and log or raise, depending on what we are instructed to do.
                log_msg = 'SQL connection `{}` could not be pinged, e:`{}`'

                if self.request.input.should_raise_on_error:
                    self.logger.warning(log_msg.format(item.name, format_exc()))
                    raise e
                else:
                    self.logger.warning(log_msg.format(item.name, e.args[0]))

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

class GetEngineList(AdminService):
    """ Returns a list of all engines defined in sql.conf.
    """
    output = AsIs('id'), 'name'

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
