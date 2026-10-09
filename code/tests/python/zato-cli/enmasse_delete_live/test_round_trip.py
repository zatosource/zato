# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.cli.enmasse.importer.delete_targets import security_keyed_sections

# Zato - the suite's own parts
from _definitions import creation_file, deletion_file, name_of, round_trip_key, round_trip_sections, topic_of, username_of
from _support import is_listed, ModuleCtx as SupportCtx, Pickup, Runtime
from conftest import reload_free_server_environment, wait_for_runtime_service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_environment.quickstart import ZatoEnvironment
    from zato.common.test.client import AdminClient

# ################################################################################################################################
# ################################################################################################################################

# The sections the second server goes through without a configuration reload - a channel in the URL routing,
# a generic connection in its API map and a security definition in its store
_reload_free_sections = ('channel_rest', 'llm', 'security')

# What enmasse logs when the reload is off
_Reload_Skipped = 'Skipping config reload'

# ################################################################################################################################
# ################################################################################################################################

def _runtime_key(section:'str') -> 'str':
    """ What the runtime service identifies the object of a section by - the username for the pub/sub sections keyed
    by security, the name otherwise.
    """
    if section in security_keyed_sections:
        out = username_of(section)
    else:
        out = name_of(section)

    return out

# ################################################################################################################################

def _runtime_topic(section:'str') -> 'str':
    """ The topic the runtime service evaluates the pub/sub sections against, empty for every other section.
    """
    if section in security_keyed_sections:
        out = topic_of(section)
    else:
        out = ''

    return out

# ################################################################################################################################

def _round_trip(section:'str', client:'AdminClient', pickup:'Pickup', runtime:'Runtime') -> 'None':
    """ Creates the object of a section through the pickup directory, deletes it the same way and checks both
    the list service and the runtime after each step.
    """
    key = round_trip_key(section)
    runtime_key = _runtime_key(section)
    topic = _runtime_topic(section)

    # The object is created ..
    log = pickup.place(f'create-{section}', creation_file(section))
    assert SupportCtx.Import_OK in log, log

    assert is_listed(client, runtime, section, key), f'{section} `{key}` is not listed after its creation'
    assert runtime.is_present(section, runtime_key, topic), f'{section} `{runtime_key}` is not at runtime after its creation'

    # .. and the object is deleted.
    log = pickup.place(f'delete-{section}', deletion_file(section, key))
    assert SupportCtx.Import_OK in log, log

    assert not is_listed(client, runtime, section, key), f'{section} `{key}` is still listed after its deletion'
    assert not runtime.is_present(section, runtime_key, topic), f'{section} `{runtime_key}` is still at runtime'

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('section', round_trip_sections)
def test_round_trip(section:'str', client:'AdminClient', pickup:'Pickup', runtime:'Runtime') -> 'None':
    """ Every section that supports deletion creates and deletes its object through the pickup directory.
    """
    _round_trip(section, client, pickup, runtime)

# ################################################################################################################################
# ################################################################################################################################

def test_runtime_removal_without_reload(reload_free_environment:'ZatoEnvironment') -> 'None':
    """ A server whose pickup imports run without a configuration reload still removes the runtime state of a deleted
    object, through the configuration events the delete services publish.
    """
    environment = reload_free_environment
    client = environment.client()
    pickup = Pickup(environment)
    runtime = Runtime(client)

    # The objects are created while the reload is still on ..
    for section in _reload_free_sections:
        key = round_trip_key(section)
        log = pickup.place(f'create-{section}', creation_file(section))
        assert SupportCtx.Import_OK in log, log
        assert runtime.is_present(section, key), log

    # .. the server is restarted with the reload off for the enmasse processes it spawns ..
    environment.restart(reload_free_server_environment())
    client = environment.client()
    runtime = Runtime(client)
    wait_for_runtime_service(client)

    # .. and each deletion reaches the runtime without a reload.
    for section in _reload_free_sections:
        key = round_trip_key(section)
        assert runtime.is_present(section, key), f'{section} `{key}` is not at runtime after the restart'

        log = pickup.place(f'delete-{section}', deletion_file(section, key))
        assert SupportCtx.Import_OK in log, log
        assert _Reload_Skipped in log, log

        assert not is_listed(client, runtime, section, key), f'{section} `{key}` is still listed after its deletion'
        assert not runtime.is_present(section, key), f'{section} `{key}` is still at runtime after its deletion'

# ################################################################################################################################
# ################################################################################################################################
