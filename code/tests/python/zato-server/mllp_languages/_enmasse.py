# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess

# Zato
from _certs import Java_Client_Subject_DN
from _services import Plain_Service_Name, TLS_Service_Name

# ################################################################################################################################
# ################################################################################################################################

# The launcher the environment under test was built with, which is what runs enmasse against it
_Zato_Binary = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')

# The security definition the channel taking verified connections accepts a sender against
Security_Name = 'test.mllp.languages.mtls'

# The channels one test run creates
Plain_Channel_Name = 'test.mllp.languages.plain'
TLS_Channel_Name   = 'test.mllp.languages.tls'

# What a sender puts in MSH-3 to reach each of the two channels. Routing is by the sending
# application rather than by the port, so both channels are reachable over either bind and a
# message that arrives on the wrong one is turned away by the channel rather than by HAProxy.
Plain_Sending_Application = 'ZATO-TEST-PLAIN'
TLS_Sending_Application   = 'ZATO-TEST-TLS'

# How long enmasse waits for an object a definition refers to but has not seen yet
_Missing_Wait_Time = '15'

# How long the import is given before the run is called off
_Import_Timeout = 120

# ################################################################################################################################
# ################################################################################################################################

# The environment the tests operate on. Both channels take the raw message rather than a parsed one,
# because what the service records is compared against what the client sent, character for character.
_Definitions = f"""
security:

  - name: {Security_Name}
    type: mtls
    client_cert_subject_dn: {Java_Client_Subject_DN}

channel_hl7_mllp:

  - name: {Plain_Channel_Name}
    service: {Plain_Service_Name}
    msh3_sending_app: {Plain_Sending_Application}
    should_parse_on_input: false
    should_log_messages: true

  - name: {TLS_Channel_Name}
    service: {TLS_Service_Name}
    security: {Security_Name}
    msh3_sending_app: {TLS_Sending_Application}
    should_parse_on_input: false
    should_log_messages: true
"""

# ################################################################################################################################
# ################################################################################################################################

def create_environment(directory:'str', server_directory:'str') -> 'str':
    """ Creates the channels and the security definition the tests operate on, by importing them the
    way a user does. Returns the path of the file that was imported, which a failing run is read from.
    """
    input_path = os.path.join(directory, 'mllp-languages.yaml')

    with open(input_path, 'w') as input_file:
        _ = input_file.write(_Definitions)

    command = [
        _Zato_Binary, 'enmasse', server_directory,
        '--verbose',
        '--import',
        '--input', input_path,
        '--missing-wait-time', _Missing_Wait_Time,
    ]

    result = subprocess.run(command, capture_output=True, text=True, timeout=_Import_Timeout)

    if result.returncode != 0:
        raise Exception(f'enmasse import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    print(f'[ENMASSE] Imported {input_path}')

    out = input_path
    return out

# ################################################################################################################################
# ################################################################################################################################
