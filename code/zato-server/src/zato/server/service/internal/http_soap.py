# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

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

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc
from uuid import uuid4

# SQLAlchemy
from sqlalchemy.orm.query import orm_exc

# lxml
from lxml import etree
from lxml.objectify import Element

# validate
from validate import is_boolean

# Zato
from zato.common import ZatoException, ZATO_OK
from zato.common.odb.model import Cluster, HTTPSOAP
from zato.common.odb.query import http_soap_list
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of HTTP/SOAP connections.
    """
    def handle(self, *args, **kwargs):

        params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')

        with closing(self.server.odb.session()) as session:
            item_list = Element('item_list')
            db_items = http_soap_list(session, params['cluster_id'])

            for db_item in db_items:

                item = Element('item')
                item.id = db_item.id
                item.name = db_item.name
                item.is_active = db_item.is_active
                item.url_path = db_item.url_path
                item.method = db_item.method
                item.soap_action = db_item.soap_action
                item.soap_version = db_item.soap_version

                item_list.append(item)

            return ZATO_OK, etree.tostring(item_list)

class Create(AdminService):
    """ Creates a new HTTP/SOAP connection.
    """
    def handle(self, *args, **kwargs):

        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')

            core_params = ['cluster_id', 'name', 'is_active', 'url_path', 'connection', 'transport']
            core_params = _get_params(payload, core_params, 'data.')

            optional_params = ['method', 'soap_action', 'soap_version']
            optional_params = _get_params(payload, optional_params, 'data.', default_value=None)

            name = core_params['name']
            cluster_id = core_params['cluster_id']

            existing_one = session.query(HTTPSOAP.id).\
                filter(HTTPSOAP.cluster_id==cluster_id).\
                filter(HTTPSOAP.name==name).\
                first()

            if existing_one:
                raise Exception('An object of that name [{0}] already exists on this cluster'.format(name))

            created_elem = Element('http_soap')

            try:

                core_params['is_active'] = is_boolean(core_params['is_active'])

                item = HTTPSOAP()
                item.name = core_params['name']
                item.is_active = core_params['is_active']
                item.url_path = core_params['url_path']
                item.connection = core_params['connection']
                item.transport = core_params['transport']
                item.cluster_id = core_params['cluster_id']
                item.method = optional_params.get('method')
                item.soap_action = optional_params.get('soap_action')
                item.soap_version = optional_params.get('soap_version')

                session.add(item)
                session.commit()

                created_elem.id = item.id

                return ZATO_OK, etree.tostring(created_elem)

            except Exception, e:
                msg = 'Could not create the object, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

class Edit(AdminService):
    """ Updates a ZeroMQ channel.
    """
    def handle(self, *args, **kwargs):

        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')

            core_params = ['id', 'cluster_id', 'name', 'is_active', 'address', 'socket_type']
            core_params = _get_params(payload, core_params, 'data.')

            optional_params = ['sub_key']
            optional_params = _get_params(payload, optional_params, 'data.', default_value=None)

            id = core_params['id']
            name = core_params['name']
            cluster_id = core_params['cluster_id']

            existing_one = session.query(ChannelZMQ.id).\
                filter(ChannelZMQ.cluster_id==cluster_id).\
                filter(ChannelZMQ.name==name).\
                filter(ChannelZMQ.id!=id).\
                first()

            if existing_one:
                raise Exception('A ZeroMQ channel [{0}] already exists on this cluster'.format(name))

            xml_item = Element('channel_zmq')

            try:

                core_params['id'] = int(core_params['id'])
                core_params['is_active'] = is_boolean(core_params['is_active'])

                item = session.query(ChannelZMQ).filter_by(id=id).one()
                old_name = item.name
                item.name = name
                item.is_active = core_params['is_active']
                item.address = core_params['address']
                item.socket_type = core_params['socket_type']
                item.sub_key = optional_params.get('sub_key')

                session.add(item)
                session.commit()

                xml_item.id = item.id

                return ZATO_OK, etree.tostring(xml_item)

            except Exception, e:
                msg = 'Could not update the ZeroMQ channel, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

class Delete(AdminService):
    """ Deletes a ZeroMQ channel.
    """
    def handle(self, *args, **kwargs):
        with closing(self.server.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')

                id = params['id']

                item = session.query(ChannelZMQ).\
                    filter(ChannelZMQ.id==id).\
                    one()

                session.delete(item)
                session.commit()

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the ZeroMQ channel, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise

            return ZATO_OK, ''
