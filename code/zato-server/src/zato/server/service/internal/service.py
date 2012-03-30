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

wsdl_template = """
<?xml version="1.0" encoding="utf-8"?>
<definitions xmlns="http://schemas.xmlsoap.org/wsdl/" 
  xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" 
  xmlns:http="http://schemas.xmlsoap.org/wsdl/http/" 
  xmlns:xs="http://www.w3.org/2001/XMLSchema" 
  xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" 
  xmlns:mime="http://schemas.xmlsoap.org/wsdl/mime/" 
  xmlns:zato="http://gefira.pl/zato" 
  xmlns:zato_types="http://gefira.pl/zato/types" 
  targetNamespace="http://gefira.pl/zato">
  
   <types>
     <xs:schema targetNamespace="http://gefira.pl/zato/types" xmlns="http://gefira.pl/zato/types" 
         elementFormDefault="unqualified" attributeFormDefault="unqualified">
       
         <xs:complexType name="{service_name}Input">
            <xs:sequence>
               <xs:element name="a" type="xs:string"/>
               <xs:element name="b" type="xs:string"/>
            </xs:sequence>
         </xs:complexType>
         
         <xs:complexType name="{service_name}Output">
            <xs:sequence>
               <xs:element name="c" type="xs:string"/>
            </xs:sequence>
         </xs:complexType>
         
         <xs:element name="request" type="{service_name}Input"/>
         <xs:element name="response" type="{service_name}Output"/>
         
      </xs:schema>
   </types>
   
   <message name="{service_name}MessageRequest">
      <part name="parameters" element="zato_types:request"/>
   </message>
   
   <message name="{service_name}ResponseMessage">
      <part name="parameters" element="zato_types:response"/>
   </message>
   
   <portType name="{service_name}Interface">
      <operation name="{service_name}">
         <input message="zato:{service_name}MessageRequest"/>
         <output message="zato:{service_name}ResponseMessage"/>
      </operation>
   </portType>
   
   <binding name="{service_name}SoapHttpBinding" type="zato:{service_name}Interface">
      <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
      <operation name="{service_name}">
         <soap:operation soapAction="{service_name}"/>
         <input>
            <soap:body use="literal"/>
         </input>
         <output>
            <soap:body use="literal"/>
         </output>
      </operation>
   </binding>
   
   <service name="{service_name}Service">
      <port name="{service_name}Endpoint" binding="zato:{service_name}SoapHttpBinding">
         <soap:address location="http://host.invalid/"/>
      </port>
   </service>
</definitions>
"""

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
                    self.set_attachment(service_name, self.generate_wsdl(service_name, service_class.SimpleIO), 'application/wsdl+xml')
                    
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
        
    def generate_wsdl(self, service_name, sio):
        """ Returns a WSDL automatically generated out of a service's name and its
        accompanying SimpleIO configuration.
        """
        #print(self.response.simple_io_config._bunch.items())

        request_elem = getattr(sio, 'request_elem', 'request')
        response_elem = getattr(sio, 'response_elem', 'response')
        required_list = getattr(sio, 'input_required', [])
        optional_list = getattr(sio, 'input_optional', [])
        required_list = getattr(sio, 'output_required', [])
        required_list = getattr(sio, 'output_optional', [])
        
        return wsdl_template.format(service_name=service_name)
        
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
