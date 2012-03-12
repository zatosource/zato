# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

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

# stdlib
from contextlib import closing
from traceback import format_exc
from uuid import uuid4

# lxml
from lxml import etree
from lxml.objectify import Element

# validate
from validate import is_boolean

# Zato
from zato.common import ZATO_OK
from zato.common.broker_message import MESSAGE_TYPE, OUTGOING
from zato.common.odb.model import SQLConnectionPool
from zato.common.odb.query import out_sql_list
from zato.server.service.internal import _get_params, AdminService, ChangePasswordBase

class _SQLService(object):
    """ A common class for various SQL-related services.
    """
    def notify_worker_threads(self, params, action=OUTGOING.SQL_CREATE_EDIT):
        """ Notify worker threads of new or updated parameters.
        """
        params['action'] = action
        self.broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)

class GetList(AdminService):
    """ Returns a list of outgoing SQL connections.
    """
    def handle(self, *args, **kwargs):
        params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
        
        with closing(self.odb.session()) as session:
            item_list = Element('item_list')
            db_items = out_sql_list(session, params['cluster_id'], False)
            
            for db_item in db_items:

                item = Element('item')
                item.id = db_item.id
                item.name = db_item.name
                item.is_active = db_item.is_active
                
                item.engine = db_item.engine
                item.host = db_item.host
                item.port = db_item.port
                item.db_name = db_item.db_name
                item.username = db_item.username
                item.pool_size = db_item.pool_size
                item.extra = db_item.extra.decode('utf-8') if db_item.extra else ''
                
                item_list.append(item)

            return ZATO_OK, etree.tostring(item_list)

class Create(AdminService, _SQLService):
    """ Creates a new outgoing SQL connection.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.odb.session()) as session:
            payload = kwargs.get('payload')

            core_params = ['name', 'is_active', 'cluster_id', 'engine', 'host', 'port',
                           'db_name', 'username', 'pool_size']
            core_params = _get_params(payload, core_params, 'data.')
            
            optional_params = ['extra']
            optional_params = _get_params(payload, optional_params, 'data.', default_value=None)

            name = core_params['name']
            cluster_id = core_params['cluster_id']
            extra = optional_params['extra']
            extra = extra.encode('utf-8') if extra else ''
            password = uuid4().hex

            existing_one = session.query(SQLConnectionPool.id).\
                filter(SQLConnectionPool.cluster_id==cluster_id).\
                filter(SQLConnectionPool.name==name).\
                first()

            if existing_one:
                raise Exception('An outgoing SQL connection [{0}] already exists on this cluster'.format(name))

            created_elem = Element('out_sql')

            try:

                core_params['is_active'] = is_boolean(core_params['is_active'])

                item = SQLConnectionPool()
                item.name = core_params['name']
                item.is_active = core_params['is_active']
                item.cluster_id = core_params['cluster_id']
                item.engine = core_params['engine']
                item.host = core_params['host']
                item.port = core_params['port']
                item.db_name = core_params['db_name']
                item.username = core_params['username']
                item.password = password
                item.pool_size = core_params['pool_size']
                item.extra = extra

                session.add(item)
                session.commit()
                
                created_elem.id = item.id
                
                core_params.update(optional_params)
                core_params['password'] = password
                self.notify_worker_threads(core_params)
                
                return ZATO_OK, etree.tostring(created_elem)

            except Exception, e:
                msg = 'Could not create an outgoing SQL connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            
class Edit(AdminService, _SQLService):
    """ Updates an outgoing SQL connection.
    """
    def handle(self, *args, **kwargs):

        with closing(self.odb.session()) as session:
            payload = kwargs.get('payload')

            core_params = ['id', 'cluster_id', 'name', 'is_active', 'engine', 
                           'host', 'port', 'db_name', 'username', 'pool_size']
            core_params = _get_params(payload, core_params, 'data.')
            
            optional_params = ['extra']
            optional_params = _get_params(payload, optional_params, 'data.', default_value=None)

            id = core_params['id']
            name = core_params['name']
            cluster_id = core_params['cluster_id']
            extra = optional_params['extra']
            extra = extra.encode('utf-8') if extra else ''

            existing_one = session.query(SQLConnectionPool.id).\
                filter(SQLConnectionPool.cluster_id==cluster_id).\
                filter(SQLConnectionPool.name==name).\
                filter(SQLConnectionPool.id!=core_params['id']).\
                first()

            if existing_one:
                raise Exception('An outgoing SQL connection [{0}] already exists on this cluster'.format(name))

            xml_item = Element('out_sql')

            try:

                core_params['id'] = int(core_params['id'])
                core_params['is_active'] = is_boolean(core_params['is_active'])

                item = session.query(SQLConnectionPool).filter_by(id=id).one()
                old_name = item.name
                item.name = core_params['name']
                item.is_active = core_params['is_active']
                item.cluster_id = core_params['cluster_id']
                item.engine = core_params['engine']
                item.host = core_params['host']
                item.port = core_params['port']
                item.db_name = core_params['db_name']
                item.username = core_params['username']
                item.pool_size = core_params['pool_size']
                item.extra = extra

                session.add(item)
                session.commit()

                xml_item.id = item.id

                core_params.update(optional_params)
                core_params['password'] = item.password
                core_params['old_name'] = old_name
                self.notify_worker_threads(core_params)

                return ZATO_OK, etree.tostring(xml_item)

            except Exception, e:
                msg = 'Could not update the outgoing SQL connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise
            
class Delete(AdminService, _SQLService):
    """ Deletes an outgoing SQL connection.
    """
    def handle(self, *args, **kwargs):
        with closing(self.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')

                id = params['id']

                item = session.query(SQLConnectionPool).\
                    filter(SQLConnectionPool.id==id).\
                    one()
                old_name = item.name

                session.delete(item)
                session.commit()
                
                self.notify_worker_threads({'name':old_name}, OUTGOING.SQL_DELETE)

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the outgoing SQL connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise

            return ZATO_OK, ''
        
class ChangePassword(ChangePasswordBase):
    """ Changes the password of an outgoing SQL connection. The underlying implementation
    will actually stop and recreate the connection using the new password.
    """
    def handle(self, *args, **kwargs):

        with closing(self.odb.session()) as session:
            
            def _auth(instance, password):
                instance.password = password
                
            self._handle(SQLConnectionPool, _auth, OUTGOING.SQL_CHANGE_PASSWORD, **kwargs)
            
            return ZATO_OK, ''


class Ping(AdminService):
    """ Pings an SQL database
    """
    def handle(self, *args, **kwargs):
        with closing(self.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')

                id = params['id']

                item = session.query(SQLConnectionPool).\
                    filter(SQLConnectionPool.id==id).\
                    one()

                xml_item = etree.Element('response_time')
                xml_item.text = str(self.outgoing.sql.get(item.name).ping())
                
                return ZATO_OK, etree.tostring(xml_item)

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the outgoing SQL connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise