# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The channel boundaries - each one delivers a corpus case to its service through
one channel's real entry point and decodes the wire form back into the canonical
dict or string that the case expects.
"""

# stdlib
from json import dumps as json_dumps
from unittest.mock import MagicMock

# Zato
from zato.common.api import CHANNEL, DATA_FORMAT, HL7
from zato.common.hl7.mllp.codec import frame_encode, FrameDecoder
from zato.common.json_internal import loads
from zato.common.marshal_.api import Model
from zato.common.typing_ import cast_
from zato.common.util.api import hex_sequence_to_bytes
from zato.common.util.json_ import BasicParser

# Test corpus
from cases import Family_Dict, Family_String

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict
    from zato.server.service import Service
    from cases import PayloadCase
    anylist = anylist
    stranydict = stranydict
    PayloadCase = PayloadCase
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

_test_cid = 'test-cid-0001'

# The MLLP framing sequences, resolved the same way the HL7 MLLP channel resolves them from its config.
_mllp_start_sequence = hex_sequence_to_bytes(HL7.Default.start_seq)
_mllp_end_sequence   = hex_sequence_to_bytes(HL7.Default.end_seq)
_mllp_max_message_size = HL7.Default.max_msg_size

# ################################################################################################################################
# ################################################################################################################################

def dispatch_service(
    service_class, # type: any_
    payload,       # type: any_
    channel,       # type: str
    data_format,   # type: str
    transport=None,     # type: any_
    wsgi_environ=None,  # type: stranydict | None
    job_type='',        # type: str
    **response_kwargs   # type: any_
    ) -> 'tuple[any_, Service]':
    """ Runs one service through update_handle the way non-HTTP channels do it,
    returning what the channel's caller receives along with the service instance.
    """
    service = service_class()

    server = MagicMock()
    server.json_parser = BasicParser()

    response = service.update_handle(
        service.set_response_data, service, payload, channel, data_format, transport, server,
        None, MagicMock(), _test_cid, {},
        job_type=job_type, wsgi_environ=wsgi_environ or {}, **response_kwargs)

    return response, service

# ################################################################################################################################

def to_canonical(value:'any_') -> 'any_':
    """ Maps a live response object to its canonical comparable form - models
    and lists of models become dicts, everything else stays as it is.
    """
    if isinstance(value, Model):
        out = value.to_dict()

    elif isinstance(value, list):
        out = []
        for item in value:
            if isinstance(item, Model):
                item = item.to_dict()
            out.append(item)

    else:
        out = value

    return out

# ################################################################################################################################
# ################################################################################################################################

class Boundary:
    """ One channel's entry and exit points - deliver sends a case's request
    to its service, decode turns the wire form back into a dict or a string.
    """
    name = ''
    families = ()

    def runs(self, case:'PayloadCase') -> 'bool':
        out = case.family in self.families
        return out

# ################################################################################################################################

    def deliver(self, case:'PayloadCase') -> 'any_':
        raise NotImplementedError()

# ################################################################################################################################

    def decode(self, wire:'any_', case:'PayloadCase') -> 'any_':
        out = wire
        return out

# ################################################################################################################################

    def normalize_expected(self, expected:'any_') -> 'any_':
        out = expected
        return out

# ################################################################################################################################
# ################################################################################################################################

class SchedulerBoundary(Boundary):
    """ The scheduler path - update_handle with a job type, the way
    on_message_invoke_service dispatches scheduler-initiated invocations.
    """
    name = 'scheduler'
    families = (Family_Dict, Family_String)

    def deliver(self, case:'PayloadCase') -> 'any_':

        wsgi_environ = {
            'zato.request_ctx.async_msg': {'cid': _test_cid, 'service': case.service_class._Service__service_name},
        }

        out, _ = dispatch_service(case.service_class, case.request, CHANNEL.SCHEDULER, DATA_FORMAT.DICT,
            wsgi_environ=wsgi_environ, job_type='interval_based')

        return out

# ################################################################################################################################

    def decode(self, wire:'any_', case:'PayloadCase') -> 'any_':

        # The scheduler receives live Python objects - only models need mapping to their dict form.
        out = to_canonical(wire)
        return out

# ################################################################################################################################
# ################################################################################################################################

class QueueBridgeBoundary(Boundary):
    """ The queue bridge path - a message from an external queue (Kafka, IBM MQ)
    invokes the service with its headers in the WSGI environment, and the reply
    is encoded the way the bridge's recv loop encodes it for the reply-to queue.
    """
    name = 'queue-bridge'
    families = (Family_Dict, Family_String)

    def runs(self, case:'PayloadCase') -> 'bool':

        # The recv loop's stdlib JSON encoder handles dicts and lists of dicts
        # but not live model instances, so model-shaped cases stay out.
        if case.is_model_shaped:
            return False

        out = case.family in self.families
        return out

# ################################################################################################################################

    def deliver(self, case:'PayloadCase') -> 'bytes':

        # A queue message always arrives as bytes.
        if isinstance(case.request, dict):
            data = json_dumps(case.request).encode('utf8')
        else:
            data = case.request.encode('utf8')

        headers = {'MsgId': 'QMSG-0001', 'ReplyToQ': 'ORDERS.REPLY'}
        wsgi_environ = {'zato.request.headers': headers}

        response, _ = dispatch_service(case.service_class, data, CHANNEL.INVOKE, DATA_FORMAT.DICT,
            wsgi_environ=wsgi_environ)

        # The reply travels the way the recv loop encodes it for the reply-to queue.
        if isinstance(response, bytes):
            out = response
        elif isinstance(response, str):
            out = response.encode('utf8')
        else:
            out = json_dumps(response).encode('utf8')

        return out

# ################################################################################################################################

    def decode(self, wire:'bytes', case:'PayloadCase') -> 'any_':

        text = wire.decode('utf8')

        # The dict family travels as JSON ..
        if case.family == Family_Dict:
            if text:
                out = loads(text)
            else:
                out = ''

        # .. and the string family is the payload itself.
        else:
            out = text

        return out

# ################################################################################################################################
# ################################################################################################################################

class MLLPBoundary(Boundary):
    """ The MLLP path - the service's string response is framed the way the HL7 MLLP
    server frames it and the frame is decoded back on the caller's side.
    """
    name = 'mllp'
    families = (Family_String,)

    def deliver(self, case:'PayloadCase') -> 'bytes':

        # The HL7 MLLP channel invokes its service with the unframed message as the payload.
        response, _ = dispatch_service(case.service_class, case.request, CHANNEL.INVOKE, DATA_FORMAT.DICT)

        payload = response.encode('utf8')
        out = frame_encode(payload, _mllp_start_sequence, _mllp_end_sequence)

        return out

# ################################################################################################################################

    def decode(self, wire:'bytes', case:'PayloadCase') -> 'str':

        decoder = FrameDecoder(_mllp_start_sequence, _mllp_end_sequence, _mllp_max_message_size)
        decoder.feed(wire)

        # The wire always carries one complete frame here, so a message is always available.
        message = cast_('bytes', decoder.next_message())
        out = message.decode('utf8')

        return out

# ################################################################################################################################
# ################################################################################################################################

class InvokeBoundary(Boundary):
    """ The service-to-service path - update_handle exactly the way invoke_by_impl_name
    runs it, with no wire in between, so the caller receives live Python objects.
    """
    name = 'invoke'
    families = (Family_Dict, Family_String)

    def deliver(self, case:'PayloadCase') -> 'any_':

        payload = case.request

        # With no payload but with extra keyword arguments, the arguments
        # become the payload - the same block invoke_by_impl_name runs.
        if not payload:
            if case.invoke_kwargs:
                payload = {}
                for name, value in case.invoke_kwargs.items():
                    payload[name] = value

        out, _ = dispatch_service(case.service_class, payload, CHANNEL.INVOKE, case.data_format,
            transport='', serialize=False, as_bunch=case.as_bunch, skip_response_elem=True)

        return out

# ################################################################################################################################

    def decode(self, wire:'any_', case:'PayloadCase') -> 'any_':

        # The caller receives live Python objects - only models need mapping to their dict form.
        out = to_canonical(wire)
        return out

# ################################################################################################################################
# ################################################################################################################################
