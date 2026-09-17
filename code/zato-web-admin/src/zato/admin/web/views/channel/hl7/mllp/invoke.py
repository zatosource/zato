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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# .. MLLP framing bytes ..
_MLLP_Start_Byte = b'\x0b'
_MLLP_End_Bytes  = b'\x1c\x0d'

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

        # .. wrap in MLLP framing ..
        mllp_message = _MLLP_Start_Byte + payload_bytes + _MLLP_End_Bytes

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

                # .. stop once we see the MLLP end bytes ..
                if _MLLP_End_Bytes in response_data:
                    break

        finally:
            sock.close()

        elapsed = time() - start

        # .. strip MLLP framing from the response ..
        response_text = response_data
        if response_text.startswith(_MLLP_Start_Byte):
            response_text = response_text[1:]
        end_idx = response_text.find(_MLLP_End_Bytes)
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
