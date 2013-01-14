# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at gefira.pl>

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
from unittest import TestCase
from uuid import uuid4

# lxml
from lxml import etree

# Zato
from zato.common import ParsingException, soap_body_xpath, zato_path

class ZatoPathTestCase(TestCase):
    def test_zato_path(self):
        xml = etree.fromstring("""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:zato="http://gefira.pl/zato">
   <soapenv:Header/>
   <soapenv:Body>
      <zato:zato_service_get_list_request>
         <cluster_id>123</cluster_id>
      </zato:zato_service_get_list_request>
   </soapenv:Body>
</soapenv:Envelope>""")
        
        # zato:service.get-list
        # techacct-226327
        # 04fd1704f75546d58765dd13516a1512
        
        request = soap_body_xpath(xml)[0].getchildren()[0]
        zato_path('zato_service_get_list_request', True).get_from(request)
        
        path = uuid4().hex
        try:
            zato_path(path, True).get_from(request)
        except ParsingException:
            pass
        else:
            raise AssertionError('Expected an ParsingException with path:[{}]'.format(path))
