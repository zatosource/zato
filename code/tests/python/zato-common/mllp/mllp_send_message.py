# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import socket
import sys

# Zato
from conftest import start_sequence, end_sequence, sample_wellness_oru

# ################################################################################################################################
# ################################################################################################################################

_host                 = '127.0.0.1'
_recv_timeout_seconds = 3.0
_recv_buffer_size     = 4096

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Sends the wellness HL7v2 message to the HAProxy frontend via MLLP framing
    and prints the ACK response.
    """

    parser = argparse.ArgumentParser(description='Send an MLLP-framed HL7v2 wellness message')
    _ = parser.add_argument('--port', type=int, required=True)
    args = parser.parse_args()

    port = args.port
    message = sample_wellness_oru()
    framed = start_sequence + message + end_sequence

    # Connect and send ..
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.settimeout(_recv_timeout_seconds)
    connection.connect((_host, port))
    connection.sendall(framed)

    _ = sys.stdout.write(f'Sent {len(message)} bytes to {_host}:{port}\n')

    # .. read the ACK response ..
    response = b''

    while True:
        try:
            chunk = connection.recv(_recv_buffer_size)
            if not chunk:
                break
            response += chunk
            if end_sequence in response:
                break
        except socket.timeout:
            break

    connection.close()

    # .. extract and display the ACK payload ..
    ack_start = response.find(start_sequence)
    ack_end = response.find(end_sequence)

    if ack_start != -1:
        if ack_end != -1:
            ack_payload = response[ack_start + len(start_sequence):ack_end]
            _ = sys.stdout.write(f'ACK: {ack_payload.decode("utf-8")}\n')
    else:
        _ = sys.stdout.write(f'Raw response: {response!r}\n')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()
