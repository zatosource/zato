# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import time

# Zato
from zato.common.api import GENERIC
from zato.common.util.api import asbool

# Zato - test helpers
from conftest import wait_for_port_open

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The launcher the environment under test was built with, which is what runs enmasse against it
_zato_binary = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')

# How long enmasse waits for an object a definition refers to but has not seen yet
_missing_wait_time = '15'

# How long the import is given before the run is called off
_import_timeout = 120

# The two channels this module creates, each saved with the default flag, one after the other
_first_channel_name  = 'test-mllp-default-first'
_second_channel_name = 'test-mllp-default-second'

_channel_service_name = 'test.hl7.mllp.echo'

# How long to wait for routes to settle after an import
_settle_seconds = 1

# ################################################################################################################################
# ################################################################################################################################

def _definitions(channel_name:'str') -> 'str':
    out = f"""
channel_mllp:
  - name: {channel_name}
    service: {_channel_service_name}
    is_default: true
"""
    return out

# ################################################################################################################################

def _run_import(input_path:'str', server_directory:'str') -> 'any_':
    command = [
        _zato_binary, 'enmasse', server_directory,
        '--verbose',
        '--import',
        '--input', input_path,
        '--missing-wait-time', _missing_wait_time,
    ]

    result = subprocess.run(command, capture_output=True, text=True, timeout=_import_timeout)
    return result

# ################################################################################################################################

def _import_channel(directory:'str', server_directory:'str', channel_name:'str') -> 'None':
    input_path = os.path.join(directory, f'{channel_name}.yaml')

    with open(input_path, 'w') as input_file:
        _ = input_file.write(_definitions(channel_name))

    result = _run_import(input_path, server_directory)

    if result.returncode != 0:
        raise Exception(f'enmasse import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

# ################################################################################################################################

def _default_channel_names(zato_client:'any_') -> 'anylist':
    """ The names of the channels of this module that store the default flag.
    """
    items, _ = zato_client.get_list('zato.generic.connection.get-list',
        cluster_id=1, type_=GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP)

    out = []

    for item in items:

        if item['name'] not in (_first_channel_name, _second_channel_name):
            continue

        # A channel that was never saved with the flag has no such key
        if 'is_default' not in item:
            continue

        if asbool(item['is_default']):
            out.append(item['name'])

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOnlyOneChannelStoresTheDefaultFlag:
    """ Only one channel can be the default at a time, so the second channel saved with the flag
    takes it from the first, in what is stored as much as in the router.
    """

# ################################################################################################################################

    def test_01_create_the_first_default_channel(self, zato_server:'dict', mllp_port:'int', tmp_path:'any_') -> 'None':

        _import_channel(str(tmp_path), zato_server['server_directory'], _first_channel_name)

        wait_for_port_open(mllp_port)
        time.sleep(_settle_seconds)

# ################################################################################################################################

    def test_02_the_second_default_channel_takes_the_flag(
        self,
        zato_client:'any_',
        zato_server:'dict',
        tmp_path:'any_',
        ) -> 'None':

        assert _default_channel_names(zato_client) == [_first_channel_name]

        _import_channel(str(tmp_path), zato_server['server_directory'], _second_channel_name)
        time.sleep(_settle_seconds)

        assert _default_channel_names(zato_client) == [_second_channel_name]

# ################################################################################################################################

    def test_03_a_file_naming_two_default_channels_is_refused(
        self,
        zato_client:'any_',
        zato_server:'dict',
        tmp_path:'any_',
        ) -> 'None':
        """ One file cannot make two channels the default - imported, it would leave the flag with the last of
        them alone and its export would no longer reproduce it, so the import is refused before anything is written.
        """
        two_defaults = _definitions(_first_channel_name) + _definitions(_second_channel_name).split('channel_mllp:')[1]

        input_path = os.path.join(str(tmp_path), 'two-defaults.yaml')
        with open(input_path, 'w') as input_file:
            _ = input_file.write(two_defaults)

        result = _run_import(input_path, zato_server['server_directory'])

        assert result.returncode != 0
        assert 'Only one HL7 MLLP channel can be the default' in result.stdout + result.stderr
        assert _default_channel_names(zato_client) == [_second_channel_name]

# ################################################################################################################################
# ################################################################################################################################
