# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import subprocess

# Zato
from hl7_client.java_build import build_project, get_launcher_path, is_java_available
from hl7_client.python_client import SendResult

# ################################################################################################################################
# ################################################################################################################################

# What the client's Gradle project is called, which is also what its launcher is named after
_Project_Name = 'hl7-mllp-client'

# The launcher the runner invokes
_Launcher_Path = get_launcher_path(_Project_Name)

# How long one send is given, above the client's own read timeout so that a listener that never
# answers is reported by the client rather than by the process being cut short here
_Send_Timeout = 60

# The check for a Java runtime is the same one every Java-backed helper here makes, and it is
# re-exported so that a caller of this module has no second module to import for it
is_java_available = is_java_available

# ################################################################################################################################
# ################################################################################################################################

def build_client() -> 'None':
    """ Builds the HAPI client with Gradle, unless what is already installed is newer than
    its sources. The first build downloads the HAPI dependencies from Maven Central.
    """
    _ = build_project(_Project_Name)

# ################################################################################################################################

def _parse_output(output:'str') -> 'SendResult':
    """ Reads the MSA fields out of the lines the client printed.
    """
    fields = {}

    for line in output.splitlines():
        if '=' in line:
            key, _, value = line.partition('=')
            fields[key] = value

    if 'msa_1' not in fields:
        raise Exception(f'No MSA fields in the Java client output:\n{output}')

    out = SendResult(fields['msa_1'], fields['msa_2'], fields['msa_3'])
    return out

# ################################################################################################################################

def send_message(
    host:'str',
    port:'int',
    control_id:'str',
    sending_app:'str',
    sending_facility:'str' = '',
    message_type:'str' = 'ADT',
    trigger_event:'str' = 'A01',
    ) -> 'SendResult':
    """ Sends one HL7 message with the Java HAPI client and returns what its acknowledgment's
    MSA segment said. The client is built first when it has to be.
    """
    build_client()

    command = [
        _Launcher_Path,
        '--host', host,
        '--port', str(port),
        '--control-id', control_id,
        '--sending-app', sending_app,
        '--sending-facility', sending_facility,
        '--message-type', message_type,
        '--trigger-event', trigger_event,
    ]

    result = subprocess.run(command, capture_output=True, text=True, timeout=_Send_Timeout)

    if result.returncode != 0:
        raise Exception(f'The Java HAPI client failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    out = _parse_output(result.stdout)
    return out

# ################################################################################################################################
# ################################################################################################################################
