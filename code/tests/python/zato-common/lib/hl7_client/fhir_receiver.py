# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import threading
import time
from http.client import OK
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import NamedTuple

# fhir.resources
from fhir.resources import get_fhir_model_class

# Zato
from hl7_client.ports import find_free_port
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# What every listener here binds to
_Host = '127.0.0.1'

# What the receiver keeps its resources in
resource_list = list['ReceivedResource']

# What validating one document produces - whether it is valid and the error text when it is not
validation_result = tuple[bool, str]

# ################################################################################################################################
# ################################################################################################################################

class ReceivedResource(NamedTuple):
    """ One FHIR resource as this receiver saw it, with the outcome of validating it
    against the FHIR specification.
    """
    path: 'str'
    document: 'stranydict'
    is_valid: 'bool'
    error: 'str'
    arrived_at: 'float'

# ################################################################################################################################
# ################################################################################################################################

def _validate(document:'stranydict') -> 'validation_result':
    """ Validates one document against the FHIR specification with fhir.resources, the
    standard Python model of that specification.
    """
    resource_type = document['resourceType']
    model_class = get_fhir_model_class(resource_type)

    try:
        _ = model_class.model_validate(document)
    except Exception as error:
        out = False, str(error)
    else:
        out = True, ''

    return out

# ################################################################################################################################
# ################################################################################################################################

class _FHIRHTTPHandler(BaseHTTPRequestHandler):
    """ Records each resource on the receiver it serves, validating it first, and answers
    the way a FHIR server answers - with the resource it was sent.
    """

    def do_POST(self) -> 'None':

        server = cast_('any_', self.server)
        receiver = server.receiver

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode('utf-8')

        document = json.loads(body)
        is_valid, error = _validate(document)

        resource = ReceivedResource(self.path, document, is_valid, error, time.monotonic())
        receiver.resources.append(resource)

        response_body = body.encode('utf-8')

        self.send_response(OK)
        self.send_header('Content-Type', 'application/fhir+json')
        self.send_header('Content-Length', str(len(response_body)))
        self.end_headers()
        _ = self.wfile.write(response_body)

    def log_message(self, message_format:'str', *args:'object') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class FHIRReceiver:
    """ An HTTP receiving side for FHIR deliveries. Every incoming document is validated with
    fhir.resources against the actual FHIR specification, so what a FHIR destination sends is
    checked for being a real resource rather than merely being echoed back.
    """

    def __init__(self) -> 'None':
        self.port = find_free_port()
        self.resources:'resource_list' = []

        self._server:'any_' = None
        self._thread:'threading.Thread | None' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the receiver on its port, which stays the same across a stop and a start.
        """
        server = cast_('any_', ThreadingHTTPServer((_Host, self.port), _FHIRHTTPHandler))

        # The handler reads its receiver off the server it runs on
        server.receiver = self

        self._server = server

        self._thread = threading.Thread(target=server.serve_forever, daemon=True)
        self._thread.start()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the receiver, leaving its port free for a later start.
        """
        self._server.shutdown()
        self._server.server_close()
        self._server = None

# ################################################################################################################################
# ################################################################################################################################
