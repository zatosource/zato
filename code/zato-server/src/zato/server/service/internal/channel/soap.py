# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

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

# lxml
from lxml import etree
from lxml.objectify import Element

# Zato
from zato.common import ZatoException, ZATO_OK
from zato.common.odb.model import ChannelURLDefinition, Cluster
from zato.common.odb.query import soap_channel_list
from zato.server.service.internal import _get_params, AdminService

class GetList(AdminService):
    """ Returns a list of SOAP channels defined.
    """
    def handle(self, *args, **kwargs):
        
        with closing(self.server.odb.session()) as session:
            
            params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
            definition_list = Element('definition_list')
            definitions = soap_channel_list(session, params['cluster_id'])
            
            for definition in definitions:
    
                definition_elem = Element('definition')
                definition_elem.id = definition.id
                definition_elem.url_pattern = definition.url_pattern
                definition_elem.is_internal = definition.is_internal
                
                
                definition_list.append(definition_elem)
    
            return ZATO_OK, etree.tostring(definition_list)