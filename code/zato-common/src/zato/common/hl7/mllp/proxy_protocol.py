# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from logging import getLogger
from struct import unpack

# Zato
from zato.common.hl7.exception import HL7Exception

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The fixed bytes every version 2 header opens with, chosen so that no plausible
# application payload can be mistaken for one.
Signature = b'\x0d\x0a\x0d\x0a\x00\x0d\x0a\x51\x55\x49\x54\x0a'

# The version and command byte, the family and protocol byte and the two length bytes -
# what follows the signature before the rest of the header can be sized.
_Sizing_Length = 4

# The signature, the version and command byte, the family and protocol byte and the
# two length bytes - what has to be read before the rest of the header can be sized.
Prefix_Length = len(Signature) + _Sizing_Length

# The high nibble of the version and command byte, which is the only version accepted here.
_Version_2 = 0x20

# The low nibble of that same byte - LOCAL is a health check with no address, PROXY carries one.
_Command_Local = 0x00
_Command_Proxy = 0x01

# The high nibble of the family and protocol byte.
_Family_Unspecified = 0x00
_Family_Inet        = 0x10
_Family_Inet6       = 0x20
_Family_Unix        = 0x30

# How many bytes of address block each family contributes - two addresses and two ports.
_Address_Length = {
    _Family_Inet:  12,
    _Family_Inet6: 36,
    _Family_Unix:  216,
}

# The type-length-value block holding what the TLS bind learned about the client.
_Block_Type_TLS = 0x20

# The sub-block inside it holding the common name of the verified client certificate.
_Sub_Block_Type_TLS_Common_Name = 0x22

# How many bytes of the TLS block precede its sub-blocks - one flags byte and a four-byte verify result.
_TLS_Block_Header_Length = 5

# Every type-length-value block opens with a type byte and a two-byte length.
_Block_Header_Length = 3

# ################################################################################################################################
# ################################################################################################################################

class ProxyHeader:
    """ What one PROXY protocol header said about the connection carrying it.
    """

    def __init__(self) -> 'None':

        # The address the load balancer accepted the connection from, empty for a health check
        self.client_ip = ''
        self.client_port = 0

        # The common name of the client certificate the TLS bind verified, empty when there was none
        self.client_common_name = ''

# ################################################################################################################################
# ################################################################################################################################

def _receive_exactly(sock:'socket.socket', byte_count:'int') -> 'bytes':
    """ Reads exactly byte_count bytes, which a stream socket is free to deliver in pieces.
    """
    chunks = []
    remaining = byte_count

    while remaining:

        chunk = sock.recv(remaining)

        # An empty read means the peer went away with the header half sent
        if not chunk:
            raise HL7Exception('Connection closed while reading the PROXY header')

        chunks.append(chunk)
        remaining -= len(chunk)

    out = b''.join(chunks)
    return out

# ################################################################################################################################

def _parse_tls_block(value:'bytes') -> 'str':
    """ Digs the client certificate common name out of the TLS block's sub-blocks.
    """

    # Everything before the sub-blocks is the flags byte and the verify result
    position = _TLS_Block_Header_Length
    value_length = len(value)

    while position + _Block_Header_Length <= value_length:

        sub_block_type = value[position]
        sub_block_length = unpack('!H', value[position + 1:position + _Block_Header_Length])[0]
        position += _Block_Header_Length

        if sub_block_type == _Sub_Block_Type_TLS_Common_Name:
            out = value[position:position + sub_block_length].decode('utf-8', errors='replace')
            return out

        position += sub_block_length

    return ''

# ################################################################################################################################

def _parse_optional_blocks(header:'ProxyHeader', data:'bytes') -> 'None':
    """ Walks the optional blocks trailing the address block, taking the one that carries TLS details.
    """
    position = 0
    data_length = len(data)

    while position + _Block_Header_Length <= data_length:

        block_type = data[position]
        block_length = unpack('!H', data[position + 1:position + _Block_Header_Length])[0]
        position += _Block_Header_Length

        if block_type == _Block_Type_TLS:
            header.client_common_name = _parse_tls_block(data[position:position + block_length])

        position += block_length

# ################################################################################################################################

def read_proxy_header(sock:'socket.socket') -> 'ProxyHeader':
    """ Reads one PROXY protocol version 2 header off the socket, leaving the stream positioned
    at the first byte of the application payload.
    """

    signature = _receive_exactly(sock, len(Signature))

    if signature != Signature:
        raise HL7Exception('Connection did not open with a PROXY protocol header')

    out = _read_after_signature(sock)
    return out

# ################################################################################################################################

def read_optional_proxy_header(sock:'socket.socket') -> 'tuple':
    """ Reads the header a load balancer prefixes a connection with, for a connection that has
    one. A sender that reached this socket directly opens with its message instead, so the bytes
    read to tell the two apart are handed back rather than consumed.

    Returns the header and whatever of the application payload was already read - a connection
    that carried a header has nothing of its payload read yet, and one that carried none has
    no header to report.
    """

    opening = _receive_exactly(sock, len(Signature))

    # The message itself opens the connection, and what was read is the beginning of it
    if opening != Signature:
        return None, opening

    # The load balancer announced the sender, and the rest of what it said follows
    header = _read_after_signature(sock)
    return header, b''

# ################################################################################################################################

def _read_after_signature(sock:'socket.socket') -> 'ProxyHeader':
    """ Reads the rest of a version 2 header whose signature has already been read off the socket.
    """

    sizing = _receive_exactly(sock, _Sizing_Length)

    version_and_command = sizing[0]
    family_and_protocol = sizing[1]
    remainder_length = unpack('!H', sizing[2:])[0]

    if version_and_command & 0xf0 != _Version_2:
        raise HL7Exception('Unsupported PROXY protocol version')

    remainder = _receive_exactly(sock, remainder_length)

    out = ProxyHeader()
    command = version_and_command & 0x0f

    # A health check carries no addresses at all and leaves the header empty
    if command == _Command_Local:
        return out

    if command != _Command_Proxy:
        raise HL7Exception('Unsupported PROXY protocol command')

    family = family_and_protocol & 0xf0

    # An unspecified family means the addresses were not translated and none can be reported
    if family == _Family_Unspecified:
        return out

    if family not in _Address_Length:
        raise HL7Exception('Unsupported PROXY protocol address family')

    address_length = _Address_Length[family]

    if remainder_length < address_length:
        raise HL7Exception('PROXY protocol header is shorter than its address family requires')

    address_block = remainder[:address_length]

    if family == _Family_Inet:
        out.client_ip = socket.inet_ntop(socket.AF_INET, address_block[:4])
        out.client_port = unpack('!H', address_block[8:10])[0]

    elif family == _Family_Inet6:
        out.client_ip = socket.inet_ntop(socket.AF_INET6, address_block[:16])
        out.client_port = unpack('!H', address_block[32:34])[0]

    # A Unix socket peer has a path rather than an address, and nothing here reports paths

    _parse_optional_blocks(out, remainder[address_length:])

    return out

# ################################################################################################################################
# ################################################################################################################################
