# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A suite standing in for a system that sends to the engine sends with the engine's own client, so that what
# comes back is the same validated acknowledgment an outgoing connection sees.

# Zato
from zato.common.hl7.mllp.settings import Default_End_Sequence, Default_Start_Sequence
from zato.common.hl7.mllp.client import HL7MLLPClient
from zato.common.hl7.mllp.tls import build_client_ssl_context

# Live HL7
from live_hl7.messages import control_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.hl7.mllp.ack import AckResult
    from live_hl7.enmasse import TLSClient

# ################################################################################################################################
# ################################################################################################################################

# How long one send waits for the acknowledgment - long enough for a message the engine carries on to
# a container and answers with what the container said
Receive_Timeout = 30.0

# The name a TLS sender expects on the engine's certificate
Server_Name = 'localhost'

# ################################################################################################################################
# ################################################################################################################################

def send(host:'str', port:'int', message:'str', *, tls:'TLSClient | None'=None) -> 'AckResult':
    """ One message to one listener, the acknowledgment validated against the control id it carried.
    """
    if tls:
        ssl_context = build_client_ssl_context(tls.ca_path, tls.cert_path, tls.key_path)
    else:
        ssl_context = None

    client = HL7MLLPClient(
        host,
        port,
        Default_Start_Sequence,
        Default_End_Sequence,
        receive_timeout=Receive_Timeout,
        ssl_context=ssl_context,
        server_hostname=Server_Name,
    )

    out = client.send(message.encode('utf8'), control_id(message))
    return out

# ################################################################################################################################
# ################################################################################################################################
