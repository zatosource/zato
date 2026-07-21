# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The HTTP boundaries - REST and SOAP, both driven through RequestHandler.handle,
the entry point every HTTP channel goes through.
"""

# stdlib
from unittest.mock import MagicMock

# Bunch
from zato.common.ext.bunch import Bunch

# Zato
from zato.common.api import URL_TYPE
from zato.common.json_internal import dumps, loads
from zato.common.soap.common import Content_Type, SOAPVersion
from zato.common.soap.envelope import attach_body, build_envelope, parse_body, parse_envelope, to_bytes
from zato.common.soap.message import SOAPMessage
from zato.common.util.json_ import BasicParser
from zato.common.util.xml_.message import to_lexical
from zato.server.connection.http_soap.channel import RequestHandler
from zato.server.connection.http_soap.channel_soap import parse_soap_request, resolve_soap_payload

# Test corpus
from boundaries import Boundary
from cases import Family_Dict, Family_SOAP, Family_String

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    from cases import PayloadCase
    anydict = anydict
    PayloadCase = PayloadCase

# ################################################################################################################################
# ################################################################################################################################

_test_cid = 'test-cid-0001'

# The operation every SOAP request in this module carries - its response wrapper
# is the element the decoder reads the service's message back from.
_soap_operation = 'getOrderStatus'

# ################################################################################################################################
# ################################################################################################################################

def _invoke_http_channel(service_class:'any_', channel_item:'Bunch', wsgi_environ:'anydict', raw_request:'any_') -> 'any_':
    """ Runs one service through RequestHandler.handle, the way HTTP channels do it.
    """
    server = MagicMock()
    server.json_parser = BasicParser()

    service = service_class()
    server.service_store.new_instance.return_value = (service, True)

    handler = RequestHandler(server)

    out = handler.handle(_test_cid, {}, channel_item, wsgi_environ, raw_request,
        MagicMock(), None, '/test/path', {}, {})

    return out

# ################################################################################################################################
# ################################################################################################################################

class RESTBoundary(Boundary):
    """ The REST path - RequestHandler.handle with a JSON channel, the wire being
    the response's payload string.
    """
    name = 'rest'
    families = (Family_Dict, Family_String)

    def deliver(self, case:'PayloadCase') -> 'str':

        # The request travels as the wire string a REST client would send.
        if isinstance(case.request, dict):
            raw_request = dumps(case.request)
        else:
            raw_request = case.request

        channel_item = Bunch({
            'id': 1,
            'name': 'test.rest.channel',
            'service_impl_name': case.service_class._Service__service_impl_name,
            'data_format': 'json',
            'transport': 'plain_http',
            'merge_url_params_req': True,
            'params_pri': 'channel-params-over-msg',
        })

        wsgi_environ = {
            'zato.http.response.headers': {},
        }

        response = _invoke_http_channel(case.service_class, channel_item, wsgi_environ, raw_request)

        out = response.payload
        return out

# ################################################################################################################################

    def decode(self, wire:'str', case:'PayloadCase') -> 'any_':

        # The dict family travels as JSON, with no response at all being an empty string ..
        if case.family == Family_Dict:
            if wire:
                out = loads(wire)
            else:
                out = ''

        # .. and the string family is the payload itself.
        else:
            out = wire

        return out

# ################################################################################################################################
# ################################################################################################################################

class SOAPBoundary(Boundary):
    """ The SOAP path - RequestHandler.handle with a SOAP channel whose request
    was parsed into a protocol context first, the way the dispatcher does it.
    """
    name = 'soap'
    families = (Family_String, Family_SOAP)

    def deliver(self, case:'PayloadCase') -> 'any_':

        # Build the wire bytes of the incoming request envelope ..
        request_message = SOAPMessage()
        request_message.orderID = 'ORD-0001'

        envelope = build_envelope(SOAPVersion.V11)
        _ = attach_body(envelope, request_message, _soap_operation)
        request_body = to_bytes(envelope)

        channel_item = Bunch({
            'id': 1,
            'name': 'test.soap.channel',
            'service_impl_name': case.service_class._Service__service_impl_name,
            'data_format': 'xml',
            'transport': URL_TYPE.SOAP,
            'soap_version': SOAPVersion.V11,
            'use_mtom': False,
            'merge_url_params_req': True,
            'params_pri': 'channel-params-over-msg',
        })

        # .. parse it into the protocol context the dispatcher would build ..
        soap_context = parse_soap_request(_test_cid, request_body, Content_Type[SOAPVersion.V11], channel_item)
        resolve_soap_payload(_test_cid, soap_context, {})

        wsgi_environ = {
            'zato.http.response.headers': {},
            'zato.request.soap': soap_context,
            'zato.request.payload': soap_context.payload,
        }

        # .. and run the service the way any HTTP channel runs it.
        response = _invoke_http_channel(case.service_class, channel_item, wsgi_environ, request_body)

        out = response.payload
        return out

# ################################################################################################################################

    def decode(self, wire:'any_', case:'PayloadCase') -> 'any_':

        # A SOAP message travels enveloped and reads back from the operation's response wrapper ..
        if case.family == Family_SOAP:
            envelope = parse_envelope(wire)
            body_message = parse_body(envelope)

            operation_response = getattr(body_message, _soap_operation + 'Response')
            out = operation_response.to_dict()

        # .. and the string family passes through the channel unchanged.
        else:
            out = wire

        return out

# ################################################################################################################################

    def normalize_expected(self, expected:'any_') -> 'any_':

        # XML wire scalars read back as strings, so the canonical expected
        # values are mapped to their lexical forms before the comparison.
        out = _scalars_to_strings(expected)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _scalars_to_strings(value:'any_') -> 'any_':
    """ Returns a value with every scalar in it replaced by its XML lexical form.
    """
    if isinstance(value, dict):
        out = {}
        for name, item in value.items():
            out[name] = _scalars_to_strings(item)

    elif isinstance(value, list):
        out = []
        for item in value:
            out.append(_scalars_to_strings(item))

    elif isinstance(value, str):
        out = value

    else:
        out = to_lexical(value)

    return out

# ################################################################################################################################
# ################################################################################################################################
