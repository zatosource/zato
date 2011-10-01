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
from traceback import format_exc
from uuid import uuid4

# SQLAlchemy
from sqlalchemy.orm.query import orm_exc

# lxml
from lxml import etree
from lxml.objectify import Element

# Zato
from zato.common import ZatoException, ZATO_FIELD_OPERATORS, ZATO_OK
from zato.common.odb.model import Cluster, SSLAuth, SSLAuthItem
from zato.common.util import TRACE1
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of SSL/TLS definitions available.
    """
    def handle(self, *args, **kwargs):
        definition_list = Element('definition_list')

        definitions = self.server.odb.query(SSLAuth).order_by('name').all()

        for definition in definitions:

            definition_elem = Element('definition')
            definition_elem.id = definition.id
            definition_elem.name = definition.name
            definition_elem.is_active = definition.is_active
            definition_elem.def_items = Element('def_items')
            
            for item in definition.items:
                item_elem = Element('item')
                item_elem.field = item.field
                item_elem.operator = item.operator
                item_elem.value = item.value
                
                definition_elem.def_items.append(item_elem)

            definition_list.append(definition_elem)

        return ZATO_OK, etree.tostring(definition_list)

class Create(AdminService):
    """ Creates a new SSL/TLS definition.
    """
    def handle(self, *args, **kwargs):
        
        try:
            
            payload = kwargs.get('payload')
            core_params = ['cluster_id', 'name', 'is_active']
            params = _get_params(payload, core_params, 'data.')
            
            def_items = _get_params(payload, ['def_items'], 'data.', use_text=False)
            
            cluster_id = params['cluster_id']
            name = params['name']
            is_active = params['is_active']
            
            items = []
            
            children = def_items.getchildren()
            if not children:
                raise Exception('[def_items] element must not be empty')
            
            for child in children:
                field = child.field.text.strip()
                operator = child.operator.text.strip()
                value = child.value.text.strip()
                
                if not field:
                    raise Exception('Field must not be empty in [{0}] [{1}] [{2}]'.format(
                        field, operator, value))
                
                if not operator:
                    raise Exception('Operator must not be empty in [{0}] [{1}] [{2}]'.format(
                        field, operator, value))
                
                if not value:
                    raise Exception('Value must not be empty in [{0}] [{1}] [{2}]'.format(
                        field, operator, value))
                
                if not operator in ZATO_FIELD_OPERATORS:
                    raise Exception('Operator must be one of [{0}] in [{1}] [{2}] [{3}]'.format(
                        sorted(ZATO_FIELD_OPERATORS.keys()), field, operator, value))
                
                item = SSLAuthItem(None, field, operator, value)
                items.append(item)
                
            
            cluster = self.server.odb.query(Cluster).filter_by(id=cluster_id).first()
            
            # Let's see if we already have a definition of that name before committing
            # any stuff into the database.
            existing_one = self.server.odb.query(SSLAuth).\
                filter(Cluster.id==cluster_id).\
                filter(SSLAuth.name==name).first()
            
            if existing_one:
                raise Exception('SSL/TLS definition [{0}] already exists on this cluster'.format(name))

            auth = SSLAuth(None, name, is_active, cluster)
            auth.items = items
            
            self.server.odb.add(auth)
            self.server.odb.commit()
            
            auth_elem = Element('ssl')
            auth_elem.id = auth.id
            
            return ZATO_OK, etree.tostring(auth_elem)
            
        except Exception, e:
            msg = "Could not create an SSL/TLS definition, e=[{e}]".format(e=format_exc(e))
            self.logger.error(msg)
            self.server.odb.rollback()
            
            raise 
        
class Edit(AdminService):
    """ Updates an SSL/TLS definition.
    """
    def handle(self, *args, **kwargs):

        try:
            
            payload = kwargs.get('payload')
            request_params = ['id', 'is_active', 'name', 'username', 'domain', 
                              'cluster_id']
            new_params = _get_params(payload, request_params, 'data.')
            
            def_id = new_params['id']
            name = new_params['name']
            cluster_id = new_params['cluster_id']

            existing_one = self.server.odb.query(SSLAuth).\
                filter(Cluster.id==cluster_id).\
                filter(SSLAuth.name==name).\
                filter(SSLAuth.id != def_id).\
                first()
            
            if existing_one:
                raise Exception('SSL/TLS definition [{0}] already exists on this cluster'.format(name))
            
            definition = self.server.odb.query(SSLAuth).filter_by(id=def_id).one()
            
            definition.name = name
            definition.is_active = new_params['is_active']
            definition.username = new_params['username']
            definition.domain = new_params['domain']

            self.server.odb.add(definition)
            self.server.odb.commit()
            
        except orm_exc.NoResultFound:
            raise ZatoException('SSL/TLS definition [%s] does not exist' % new_params['original_name'])
        except Exception, e:
            msg = "Could not update the SSL/TLS definition, e=[{e}]".format(e=format_exc(e))
            self.logger.error(msg)
            self.server.odb.rollback()
            
            raise 


        return ZATO_OK, ''
    
class Delete(AdminService):
    """ Deletes an SSL/TLS definition.
    """
    def handle(self, *args, **kwargs):
        
        try:
            payload = kwargs.get('payload')
            request_params = ['id']
            params = _get_params(payload, request_params, 'data.')
            
            id = params['id']
            
            auth = self.server.odb.query(SSLAuth).\
                filter(SSLAuth.id==id).\
                one()
            
            self.server.odb.delete(auth)
            self.server.odb.commit()
        except Exception, e:
            msg = "Could not delete the SSL/TLS definition, e=[{e}]".format(e=format_exc(e))
            self.logger.error(msg)
            self.server.odb.rollback()
            
            raise
        
        return ZATO_OK, ''