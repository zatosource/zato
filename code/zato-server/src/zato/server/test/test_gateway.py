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
import unittest
from string import Template
from cStringIO import StringIO

# lxml
from lxml import etree
from lxml import objectify

# Zato
from zato..soap import ClientSOAPException
from zato..server import SOAPGateway, CircuitsSOAPGateway

# Zato tests
from zato..test.common import soap_request

soapenv_ns = "http://schemas.xmlsoap.org/soap/envelope/"
soap_response = Template("""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body>$body</soap:Body></soap:Envelope>""")

class GatewayTestCase(unittest.TestCase):

    def test_gateway(self):
        gateway = SOAPGateway()

        # SOAPGateway is an abstract class subclassing 'object' and defines no
        # new attributes/methods.
        diff = set(dir(gateway)) ^ set(dir(object))
        self.assertEquals(diff, set(["__module__", "logger", "__dict__", "__weakref__"]))

    def _assert_headers(self, headers):
        self.assertEquals(1, len(headers))
        self.assertEquals(headers["Content-Type"], "text/xml")

    def test_circuit_soap_gateway(self):

        soap_action = "foobar"

        class TestRequest(object):
            def __init__(self):
                self.headers = {}
                self.body = StringIO()
                self.body.write(soap_request)

            def _reset(self):
                self.headers.clear()
                self.body.truncate()
                self.body.write(soap_request)

        class TestResponse(object):
            def __init__(self):
                self.headers = {}
                self.status = None

            def _reset(self):
                self.headers.clear()
                self.status = None

        class OKReturningDispatcher(object):
            def handle(self, request, headers):
                return soap_response.safe_substitute(body="abc")

        class ErrorReturningDispatcher(object):
            def handle(self, request, headers):
                raise ClientSOAPException(soap_response.safe_substitute(body=httplib.BAD_REQUEST))

        class ExceptionRaisingDispatcher(object):
            def handle(self, request, headers):
                raise KeyError()

        test_request = TestRequest()
        test_response = TestResponse()

        gateway = CircuitsSOAPGateway()
        gateway.request = test_request
        gateway.response = test_response
        gateway.cookie = None

        # Succcess.
        gateway.dispatcher = OKReturningDispatcher()
        data = gateway.index()
        self.assertEquals(test_response.status, httplib.OK)
        self.assertEquals(data, soap_response.safe_substitute(body="abc"))
        self._assert_headers(test_response.headers)
        test_request._reset()
        test_response._reset()

        # Client error
        gateway.dispatcher = ErrorReturningDispatcher()
        gateway.request = test_request
        gateway.response = test_response
        gateway.cookie = None
        data = gateway.index()
        self.assertEquals(test_response.status, httplib.BAD_REQUEST)
        self.assertEquals(data, soap_response.safe_substitute(body=httplib.BAD_REQUEST))
        test_request._reset()
        test_response._reset()

        # Dispatcher has raised an exception, gateway has caught it
        # and a server error must've been returned ..
        gateway.dispatcher = ExceptionRaisingDispatcher()
        gateway.request = test_request
        gateway.response = test_response
        gateway.cookie = None
        data = gateway.index()
        self.assertEquals(test_response.status, httplib.INTERNAL_SERVER_ERROR)

        # .. which we must now parse and make sure it's a proper SOAP response
        # containing the fault code and a traceback (or at least the relevant parts of it).

        envelope = objectify.fromstring(data)

        # Validate with XML Schema first
        soap11_schema_doc = etree.parse(open("./support/soap11.xsd"))
        soap11_schema = etree.XMLSchema(soap11_schema_doc)
        soap11_schema.assert_(envelope)

        # An unhandled exception is always our fault
        self.assertEquals("SOAP-ENV:Server", envelope.Body.Fault.find("faultcode"))

        # Make sure the fault string mentions what happended during processing
        # of message.
        self.assertTrue("raise KeyError()" in envelope.Body.Fault.find("faultstring").text)

        test_request._reset()
        test_response._reset()

if  __name__ == "__main__":
    unittest.main()
