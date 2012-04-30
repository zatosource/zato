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

# stdlib
import logging

# lxml
from lxml import etree
from lxml.objectify import Element

# Zato
from zato.admin.settings import TECH_ACCOUNT_NAME, TECH_ACCOUNT_PASSWORD
from zato.common import zato_namespace
from zato.common.soap import invoke_admin_service as _invoke_admin_service

logger = logging.getLogger(__name__)

def invoke_admin_service(cluster, soap_action, input_dict):
    """ A thin wrapper around zato.common.soap.invoke_admin_service that adds
    Django session-related information to the request headers.
    """
    zato_message = Element('{%s}zato_message' % zato_namespace)
    zato_message.request = Element('request')
    
    for k, v in input_dict.items():
        setattr(zato_message.request, k, v)

    headers = {'x-zato-session-type':'zato-admin/tech_acc', 
               'x-zato-user': TECH_ACCOUNT_NAME,
               'x-zato-password': TECH_ACCOUNT_PASSWORD
               }
    
    request = etree.tostring(zato_message)
    zato_message, soap_response = _invoke_admin_service(cluster, soap_action, request, headers)
    
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug('Request:[{}], response:[{}]'.format(request, soap_response))
        
    return zato_message, soap_response
