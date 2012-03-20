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
from zato.common.broker_message import MESSAGE_TYPE, SERVICE
from zato.common.odb.model import Cluster, Service
from zato.common.odb.query import service, service_list
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of services.
    """
    class SimpleIO:
        input_required = ('cluster_id',)
        
    def handle(self):
        with closing(self.odb.session()) as session:
            item_list = Element('item_list')
            db_items = service_list(session, self.request.input.cluster_id, False)

            for db_item in db_items:

                item = Element('item')
                item.id = db_item.id
                item.name = db_item.name
                item.is_active = db_item.is_active
                item.impl_name = db_item.impl_name
                item.is_internal = db_item.is_internal
                item.usage_count = 'TODO getlist'
    
                item_list.append(item)
    
            self.response.payload = etree.tostring(item_list)
        
class GetByID(AdminService):
    """ Returns a particular service.
    """
    class SimpleIO:
        input_required = ('cluster_id', 'id')

    def handle(self):
        with closing(self.odb.session()) as session:

            db_item = service(session, self.request.input.cluster_id, self.request.input.id)
            
            item = Element('item')
            item.id = db_item.id
            item.name = db_item.name
            item.is_active = db_item.is_active
            item.impl_name = db_item.impl_name
            item.is_internal = db_item.is_internal
            item.usage_count = 'TODO getbyid'
    
            self.response.payload = etree.tostring(item)

class Edit(AdminService):
    """ Updates a service.
    """
    class SimpleIO:
        input_required = ('id', 'is_active', 'name')
    
    def handle(self):
        input = self.request.input
        
        with closing(self.odb.session()) as session:
            service_elem = Element('service')
            try:
                service = session.query(Service).filter_by(id=input.id).one()
                service.is_active = input.is_active
                service.name = input.name
                
                session.add(service)
                session.commit()
                
                service_elem.id = service.id
                service_elem.name = service.name
                service_elem.impl_name = service.impl_name
                service_elem.is_internal = service.is_internal
                service_elem.usage_count = 'TODO edit'
                
                input.action = SERVICE.EDIT
                self.broker_client.send_json(input, msg_type=MESSAGE_TYPE.TO_PARALLEL_SUB)
                
                self.response.payload = etree.tostring(service_elem)
                
            except Exception, e:
                msg = 'Could not update the service, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                session.rollback()
                
                raise         
        
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
            