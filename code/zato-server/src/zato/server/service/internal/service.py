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
from httplib import BAD_REQUEST, NOT_FOUND
from mimetypes import guess_type
from traceback import format_exc
from urlparse import parse_qs

# Zato
from zato.common import ZATO_OK, ZatoException
from zato.common.broker_message import MESSAGE_TYPE, SERVICE
from zato.common.odb.model import Cluster, Service
from zato.common.odb.query import service, service_list
from zato.server.service import Boolean, Service as ServiceClass
from zato.server.service.internal import AdminService

def generate_wsdl(service_name, sio):
    """ Returns a WSDL automatically generated out of a service's name and its
    accompanying SimpleIO configuration.
    """
    return 'aaa'

class GetList(AdminService):
    """ Returns a list of services.
    """
    class SimpleIO:
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'impl_name', 'is_internal')
        output_repeated = True
        
    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = service_list(session, self.request.input.cluster_id, False)
        
class GetByID(AdminService):
    """ Returns a particular service.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'id')
        output_required = ('id', 'name', 'is_active', 'impl_name', 'is_internal', )
        output_optional = ('usage_count',)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = service(session, self.request.input.cluster_id, self.request.input.id)

class Edit(AdminService):
    """ Updates a service.
    """
    class SimpleIO:
        input_required = ('id', 'is_active', 'name')
        output_required = ('id', 'name', 'impl_name', 'is_internal',)
        output_optional = (Boolean('usage_count'),)
    
    def handle(self):
        input = self.request.input
        with closing(self.odb.session()) as session:
            try:
                service = session.query(Service).filter_by(id=input.id).one()
                service.is_active = input.is_active
                service.name = input.name
                
                session.add(service)
                session.commit()
                
                input.action = SERVICE.EDIT
                self.broker_client.send_json(input, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
                
                self.response.payload = service
                
            except Exception, e:
                msg = 'Could not update the service, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise         
            
class GetWSDL(ServiceClass):
    """ Returns a WSDL for the given service. Either uses a user-uploaded one,
    or, optionally generates one on fly if the service uses SimpleIO.
    """
    input_optional = ('service',)
    def handle(self):
        if self.request.request_data.query:
            query = parse_qs(self.request.request_data.query)
            service_name = query.get('service')
            
            if not service_name:
                self.response.status_code = BAD_REQUEST
                self.response.payload = 'No [service] parameter in the query string'
                return
            
            service_name = service_name[0]
            
            with closing(self.odb.session()) as session:
                service = session.query(Service).filter_by(name=service_name).first()
                if not service:
                    self.response.status_code = NOT_FOUND
                    self.response.payload = 'Service [{}] not found'.format(service_name)
                    return
                
            # User-uploaded stuff has precedence over auto-generated WSDLs .. 
            if service.wsdl:
                content_type = guess_type(service.wsdl_name)[0] or 'application/octet-stream'
                self.set_attachment(service_name, service.wsdl, content_type)
                
            # .. now let's find out whether the service uses SimpleIO ..
            else:
                service_class = self.server.service_store.service_data(service.impl_name)['service_class']
                if hasattr(service_class, 'SimpleIO'):
                    self.set_attachment(service_name, generate_wsdl(service_name, service_class.SimpleIO), 'application/wsdl+xml')
                    
                # .. give up, there's neither a WSDL from the user nor SimpleIO in use
                else:
                    self.response.status_code = NOT_FOUND
                    self.response.payload = 'No WSDL found'
                    
    def set_attachment(self, service_name, payload, content_type):
        """ Sets the information that we're returning an attachment to the user.
        """
        self.response.content_type = content_type
        self.response.payload = payload
        self.response.headers['Content-Disposition'] = 'attachment; filename={}.wsdl'.format(service_name)
        
class Delete(AdminService):
    """ Deletes a service
    """
    class SimpleIO:
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                service = session.query(Service).\
                    filter(Service.id==self.request.input.id).\
                    one()
                
                session.delete(service)
                session.commit()

                msg = {'action': SERVICE.DELETE, 'id': self.request.input.id}
                self.broker_client.send_json(msg, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the service, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
