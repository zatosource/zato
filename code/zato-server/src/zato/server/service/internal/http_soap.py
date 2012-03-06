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

# Zato
from zato.common import ZATO_OK
from zato.common.odb.model import Cluster, HTTPSOAP, Service
from zato.common.odb.query import http_soap_list
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of HTTP/SOAP connections.
    """
    def handle(self, *args, **kwargs):

        params = _get_params(kwargs.get('payload'), ['cluster_id', 'connection', 'transport'], 'data.')

        with closing(self.server.odb.session()) as session:
            item_list = Element('item_list')
            db_items = http_soap_list(session, params['cluster_id'],
                                      params['connection'], params['transport'], 
                                      False)
            
            for db_item in db_items:

                item = Element('item')
                item.id = db_item.id
                item.name = db_item.name
                item.is_active = db_item.is_active
                item.is_internal = db_item.is_internal
                item.url_path = db_item.url_path
                item.method = db_item.method
                item.soap_action = db_item.soap_action
                item.soap_version = db_item.soap_version
                item.service_id = db_item.service_id
                item.service_name = db_item.service_name
                item.security_id = db_item.security_id
                item.security_name = db_item.security_name
                item.security_def_type = db_item.security_def_type

                item_list.append(item)

            return ZATO_OK, etree.tostring(item_list)

class Create(AdminService):
    """ Creates a new HTTP/SOAP connection.
    """
    def handle(self, *args, **kwargs):

        with closing(self.server.odb.session()) as session:
            payload = kwargs.get('payload')

            core_params = ['connection', 'transport', 'cluster_id', 'name', 
                           'is_active', 'is_internal', 'url_path', 'service', 
                           'sec_def_id']
            core_params = _get_params(payload, core_params, 'data.')

            optional_params = ['method', 'soap_action', 'soap_version']
            optional_params = _get_params(payload, optional_params, 'data.', default_value=None)

            name = core_params['name']
            cluster_id = core_params['cluster_id']
            service_name = core_params['service']
            sec_def_id = core_params['sec_def_id']

            existing_one = session.query(HTTPSOAP.id).\
                filter(HTTPSOAP.cluster_id==cluster_id).\
                filter(HTTPSOAP.name==name).\
                first()

            if existing_one:
                raise Exception('An object of that name [{0}] already exists on this cluster'.format(name))
            
            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==cluster_id).\
                filter(Service.name==service_name).first()
            
            if not service:
                msg = 'Service [{0}] does not exist on this cluster'.format(service_name)
                self.logger.error(msg)
                raise Exception(msg)
            
            # Now onto assigning the security-related attributes.

            #if sec_def_id != ZATO_NONE:
            #    sec_def = session.query(SecurityDefinition).\
            #    filter(SecurityDefinition.id==sec_def_id).\
            #    one()
            #    
            #    #sec_def = SecurityDefinition(None, security_def_type)
            #    #session.add(sec_def)

            created_elem = Element('http_soap')
            
            try:

                core_params['is_active'] = is_boolean(core_params['is_active'])

                item = HTTPSOAP()
                item.connection = core_params['connection']
                item.transport = core_params['transport']
                item.cluster_id = core_params['cluster_id']
                item.is_internal = core_params['is_internal']
                item.name = core_params['name']
                item.is_active = core_params['is_active']
                item.url_path = core_params['url_path']
                item.method = optional_params.get('method')
                item.soap_action = optional_params.get('soap_action')
                item.soap_version = optional_params.get('soap_version')
                item.service = service
                
                #if sec_def_id != ZATO_NONE:
                #    
                #    channel_sec = HTTPSOAPSecurity(item, sec_def)
                #    session.add(channel_sec)

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

            core_params = ['id', 'cluster_id', 'name', 'is_active', 'url_path', 'connection', 'transport']
            core_params = _get_params(payload, core_params, 'data.')

            optional_params = ['method', 'soap_action', 'soap_version']
            optional_params = _get_params(payload, optional_params, 'data.', default_value=None)

            id = core_params['id']
            name = core_params['name']
            cluster_id = core_params['cluster_id']

            existing_one = session.query(HTTPSOAP.id).\
                filter(HTTPSOAP.cluster_id==cluster_id).\
                filter(HTTPSOAP.id!=id).\
                filter(HTTPSOAP.name==name).\
                first()

            if existing_one:
                raise Exception('An object of that name [{0}] already exists on this cluster'.format(name))

            xml_item = Element('http_soap')

            try:

                core_params['id'] = int(core_params['id'])
                core_params['is_active'] = is_boolean(core_params['is_active'])

                item = session.query(HTTPSOAP).filter_by(id=id).one()
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

                xml_item.id = item.id

                return ZATO_OK, etree.tostring(xml_item)

            except Exception, e:
                msg = 'Could not update the object, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

class Delete(AdminService):
    """ Deletes an HTTP/SOAP connection.
    """
    def handle(self, *args, **kwargs):
        with closing(self.server.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')

                id = params['id']

                item = session.query(HTTPSOAP).\
                    filter(HTTPSOAP.id==id).\
                    one()

                session.delete(item)
                session.commit()

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the object, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise

            return ZATO_OK, ''
