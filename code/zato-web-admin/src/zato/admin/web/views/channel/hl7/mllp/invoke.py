# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http import HTTPStatus
from socket import AF_INET, SOCK_STREAM, socket as socket_
from time import time
from traceback import format_exc
from urllib.parse import urlparse

# Django
from django.http import JsonResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.channel.hl7.mllp.common import logger
from zato.common.util.api import hex_sequence_to_bytes

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# .. TCP recv buffer size ..
_Recv_Buffer_Size = 65536

# .. socket timeout in seconds ..
_Socket_Timeout = 90

# ################################################################################################################################
# ################################################################################################################################

def _resolve_mllp_listener_address(req:'any_') -> 'tuple[str, int]':
    """ Resolves where the shared MLLP listener accepts connections - the port lives
    in the server process and the listener runs on the same host as the server itself.
    """
    response = req.zato.client.invoke('zato.server.invoker', {'func_name': 'get_hl7_mllp_port'})
    port = int(response.data)

    host = urlparse(req.zato.client.address).hostname

    return host, port

# ################################################################################################################################

def _resolve_channel_framing(req:'any_', id:'str') -> 'tuple[bytes, bytes]':
    """ Resolves the start and end sequences of the channel the message is sent on behalf of -
    the listener reads a frame under the sequences of the channel its MSH line selects and
    answers with them, so the message is framed and the reply read the way that channel is.
    """
    response = req.zato.client.invoke('zato.generic.connection.get-by-id', {'id': id})

    if not response.ok:
        raise Exception(f'HL7 MLLP channel with id `{id}` could not be read')

    start_bytes = hex_sequence_to_bytes(response.data['start_seq'])
    end_bytes = hex_sequence_to_bytes(response.data['end_seq'])

    return start_bytes, end_bytes

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def invoke_channel(req:'any_', id:'str') -> 'JsonResponse':
    """ Sends an MLLP-framed HL7 message to the server's MLLP listener and returns the response.
    """
    try:
        payload = req.POST['data-request']
        payload_bytes = payload.encode('utf-8')

        # .. find the listener - a port of zero means no MLLP channel is running ..
        listener_host, listener_port = _resolve_mllp_listener_address(req)

        if not listener_port:
            return JsonResponse({
                'data': 'No HL7 MLLP listener is running - create an active MLLP channel first',
                'response_time_human': '',
                'content_type': 'text/plain',
            }, status=HTTPStatus.BAD_REQUEST)

        # .. wrap in the framing of the channel the overlay was opened from ..
        start_bytes, end_bytes = _resolve_channel_framing(req, id)
        mllp_message = start_bytes + payload_bytes + end_bytes

        start = time()

        # .. open a TCP connection to the listener ..
        sock = socket_(AF_INET, SOCK_STREAM)
        sock.settimeout(_Socket_Timeout)

        try:
            sock.connect((listener_host, listener_port))
            sock.sendall(mllp_message)

            # .. read the MLLP-framed response ..
            response_data = b''
            while True:
                chunk = sock.recv(_Recv_Buffer_Size)
                if not chunk:
                    break
                response_data += chunk

                # .. stop once we see the channel's end bytes ..
                if end_bytes in response_data:
                    break

        finally:
            sock.close()

        elapsed = time() - start

        # .. strip MLLP framing from the response ..
        response_text = response_data
        if response_text.startswith(start_bytes):
            response_text = response_text[len(start_bytes):]
        end_idx = response_text.find(end_bytes)
        if end_idx != -1:
            response_text = response_text[:end_idx]

        response_body = response_text.decode('utf-8', errors='replace')

        return JsonResponse({
            'data': response_body,
            'response_time_human': '{:.1f}ms'.format(elapsed * 1000),
            'content_type': 'text/plain',
        })

    except Exception as e:
        logger.error('invoke_channel error: %s', format_exc())
        return JsonResponse({
            'data': str(e),
            'response_time_human': '',
            'content_type': 'text/plain',
        }, status=HTTPStatus.INTERNAL_SERVER_ERROR)

# ################################################################################################################################
# ################################################################################################################################
