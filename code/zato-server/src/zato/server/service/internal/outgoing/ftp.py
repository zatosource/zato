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

# lxml
from lxml import etree
from lxml.objectify import Element

# validate
from validate import is_boolean

# Bunch
from bunch import Bunch

# Zato
from zato.common import ZATO_OK
from zato.common.odb.model import OutgoingFTP
from zato.common.odb.query import out_ftp_list
from zato.server.service.internal import _get_params, AdminService, ChangePasswordBase

class _FTPService(AdminService):
    def update_facade(self, params, optional_params, old_name=None):
        params.update(optional_params)
        self.ftp.update(Bunch(params), old_name)

class GetList(AdminService):
    """ Returns a list of outgoing FTP connections.
    """
    def handle(self, *args, **kwargs):
        
        params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')

        with closing(self.odb.session()) as session:
            item_list = Element('item_list')
            db_items = out_ftp_list(session, params['cluster_id'], False)

            for db_item in db_items:

                item = Element('item')
                item.id = db_item.id
                item.name = db_item.name
                item.is_active = db_item.is_active
                item.host = db_item.host
                item.port = db_item.port
                item.user = db_item.user
                item.acct = db_item.acct
                item.timeout = db_item.timeout
                item.dircache = db_item.dircache

                item_list.append(item)

            return ZATO_OK, etree.tostring(item_list)

class Create(_FTPService):
    """ Creates a new outgoing FTP connection.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.odb.session()) as session:
            payload = kwargs.get('payload')

            core_params = ['cluster_id', 'name', 'is_active', 'host', 'port', 'dircache']
            core_params = _get_params(payload, core_params, 'data.')
            
            optional_params = ['user', 'acct', 'timeout']
            optional_params = _get_params(payload, optional_params, 'data.', default_value=None)

            name = core_params['name']
            cluster_id = core_params['cluster_id']

            existing_one = session.query(OutgoingFTP.id).\
                filter(OutgoingFTP.cluster_id==cluster_id).\
                filter(OutgoingFTP.name==name).\
                first()

            if existing_one:
                raise Exception('An outgoing FTP connection [{0}] already exists on this cluster'.format(name))

            created_elem = Element('out_ftp')

            try:

                core_params['is_active'] = is_boolean(core_params['is_active'])
                core_params['dircache'] = is_boolean(core_params['dircache'])

                item = OutgoingFTP()
                item.name = core_params['name']
                item.is_active = core_params['is_active']
                item.cluster_id = core_params['cluster_id']
                item.dircache = core_params['dircache']
                item.host = core_params['host']
                item.port = core_params['port']
                item.user = optional_params['user']
                item.acct = optional_params['acct']
                item.timeout = optional_params['timeout']

                session.add(item)
                session.commit()

                created_elem.id = item.id
                self.update_facade(core_params, optional_params)

                return ZATO_OK, etree.tostring(created_elem)

            except Exception, e:
                msg = 'Could not create an outgoing FTP connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

class Edit(_FTPService):
    """ Updates an outgoing FTP connection.
    """
    def handle(self, *args, **kwargs):

        with closing(self.odb.session()) as session:
            payload = kwargs.get('payload')

            core_params = ['id', 'cluster_id', 'name', 'is_active', 'host', 'port', 'dircache']
            core_params = _get_params(payload, core_params, 'data.')
            
            optional_params = ['user', 'acct', 'timeout']
            optional_params = _get_params(payload, optional_params, 'data.', default_value=None)

            id = core_params['id']
            name = core_params['name']
            cluster_id = core_params['cluster_id']

            existing_one = session.query(OutgoingFTP.id).\
                filter(OutgoingFTP.cluster_id==cluster_id).\
                filter(OutgoingFTP.name==name).\
                filter(OutgoingFTP.id!=core_params['id']).\
                first()

            if existing_one:
                raise Exception('An outgoing FTP connection [{0}] already exists on this cluster'.format(name))

            xml_item = Element('out_ftp')

            try:

                core_params['id'] = int(core_params['id'])
                core_params['is_active'] = is_boolean(core_params['is_active'])
                core_params['dircache'] = is_boolean(core_params['dircache'])

                item = session.query(OutgoingFTP).filter_by(id=id).one()
                old_name = item.name
                item.name = core_params['name']
                item.is_active = core_params['is_active']
                item.cluster_id = core_params['cluster_id']
                item.dircache = core_params['dircache']
                item.host = core_params['host']
                item.port = core_params['port']
                item.user = optional_params['user']
                item.acct = optional_params['acct']
                item.timeout = optional_params['timeout']

                session.add(item)
                session.commit()

                xml_item.id = item.id
                self.update_facade(core_params, optional_params, old_name)

                return ZATO_OK, etree.tostring(xml_item)

            except Exception, e:
                msg = 'Could not update the outgoing FTP connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

class Delete(AdminService):
    """ Deletes an outgoing FTP connection.
    """
    def handle(self, *args, **kwargs):
        with closing(self.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')

                id = params['id']

                item = session.query(OutgoingFTP).\
                    filter(OutgoingFTP.id==id).\
                    one()
                old_name = item.name

                session.delete(item)
                session.commit()
                
                self.ftp.update(None, old_name)

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the outgoing FTP connection, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise

            return ZATO_OK, ''

class ChangePassword(ChangePasswordBase):
    """ Changes the password of an outgoing FTP connection.
    """
    def handle(self, *args, **kwargs):

        with closing(self.odb.session()) as session:
            
            def _auth(instance, password):
                instance.password = password
                self.ftp.update_password(instance.name, password)
                
            self._handle(OutgoingFTP, _auth, None, **kwargs)
            
            return ZATO_OK, ''
