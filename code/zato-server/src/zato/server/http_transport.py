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
import logging

# Spring Python
from springpython.config import ApplicationContextAware

class HTTPTransport(Component, ApplicationContextAware):

    def __init__(self, services=None, service_store=None, crypto_manager=None):
        self.logger = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))

        self.services = services
        self.service_store = service_store
        self.crypto_manager = crypto_manager

    def http_message(self, request):
        # TODO: Add background thread somewhere which will in a couple of seconds
        # interval go through all registered URLs and try to find any conflicts.
        # Conflicts should then be reported /somewhere/ and be available for
        # ZatoAdmin users.

        # TODO: Here the transport type (SOAP/REST) should be recognized.

        body = request.body.read()
        headers = request.headers
        return self.push(Event(body, headers), "soap_message")
