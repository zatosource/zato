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
from zato.common.broker_message import MESSAGE_TYPE, OUTGOING
from zato.common.odb.model import Cluster, OutgoingS3
from zato.common.odb.query import out_s3_list
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of outgoing S3 connections.
    """
    def handle(self, *args, **kwargs):

        params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')

        with closing(self.server.odb.session()) as session:
            item_list = Element('item_list')
            db_items = out_s3_list(session, params['cluster_id'])

            for db_item in db_items:

                item = Element('item')
                item.id = db_item.id
                item.name = db_item.name
                item.is_active = db_item.is_active
                item.prefix_ = db_item.prefix
                item.aws_access_key = db_item.aws_access_key
                item.separator = db_item.separator
                item.key_sync_timeout = db_item.key_sync_timeout

                item_list.append(item)

            return ZATO_OK, etree.tostring(item_list)

class Create(AdminService):
    """ Creates a new outgoing S3 connection.
    """
    def handle(self, *args, **kwargs):

        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')

            core_params = ['cluster_id', 'name', 'is_active', 'prefix', 'aws_access_key', 'separator', 'key_sync_timeout']
            core_params = _get_params(payload, core_params, 'data.')

            name = core_params['name']
            cluster_id = core_params['cluster_id']

            existing_one = session.query(OutgoingS3.id).\
                filter(OutgoingS3.cluster_id==cluster_id).\
                filter(OutgoingS3.name==name).\
                first()

            if existing_one:
                raise Exception('An outgoing S3 connection [{0}] already exists on this cluster'.format(name))

            created_elem = Element('out_s3')

            try:

                core_params['is_active'] = is_boolean(core_params['is_active'])

                item = OutgoingS3()
                item.name = core_params['name']
                item.is_active = core_params['is_active']
                item.prefix = core_params['prefix']
                item.aws_access_key = core_params['aws_access_key']
                item.aws_secret_key = uuid4().hex
                item.separator = core_params['separator']
                item.key_sync_timeout = core_params['key_sync_timeout']
                item.cluster_id = core_params['cluster_id']

                session.add(item)
                session.commit()

                created_elem.id = item.id

                return ZATO_OK, etree.tostring(created_elem)

            except Exception, e:
                msg = 'Could not create an outgoing S3 connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

class Edit(AdminService):
    """ Updates an outgoing S3 connection.
    """
    def handle(self, *args, **kwargs):

        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')

            core_params = ['cluster_id', 'name', 'is_active', 'prefix', 'aws_access_key', 'separator', 'key_sync_timeout']
            core_params = _get_params(payload, core_params, 'data.')

            id = core_params['id']
            name = core_params['name']
            cluster_id = core_params['cluster_id']

            existing_one = session.query(OutgoingS3.id).\
                filter(OutgoingS3.cluster_id==cluster_id).\
                filter(OutgoingS3.name==name).\
                filter(OutgoingS3.id!=core_params['id']).\
                first()

            if existing_one:
                raise Exception('An outgoing S3 connection [{0}] already exists on this cluster'.format(name))

            xml_item = Element('out_s3')

            try:

                core_params['id'] = int(core_params['id'])
                core_params['is_active'] = is_boolean(core_params['is_active'])

                item = session.query(OutgoingS3).filter_by(id=id).one()
                old_name = item.name
                item.name = name
                item.is_active = core_params['is_active']
                item.prefix = core_params['prefix']
                item.aws_access_key = core_params['aws_access_key']
                item.separator = core_params['separator']
                item.key_sync_timeout = core_params['key_sync_timeout']

                session.add(item)
                session.commit()

                xml_item.id = item.id

                return ZATO_OK, etree.tostring(xml_item)

            except Exception, e:
                msg = 'Could not update the outgoing S3 connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

class Delete(AdminService):
    """ Deletes an outgoing S3 connection.
    """
    def handle(self, *args, **kwargs):
        with closing(self.server.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')

                id = params['id']

                item = session.query(OutgoingS3).\
                    filter(OutgoingS3.id==id).\
                    one()

                session.delete(item)
                session.commit()

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the outgoing S3 connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise

            return ZATO_OK, ''
