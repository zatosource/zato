# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class BearerOutgoingCall(Service):
    """ Invokes a named outgoing REST connection and reports what came back, including any error raised
    on the way, so that a test can assert on the token flow without reading server logs.
    """
    name = 'test.bearer.outgoing.call'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        conn = self.out.rest[conn_name].conn

        try:
            response = conn.get(self.cid)
        except Exception as e:
            self.response.payload = {'status_code': 0, 'text': '', 'error': str(e)}
        else:
            self.response.payload = {'status_code': response.status_code, 'text': response.text, 'error': ''}

# ################################################################################################################################
# ################################################################################################################################

class BearerOutgoingFHIRRead(Service):
    """ Reads a resource through a named outgoing FHIR connection - the connection logs in to the FHIR server's
    token endpoint with its bearer token definition before the read goes out.
    """
    name = 'test.bearer.outgoing.fhir.read'

    def handle(self) -> 'None':

        conn_name = self.request.raw_request['conn_name']
        resource_type = self.request.raw_request['resource_type']
        resource_id = self.request.raw_request['resource_id']

        client = self.fhir[conn_name]

        try:
            resource = client.get(resource_type, resource_id)
        except Exception as e:
            self.response.payload = {'resource': {}, 'error': str(e)}
        else:
            self.response.payload = {'resource': dict(resource), 'error': ''}

# ################################################################################################################################
# ################################################################################################################################
