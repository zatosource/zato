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

# lxml
from lxml import etree

# Zato
from zato.server.service import Service
from zato.server.soap import soap_invoke

import time

class HelloZatoService(Service):

    def handle(self, *args, **kwargs):
        response = etree.Element("response")
        response.text = "Hello Zato!"
        time.sleep(0.3)

        return etree.tostring(response)

class SampleSOAPInvokingService(Service):

    def handle(self, *args, **kwargs):
        resp = soap_invoke("http://localhost:17080/soap","haj")
        self.logger.debug("RESP [%s]" % resp)
        return resp
