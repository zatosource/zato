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
import httplib

host = "localhost"
http_port = 17080
soap_uri_path = "/soap"

soap_request = """<soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
   <soapenv:Header/>
   <soapenv:Body>
      <test>123</test>
   </soapenv:Body>
</soapenv:Envelope>"""

len_soap_request = len(soap_request)

def soap_invoke(soap_action, http_port=8080, soap_uri_path=soap_uri_path):

    conn = httplib.HTTPConnection("127.0.0.1", http_port)

    conn.putrequest("POST", soap_uri_path, skip_host=True)
    conn.putheader("Host", "127.0.0.1:%s" % http_port)
    conn.putheader("Content-Type", "text/xml;charset=UTF-8")
    conn.putheader("Content-Length", len_soap_request)
    conn.endheaders()
    conn.send(soap_request)

    response = conn.getresponse()
    status, data = response.status, response.read()

    conn.close()

    return status, data
