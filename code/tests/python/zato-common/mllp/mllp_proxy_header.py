# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from struct import pack

# Zato
from zato.common.hl7.mllp.proxy_protocol import Signature

# ################################################################################################################################
# ################################################################################################################################

# What the tests stand in for the load balancer with, so that a test can drive the listener without
# one in front of it. These mirror the reader's own constants, which are private to it.
_Version_2                      = 0x20
_Command_Proxy                  = 0x01
_Family_Inet                    = 0x10
_Protocol_Stream                = 0x01
_Block_Type_TLS                 = 0x20
_Sub_Block_Type_TLS_Common_Name = 0x22
_TLS_Client_Verified_Flags      = 0x01

# What the address block reports the connection as having arrived at, which the listener does not read
_Local_Address = '127.0.0.1'
_Local_Port    = 0

# ################################################################################################################################
# ################################################################################################################################

def build_proxy_header(client_ip:'str', client_port:'int', client_common_name:'str'='') -> 'bytes':
    """ Builds the version 2 header the load balancer prefixes a backend connection with.
    """

    # Only IPv4 is built here, which is what the load balancer's own backend connections use
    address_block = socket.inet_pton(socket.AF_INET, client_ip)
    address_block += socket.inet_pton(socket.AF_INET, _Local_Address)
    address_block += pack('!HH', client_port, _Local_Port)

    optional_blocks = b''

    if client_common_name:

        name_bytes = client_common_name.encode('utf-8')
        sub_block = pack('!BH', _Sub_Block_Type_TLS_Common_Name, len(name_bytes)) + name_bytes

        # The flags byte says a certificate was sent and verified, and the verify result is zero
        tls_block = pack('!BI', _TLS_Client_Verified_Flags, 0) + sub_block
        optional_blocks = pack('!BH', _Block_Type_TLS, len(tls_block)) + tls_block

    remainder = address_block + optional_blocks

    out = Signature
    out += pack('!BBH', _Version_2 | _Command_Proxy, _Family_Inet | _Protocol_Stream, len(remainder))
    out += remainder

    return out

# ################################################################################################################################
# ################################################################################################################################
