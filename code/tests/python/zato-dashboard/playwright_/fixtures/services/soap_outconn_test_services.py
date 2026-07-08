# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode, b64encode
from json import dumps

# Zato
from zato.common.soap.common import SOAPFault
from zato.common.soap.message import SOAPMessage
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class InvokeSOAPOutconnForTests(Service):
    """ Invokes an outgoing SOAP connection on behalf of outgoing SOAP connection tests.
    """

    name = 'test.soap.outconn.invoke'

    def handle(self):

        request = self.request.payload
        mode = request['mode']

        # A readiness probe sent while the test waits for this service to deploy ..
        if mode == 'ping':
            out = {'is_ready': True}

        # .. otherwise, call the outgoing connection and report what came back.
        else:
            out = self._invoke_outconn(request)

        self.response.payload = dumps(out)
        self.response.content_type = 'application/json'

# ################################################################################################################################

    def _invoke_outconn(self, request):

        outconn_name = request['outconn_name']
        operation = request['operation']
        namespace = request.get('namespace')

        # Build the outgoing message - plain fields keep their values,
        # base64 fields become bytes, e.g. for MTOM scenarios.
        message = SOAPMessage()

        if namespace:
            message.namespace = namespace

        for name, value in (request.get('fields') or {}).items():
            setattr(message, name, value)

        for name, value in (request.get('bytes_fields') or {}).items():
            setattr(message, name, b64decode(value))

        conn = self.out.soap[outconn_name].conn

        try:
            response = conn.invoke(self.cid, operation, message)
        except SOAPFault as fault:
            out = {
                'fault_code': fault.code,
                'fault_reason': fault.reason,
            }
            return out

        # Read back the fields the caller asked for ..
        response_fields = {}

        for name in (request.get('response_fields') or []):
            value = getattr(response, name, None)
            if isinstance(value, bytes):
                response_fields[name] = b64encode(value).decode()
            elif value is not None:
                response_fields[name] = str(value)
            else:
                response_fields[name] = None

        # .. the addressing headers of the reply, when there are any ..
        addressing = {}
        response_addressing = getattr(response, 'addressing', None)

        if response_addressing:
            addressing = {
                'action': response_addressing.action,
                'relates_to': response_addressing.relates_to,
                'message_id': response_addressing.message_id,
            }

        # .. and any MTOM attachments, base64-encoded for the JSON ride back.
        attachments = []
        response_attachments = getattr(response, 'attachments', None) or []

        for part in response_attachments:
            attachments.append({
                'content_id': part.content_id,
                'data': b64encode(part.data).decode(),
            })

        out = {
            'fields': response_fields,
            'addressing': addressing,
            'attachments': attachments,
        }

        return out

# ################################################################################################################################
# ################################################################################################################################
