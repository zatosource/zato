# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

_received = []

# ################################################################################################################################
# ################################################################################################################################

class DjangoTestEcho(Service):
    """ Receives a request from the Django plugin, stores the payload and headers, and echoes the payload back.
    """

    name = 'test.django.echo'

    def handle(self) -> 'None':

        headers = self.request.http.headers

        entry = {
            'payload': self.request.raw_request,
            'x-zato-user': headers.get('x-zato-user', ''),
            'x-zato-correlation-id': headers.get('x-zato-correlation-id', ''),
            'x-zato-forwarded-for': headers.get('x-zato-forwarded-for', ''),
        }

        _received.append(entry)

        self.response.payload = json.dumps(entry)

# ################################################################################################################################
# ################################################################################################################################

class DjangoTestGetReceived(Service):
    """ Returns the list of received entries.
    """

    name = 'test.django.get-received'

    def handle(self) -> 'None':

        out = {
            'count': len(_received),
            'entries': _received,
        }

        self.response.payload = json.dumps(out)

# ################################################################################################################################
# ################################################################################################################################

class DjangoTestClearReceived(Service):
    """ Clears the received entries list.
    """

    name = 'test.django.clear-received'

    def handle(self) -> 'None':
        _received.clear()

# ################################################################################################################################
# ################################################################################################################################
