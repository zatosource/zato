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
import unittest

# pmocky
from pmocky import MockTestCase

# Zato
from zato..server import Server, CircuitsServer, CircuitsSOAPGateway

# Zato tests
from zato..test.common import host, http_port, soap_uri_path


class ServerTestCase(MockTestCase):

    def test_server(self):

        server = Server()

        # Those default to None
        self.assertEquals(server.soap_gateway, None)
        self.assertEquals(server.soap_uri_path, None)
        self.assertEquals(server.http_port, None)

        # Server is an abstract class
        self.assertRaises(NotImplementedError, server.run)


    def test_circuits_server(self):

        soap_gateway = CircuitsSOAPGateway()

        server = CircuitsServer()
        server.soap_gateway = soap_gateway
        server.host = host
        server.soap_uri_path = soap_uri_path
        server.http_port = http_port
        server.after_properties_set()

        self.assertTrue(soap_gateway in server.components)
        self.assertFalse(server.running)

        # server.run is implemented by circuits.web.Server
        self.assertTrue(callable(server.run))

        server.stop()

if  __name__ == "__main__":
    unittest.main()
