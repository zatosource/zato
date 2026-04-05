# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent monkey-patching must happen before any other imports
from gevent.monkey import patch_all as gevent_patch_all
gevent_patch_all()

# stdlib
import socket
from configparser import ConfigParser
from contextlib import contextmanager
from pathlib import Path
from threading import Thread

# gevent
from gevent import sleep as gsleep

# Bunch
from bunch import bunchify

# Zato
from zato.hl7.mllp.server import HL7MLLPServer

# ################################################################################################################################
# ################################################################################################################################

SB = b'\x0b'
EB_CR = b'\x1c\x0d'

# ################################################################################################################################
# ################################################################################################################################

def frame(payload:'bytes') -> 'bytes':
    return SB + payload + EB_CR

# ################################################################################################################################

def unframe(data:'bytes') -> 'bytes':
    if data[:1] == SB and data[-2:] == EB_CR:
        return data[1:-2]
    return data

# ################################################################################################################################

def parse_ack(raw_bytes:'bytes') -> 'dict':
    """ Parses a raw ACK payload (already unframed) into a dict with ack_code, control_id, err_text, and msh_fields.
    """
    segments = raw_bytes.split(b'\x0d')
    out = {
        'ack_code': b'',
        'control_id': b'',
        'err_text': b'',
    }

    for seg in segments:
        if not seg:
            continue

        # Determine the field separator from MSH ..
        if seg.startswith(b'MSH'):
            field_sep = seg[3:4]
            fields = seg.split(field_sep)
            out['msh_fields'] = fields
            continue

        field_sep = seg[3:4] if len(seg) > 3 else b'|'

        if seg.startswith(b'MSA'):
            fields = seg.split(field_sep)
            if len(fields) > 1:
                out['ack_code'] = fields[1]
            if len(fields) > 2:
                out['control_id'] = fields[2]

        elif seg.startswith(b'ERR'):
            fields = seg.split(field_sep)
            if len(fields) > 1:
                out['err_text'] = fields[1]

    return out

# ################################################################################################################################

def build_adt_a01(
    control_id:'bytes'=b'CTRL001',
    sending_app:'bytes'=b'TestApp',
    sending_fac:'bytes'=b'TestFac',
    receiving_app:'bytes'=b'ZatoApp',
    receiving_fac:'bytes'=b'ZatoFac',
    version:'bytes'=b'2.5',
    charset:'bytes'=b'',
    ) -> 'bytes':
    """ Builds a minimal ADT^A01 message as raw bytes.
    """
    cr = b'\x0d'
    sep = b'|'

    msh_fields = [
        b'MSH', b'^~\\&',
        sending_app, sending_fac,
        receiving_app, receiving_fac,
        b'20240101120000', b'',
        b'ADT^A01', control_id,
        b'P', version,
        b'', b'', b'', b'', b'',
        charset,
    ]
    msh = sep.join(msh_fields)

    evn = sep.join([b'EVN', b'', b'20240101120000'])

    pid = sep.join([
        b'PID', b'', b'', b'12345^^^Hospital^PI', b'',
        b'DOE^JOHN^Q', b'', b'19800101', b'M',
    ])

    pv1 = sep.join([b'PV1', b'', b'I', b'W^100^1^Hospital'])

    return cr.join([msh, evn, pid, pv1]) + cr

# ################################################################################################################################

def load_server_config(ini_path:'str') -> 'Bunch':
    """ Reads a .ini file and returns a Bunch config suitable for HL7MLLPServer.
    """
    cp = ConfigParser()
    cp.read(str(ini_path))
    s = cp['server']

    config = bunchify({
        'id': s.get('id', 'test-1'),
        'name': s.get('name', 'test-hl7'),
        'address': ('127.0.0.1', 0),

        'service_name': s.get('service_name', 'test.service'),

        'read_buffer_size': s.getint('read_buffer_size', 2048),
        'recv_timeout': s.getfloat('recv_timeout', 1.0),
        'idle_timeout': s.getfloat('idle_timeout', 0),

        'logging_level': s.get('logging_level', 'INFO'),
        'should_log_messages': s.getboolean('should_log_messages', True),

        'start_seq': SB,
        'end_seq': EB_CR,

        'tcp_keepalive_idle': s.getint('tcp_keepalive_idle', 60),
        'tcp_keepalive_interval': s.getint('tcp_keepalive_interval', 10),
        'tcp_keepalive_count': s.getint('tcp_keepalive_count', 6),
    })

    return config

# ################################################################################################################################

def start_server(ini_path:'str', callback:'callable') -> 'tuple':
    """ Starts an HL7MLLPServer in a background thread using config from the given .ini file.
    """
    config = load_server_config(ini_path)
    server = HL7MLLPServer(config, callback)

    thread = Thread(target=server.start, daemon=True)
    thread.start()

    # Wait for the server to bind ..
    for _ in range(50):
        gsleep(0.05)
        if hasattr(server, 'impl') and server.impl.socket is not None:
            break

    host, port = server.impl.socket.getsockname()
    return server, host, port

# ################################################################################################################################

@contextmanager
def tcp_session(host:'str', port:'int', timeout:'float'=5.0) -> 'None':
    """ Context manager that yields a connected TCP socket.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect((host, port))
    try:
        yield sock
    finally:
        try:
            sock.close()
        except Exception:
            pass

# ################################################################################################################################

def tcp_send(host:'str', port:'int', data:'bytes', recv:'bool'=True, recv_size:'int'=65536, timeout:'float'=5.0) -> 'bytes':
    """ Opens a TCP connection, sends data, optionally reads the response, and closes.
    """
    with tcp_session(host, port, timeout=timeout) as sock:
        sock.sendall(data)
        if recv:
            return sock.recv(recv_size)
        return None

# ################################################################################################################################

def ini_path_from_test_file(test_file_path:'str') -> 'Path':
    """ Given __file__ of a test module, returns the path to its corresponding .ini file.
    """
    p = Path(test_file_path)
    return p.with_suffix('.ini')

# ################################################################################################################################
# ################################################################################################################################
