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

# anyjson
from json import dumps

# Zato
from zato.common import url_type, ZATO_NONE, ZATO_OK
from zato.common.broker_message import CHANNEL, MESSAGE_TYPE, OUTGOING
from zato.common.odb.model import Cluster, HTTPSOAP, SecurityBase, Service
from zato.common.odb.query import http_soap_list
from zato.common.util import security_def_type
from zato.server.service.internal import AdminService

class _HTTPSOAPService(object):
    """ A common class for various HTTP/SOAP-related services.
    """
    def notify_worker_threads(self, params, action):
        """ Notify worker threads of new or updated parameters.
        """
        params['action'] = action
        self.broker_client.send_json(params, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)

    def _handle_security_info(self, session, security_id, connection, transport):
        """ First checks whether the security type is correct for the given 
        connection type. If it is, returns a dictionary of security-related information.
        """
        info = {'sec_name':None, 'sec_type':None}
        
        if security_id:
            
            security = session.query(SecurityBase.name, SecurityBase.sec_type).\
            filter(SecurityBase.id==security_id).\
            one()
            
            # Outgoing plain HTTP connections may use HTTP Basic Auth only,
            # outgoing SOAP connections may use either WSS or HTTP Basic Auth.                
            if connection == 'outgoing':
                if transport == url_type.plain_http and security.sec_type != security_def_type.basic_auth:
                    raise Exception('Only HTTP Basic Auth is supported, not [{}]'.format(security.sec_type))
                elif transport == url_type.soap and security.sec_type \
                     not in(security_def_type.basic_auth, security_def_type.wss):
                    raise Exception('Security type must be HTTP Basic Auth or WS-Security, not [{}]'.format(security.sec_type))
            
            info['security_name'] = security.name
            info['sec_type'] = security.sec_type
            
        return info
        
