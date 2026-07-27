# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import subprocess
import tempfile
from base64 import b64decode, b64encode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _certs import TestCertificates

    TestCertificates = TestCertificates

# ################################################################################################################################
# ################################################################################################################################

# Where the clients of every language live
_Clients_Directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clients')

# The Java client and where compiling it puts what it compiled to. The build directory sits inside
# the source tree rather than in a temporary one so that a second run has nothing left to compile.
_Java_Directory = os.path.join(_Clients_Directory, 'java')
_Java_Source_Path = os.path.join(_Java_Directory, 'MllpClient.java')
_Java_Build_Directory = os.path.join(_Java_Directory, '.build')
_Java_Class_Path = os.path.join(_Java_Build_Directory, 'MllpClient.class')

# The class the Java client is entered through
_Java_Main_Class = 'MllpClient'

# What the clients of every language report each acknowledgment they read back with
_Ack_Prefix = 'ACK_BASE64: '

# How many connections one send travels over when the caller has no reason to ask for more
_Default_Connection_Count = 1

# How long compiling is given
_Build_Timeout = 120

# How long one send is given, which is above the client's own read timeout so that a channel that
# never answers is reported by the client rather than by the process being cut short here.
_Send_Timeout = 60

# ################################################################################################################################
# ################################################################################################################################

def is_java_available() -> 'bool':
    """ Returns whether there is a Java compiler and runtime on this machine to build and run with.
    """
    if not shutil.which('javac'):
        return False

    if not shutil.which('java'):
        return False

    return True

# ################################################################################################################################

def _needs_build() -> 'bool':
    """ Returns whether the Java client has to be compiled, which is the case for a tree that has
    never been built and for one whose source has been edited since it last was.
    """
    if not os.path.exists(_Java_Class_Path):
        return True

    out = os.path.getmtime(_Java_Source_Path) > os.path.getmtime(_Java_Class_Path)
    return out

# ################################################################################################################################

def build_java() -> 'None':
    """ Compiles the Java client, unless what is already compiled is newer than its source.
    """
    if not _needs_build():
        print('[BUILD] The Java client is up to date')
        return

    os.makedirs(_Java_Build_Directory, exist_ok=True)

    command = ['javac', '-d', _Java_Build_Directory, _Java_Source_Path]
    result = subprocess.run(command, capture_output=True, text=True, timeout=_Build_Timeout)

    if result.returncode != 0:
        raise Exception(f'Could not compile the Java client:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    print(f'[BUILD] Compiled the Java client into {_Java_Build_Directory}')

# ################################################################################################################################

def _parse_acks(output:'str') -> 'list':
    """ Takes the acknowledgments out of what a client wrote to standard output, in the order
    the client reported them.
    """
    out = []

    for line in output.splitlines():
        if line.startswith(_Ack_Prefix):
            out.append(b64decode(line[len(_Ack_Prefix):]))

    if not out:
        raise Exception(f'No acknowledgment in the client output:\n{output}')

    return out

# ################################################################################################################################

def send_with_java(
    host:'str',
    port:'int',
    message:'str',
    certificates:'TestCertificates | None'=None,
) -> 'bytes':
    """ Sends one HL7 message with the Java client and returns the acknowledgment it read back,
    exactly as it arrived. Certificates turn the connection into a TLS one that presents them.
    """
    acks = send_many_with_java(host, port, [message], _Default_Connection_Count, certificates)

    out = acks[0]
    return out

# ################################################################################################################################

def send_many_with_java(
    host:'str',
    port:'int',
    messages:'list',
    connection_count:'int',
    certificates:'TestCertificates | None'=None,
) -> 'list':
    """ Sends every message with the Java client, spread over as many connections as asked for and
    all of them open at once, and returns the acknowledgments read back. What came back for which
    message is not said by the order, so a caller tells them apart by what each of them echoes.
    """

    # The messages travel by file because the carriage returns they separate their segments with
    # would not survive being passed on a command line, and base64 keeps one message to one line
    handle, message_path = tempfile.mkstemp(prefix='zato-mllp-java-', suffix='.hl7')

    try:
        with os.fdopen(handle, 'w') as message_file:
            for message in messages:
                encoded = b64encode(message.encode('utf8')).decode('ascii')
                _ = message_file.write(encoded + '\n')

        command = [
            'java', '-cp', _Java_Build_Directory, _Java_Main_Class,
            '--host', host,
            '--port', str(port),
            '--message-file', message_path,
            '--connections', str(connection_count),
        ]

        if certificates:
            command.extend([
                '--tls',
                '--ca-file', certificates.ca_cert_path,
                '--keystore', certificates.java_keystore_path,
                '--keystore-password', certificates.java_store_password,
            ])

        result = subprocess.run(command, capture_output=True, text=True, timeout=_Send_Timeout)

        if result.returncode != 0:
            raise Exception(f'The Java client failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

        out = _parse_acks(result.stdout)

        if len(out) != len(messages):
            raise Exception(f'Expected {len(messages)} acknowledgments, got {len(out)}:\n{result.stdout}')

        return out

    finally:
        if os.path.exists(message_path):
            os.remove(message_path)

# ################################################################################################################################
# ################################################################################################################################
