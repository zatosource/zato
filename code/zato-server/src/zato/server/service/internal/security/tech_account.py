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

# lxml
from lxml import etree
from lxml.objectify import Element

# Zato
from zato.common import ZatoException, ZATO_OK
from zato.common.odb.model import ChannelURLDefinition, ChannelURLSecurity, \
     Cluster, SecurityDefinition, TechnicalAccount
from zato.common.util import TRACE1
from zato.server.service.internal import _get_params, AdminService

class GetDefinitionList(AdminService):
    """ Returns a list of technical accounts defined in the ODB. The items are
    sorted by the 'name' attribute.
    """
    def handle(self, *args, **kwargs):
        
        definition_list = Element('definition_list')
        
        #definitions = self.server.odb.query(TechnicalAccount).order_by('name').\
        #            filter(Cluster.id==2).\
        #            all()
        
        #sec_def_q = self.session.query(SecurityDefinition.id, 
        #                    SecurityDefinition.security_def_type, 
        #                    ChannelURLDefinition.url_pattern,
        #                    ChannelURLDefinition.url_type).\
        #       filter(SecurityDefinition.id==ChannelURLSecurity.security_def_id).\
        #       filter(ChannelURLSecurity.channel_url_def_id==ChannelURLDefinition.id).\
        #       filter(ChannelURLDefinition.cluster_id==Cluster.id).\
        #       filter(Cluster.id==server.cluster_id).\
        #       all()
        
        payload = kwargs.get('payload')
        request_params = ['id']
        params = _get_params(payload, request_params, 'cluster.')
        
        q = self.server.odb.query(TechnicalAccount).\
                    order_by(TechnicalAccount.name).\
                    filter(Cluster.id==params['id'])

        for definition in q.all():

            definition_elem = Element('definition')
            
            definition_elem.id = definition.id
            definition_elem.name = definition.name
            definition_elem.is_active = definition.is_active

            definition_list.append(definition_elem)

        return ZATO_OK, etree.tostring(definition_list)