class GetList(AdminService):
    """ Returns a list of HTTP/SOAP connections.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'connection', 'transport')
        output_required = ('id', 'name', 'is_active', 'is_internal', 'host', 
            'url_path', 'method', 'soap_action', 'soap_version', 'data_format', 
            'service_id', 'service_name', 'security_id', 'security_name', 'sec_type')
        output_repeated = True

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = http_soap_list(session, self.request.input.cluster_id,
                self.request.input.connection, self.request.input.transport, False)

class Create(AdminService, _HTTPSOAPService):
    """ Creates a new HTTP/SOAP connection.
    """
    class SimpleIO:
        input_required = ('connection', 'transport', 'cluster_id', 'name', 'is_active', 'is_internal', 
                    'url_path', 'service', 'security_id')
        input_optional = ('method', 'soap_action', 'soap_version', 'data_format', 'host')
        output_required = ('id',)
    
    def handle(self):
        input = self.request.input
        input.security_id = input.security_id if input.security_id != ZATO_NONE else None
        input.soap_action = input.soap_action if input.soap_action else ''
        
        if not input.url_path.startswith('/'):
            msg = 'URL path:[{}] must start with a slash /'.format(input.url_path)
            self.logger.error(msg)
            raise Exception(msg)
        
        with closing(self.odb.session()) as session:
            existing_one = session.query(HTTPSOAP.id).\
                filter(HTTPSOAP.cluster_id==input.cluster_id).\
                filter(HTTPSOAP.name==input.name).\
                filter(HTTPSOAP.connection==input.connection).\
                filter(HTTPSOAP.transport==input.transport).\
                first()

            if existing_one:
                raise Exception('An object of that name [{0}] already exists on this cluster'.format(input.name))
            
            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.name==input.service).first()
            
            if input.connection == 'channel' and not service:
                msg = 'Service [{0}] does not exist on this cluster'.format(input.service)
                self.logger.error(msg)
                raise Exception(msg)
            
            # Will raise exception if the security type doesn't match connection
            # type and transport
            sec_info = self._handle_security_info(session, input.security_id, 
                input.connection, input.transport)
            
            try:

                item = HTTPSOAP()
                item.connection = input.connection
                item.transport = input.transport
                item.cluster_id = input.cluster_id
                item.is_internal = input.is_internal
                item.name = input.name
                item.is_active = input.is_active
                item.host = input.host
                item.url_path = input.url_path
                item.security_id = input.security_id
                item.method = input.method
                item.soap_action = input.soap_action
                item.soap_version = input.soap_version
                item.data_format = input.data_format
                item.service = service

                session.add(item)
                session.commit()
                
                if input.connection == 'channel':
                    input.impl_name = service.impl_name
                    input.service_id = service.id
                    input.service_name = service.name

                input.id = item.id
                input.update(sec_info)
                
                if input.connection == 'channel':
                    action = CHANNEL.HTTP_SOAP_CREATE_EDIT
                else:
                    action = OUTGOING.HTTP_SOAP_CREATE_EDIT
                self.notify_worker_threads(input, action)

                self.response.payload.id = item.id

            except Exception, e:
                msg = 'Could not create the object, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

class Edit(AdminService, _HTTPSOAPService):
    """ Updates an HTTP/SOAP connection.
    """
    class SimpleIO:
        input_required = ('id', 'cluster_id', 'name', 'is_active', 'url_path', 
                'connection', 'service', 'transport', 'security_id')
        input_optional = ('method', 'soap_action', 'soap_version', 'data_format', 'host')
        output_required = ('id',)
    
    def handle(self):
        input = self.request.input
        input.security_id = input.security_id if input.security_id != ZATO_NONE else None
        input.soap_action = input.soap_action if input.soap_action else ''
        
        if not input.url_path.startswith('/'):
            msg = 'URL path:[{}] must start with a slash /'.format(input.url_path)
            self.logger.error(msg)
            raise Exception(msg)
        
        with closing(self.odb.session()) as session:

            existing_one = session.query(HTTPSOAP.id).\
                filter(HTTPSOAP.cluster_id==input.cluster_id).\
                filter(HTTPSOAP.id!=input.id).\
                filter(HTTPSOAP.name==input.name).\
                filter(HTTPSOAP.connection==input.connection).\
                filter(HTTPSOAP.transport==input.transport).\
                first()

            if existing_one:
                raise Exception('An object of that name [{0}] already exists on this cluster'.format(name))
            
            # Is the service's name correct?
            service = session.query(Service).\
                filter(Cluster.id==input.cluster_id).\
                filter(Service.name==input.service).first()
            
            if input.connection == 'channel' and not service:
                msg = 'Service [{0}] does not exist on this cluster'.format(input.service)
                self.logger.error(msg)
                raise Exception(msg)
            
            # Will raise exception if the security type doesn't match connection
            # type and transport
            sec_info = self._handle_security_info(session, input.security_id, input.connection, input.transport)

            try:
                item = session.query(HTTPSOAP).filter_by(id=input.id).one()
                old_name = item.name
                old_url_path = item.url_path
                old_soap_action = item.soap_action
                item.name = input.name
                item.is_active = input.is_active
                item.host = input.host
                item.url_path = input.url_path
                item.security_id = input.security_id
                item.connection = input.connection
                item.transport = input.transport
                item.cluster_id = input.cluster_id
                item.method = input.method
                item.soap_action = input.soap_action
                item.soap_version = input.soap_version
                item.data_format = input.data_format
                item.service = service

                session.add(item)
                session.commit()
                
                if input.connection == 'channel':
                    input.impl_name = service.impl_name
                    input.service_id = service.id
                    input.service_name = service.name
                
                input.is_internal = item.is_internal
                input.old_name = old_name
                input.old_url_path = old_url_path
                input.old_soap_action = old_soap_action
                input.update(sec_info)
                
                if input.connection == 'channel':
                    action = CHANNEL.HTTP_SOAP_CREATE_EDIT
                else:
                    action = OUTGOING.HTTP_SOAP_CREATE_EDIT
                self.notify_worker_threads(input, action)

                self.response.payload.id = item.id

            except Exception, e:
                msg = 'Could not update the object, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()

                raise

class Delete(AdminService, _HTTPSOAPService):
    """ Deletes an HTTP/SOAP connection.
    """
    class SimpleIO:
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                item = session.query(HTTPSOAP).\
                    filter(HTTPSOAP.id==self.request.input.id).\
                    one()
                
                old_name = item.name
                old_transport = item.transport
                old_url_path = item.url_path
                old_soap_action = item.soap_action

                session.delete(item)
                session.commit()
                
                if item.connection == 'channel':
                    action = CHANNEL.HTTP_SOAP_DELETE
                else:
                    action = OUTGOING.HTTP_SOAP_DELETE
                
                self.notify_worker_threads({'name':old_name, 'transport':old_transport,
                    'url_path':old_url_path, 'soap_action':old_soap_action}, action)

            except Exception, e:
                session.rollback()
                msg = 'Could not delete the object, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)

                raise
            
class Ping(AdminService):
    """ Pings an HTTP/SOAP connection.
    """
    class SimpleIO:
        input_required = ('id',)
        output_required = ('info',)

    def handle(self):
        with closing(self.odb.session()) as session:
            item = session.query(HTTPSOAP).filter_by(id=self.request.input.id).one()
            config_dict = getattr(self.outgoing, item.transport)
            self.response.payload.info = config_dict.get(item.name).ping(self.cid)

class GetURLSecurity(AdminService):
    """ Returns a JSON document describing the security configuration of all
    Zato channels.
    """
    def handle(self):
        response = {}
        response['url_sec'] = sorted(self.worker_store.request_handler.security.url_sec.items())
        response['plain_http_handler.http_soap'] = sorted(self.worker_store.request_handler.plain_http_handler.http_soap.items())
        response['soap_handler.http_soap'] = sorted(self.worker_store.request_handler.soap_handler.http_soap.items())
        self.response.payload = dumps(response, sort_keys=True, indent=4)
        self.response.content_type = 'application/json'
