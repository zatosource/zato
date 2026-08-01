# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import tempfile
import time

# Zato
from zato.common.crypto.api import CryptoManager

# Zato - the suite's own parts
from _outconn_messages import build_adt_a01
from _outconn_services import Send_Service_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import any_, anydict, anylist

    AdminClient = AdminClient
    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# What every connection here is created with, which is the command a user takes to the same end
_zato_binary = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')

# The key an outgoing MLLP connection is written under in an enmasse file
_Definition_Key = 'outgoing_mllp'

# How long one import is given to reach the server and come back
_Import_Timeout = 180

# How long the import waits for anything a definition names that is not there yet
_Missing_Wait_Time = 15

# How many bits the random part of a connection's name is made of. Every test names its own
# connection so that a run of the whole suite never has two tests share one.
_Name_Bits = 32

# How long the server is given to have built the pool behind a newly created connection. A send
# through a connection whose pool is still filling would be reported as the connection not being
# there rather than as anything about what is at the other end of it.
_Ready_Timeout = 20.0

# How often a newly created connection is tried while waiting for it
_Ready_Poll_Interval = 0.25

# The message a readiness check sends, whose only job is to reach the far end at all
_Ready_Control_Id = 'READINESS'

# ################################################################################################################################
# ################################################################################################################################

def _build_name(label:'str') -> 'str':
    """ Builds a name for one connection - the test's own label with enough randomness after it
    that a rerun never collides with what a previous one left behind.
    """
    suffix = CryptoManager.generate_hex_string(_Name_Bits)

    out = f'test-mllp-outconn-{label}-{suffix}'
    return out

# ################################################################################################################################

def _to_yaml_value(value:'any_') -> 'str':
    """ Writes one configured value the way the file reads it back as what it went in as - a count
    as a count, a switch as a switch, and everything else quoted, framing bytes included.
    """
    if value is True:
        out = 'true'

    elif value is False:
        out = 'false'

    elif isinstance(value, int):
        out = str(value)

    # .. anything else is text, and text that a reader could take for a number - the framing
    # .. sequences are written in hexadecimal - has to say that it is text.
    else:
        out = "'" + str(value) + "'"

    return out

# ################################################################################################################################

def _build_definition(name:'str', address:'str', config:'anydict') -> 'str':
    """ Builds the enmasse file one connection is created from.
    """
    lines = [
        f'{_Definition_Key}:',
        '',
        f'  - name: {name}',
        f'    address: {address}',
    ]

    for key, value in config.items():
        written = _to_yaml_value(value)
        lines.append(f'    {key}: {written}')

    out = '\n'.join(lines) + '\n'
    return out

# ################################################################################################################################

def create_outconn(environment:'any_', label:'str', address:'str', **config:'any_') -> 'str':
    """ Creates one MLLP outgoing connection and returns its name. Anything not named here is left
    at the default the connection type carries, which is what a connection created any other way
    gets. The connection stays for the rest of the run, the whole environment being a throwaway one.
    """
    name = _build_name(label)
    definition = _build_definition(name, address, config)

    definition_path = os.path.join(tempfile.gettempdir(), f'{name}.yaml')

    with open(definition_path, 'w') as definition_file:
        _ = definition_file.write(definition)

    command = [
        _zato_binary, 'enmasse', environment.server_directory,
        '--verbose',
        '--import',
        '--input', definition_path,
        '--missing-wait-time', str(_Missing_Wait_Time),
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=_Import_Timeout)

        if result.returncode != 0:
            raise Exception(f'Could not create {name}:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    finally:
        os.unlink(definition_path)

    return name

# ################################################################################################################################

def send(client:'AdminClient', name:'str', data:'str', count:'int'=1, control_ids:'anylist | None'=None) -> 'anylist':
    """ Sends one message, or several at once, through a connection and returns what came back from
    each of them - the acknowledgment where there was one and the error where there was not.
    """
    payload:'anydict' = {
        'outconn': name,
        'data': data,
        'count': count,
    }

    if control_ids:
        payload['control_ids'] = control_ids

    response = client.invoke(Send_Service_Name, payload)

    out = response['results']
    return out

# ################################################################################################################################

def send_one(client:'AdminClient', name:'str', data:'str') -> 'anydict':
    """ Sends one message through a connection and returns what came back from it.
    """
    results = send(client, name, data)

    out = results[0]
    return out

# ################################################################################################################################

def wait_until_ready(client:'AdminClient', name:'str') -> 'None':
    """ Waits until a newly created connection can be sent through. The pool behind a connection is
    built after the connection itself is stored, so the first send through it may find nothing to
    take from the pool yet.
    """
    probe_message = build_adt_a01(_Ready_Control_Id)

    deadline = time.monotonic() + _Ready_Timeout
    last_error = ''

    while time.monotonic() < deadline:

        try:
            result = send_one(client, name, probe_message)
        except Exception as exception:
            last_error = str(exception)
            time.sleep(_Ready_Poll_Interval)
            continue

        # A message that reached the far end at all means the pool is there, whatever the far end
        # then had to say about the message itself
        if result['is_sent']:
            return

        last_error = result['error_text']

        # A connection whose pool is not built yet reports that there is no connection of that
        # name, whereas anything about the far end means the pool is there and this is done
        if 'KeyError' not in last_error:
            return

        time.sleep(_Ready_Poll_Interval)

    raise Exception(f'The connection {name} was not ready within {_Ready_Timeout}s, last error: {last_error}')

# ################################################################################################################################
# ################################################################################################################################
