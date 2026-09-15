# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The objects a proof creates on the live server go in through enmasse, the way a deployment's do - a document
# built by the proof, written next to the server's own and imported against the running server with the same
# CLI that imported the server's own document before it started. With the server running, the CLI has it reload
# its configuration once the import is in, so the objects are live by the time the import returns.

# stdlib
import os
import subprocess
from copy import deepcopy
from uuid import uuid4

# PyYAML
import yaml

# Zato
from zato.common.defaults import default_cluster_id

# Test helpers
from live_config import LiveServer
from live_trace import Channel_Enmasse, Received, Sent, separator, trace

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict, anydictnone

# ################################################################################################################################
# ################################################################################################################################

# The zato binary - the same one the fixture starts the server with
_zato_bin = os.path.join(os.environ['ZATO_TEST_BASE_DIR'], 'code', 'bin', 'zato')

# How long one import may take, in seconds - the CLI starts a process of its own, syncs the ODB and waits
# for the server to reload its configuration
_import_timeout = 120

# What each imported object's file is called - one file per import, each kept next to the server's own document
_document_prefix = 'enmasse-live-'

# What a deactivating import sets on every object of the document
_is_active_key = 'is_active'

# ################################################################################################################################
# ################################################################################################################################

def _document_path() -> 'str':
    """ Where the next document goes - the quickstart directory the server's own enmasse document was written to.
    """
    quickstart_directory = os.path.dirname(LiveServer.server_directory)
    out = os.path.join(quickstart_directory, f'{_document_prefix}{uuid4().hex}.yaml')
    return out

# ################################################################################################################################

def import_document(document:'anydict') -> 'None':
    """ Imports one enmasse document against the running live server - written to a file of its own, handed to
    the enmasse CLI with the server directory, and the server's configuration reloaded by the CLI once the import
    is in. An import that fails raises with everything the CLI said.
    """
    path = _document_path()
    text = yaml.safe_dump(document, sort_keys=False)

    with open(path, 'w') as document_file:
        _ = document_file.write(text)

    trace(Channel_Enmasse, Sent, f'import {path}')
    trace(Channel_Enmasse, Sent, text)

    command = [_zato_bin, 'enmasse', '--import', '--input', path, LiveServer.server_directory]
    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=_import_timeout)

    if result.returncode != 0:
        raise RuntimeError(f'enmasse import failed for {path}:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    trace(Channel_Enmasse, Received, f'imported {path}')
    separator(Channel_Enmasse)

# ################################################################################################################################

def deactivate_document(document:'anydict') -> 'None':
    """ Imports the document again with every object of it inactive - what a proof does with its own objects once
    it is through with them, so the server stops serving, pinging or listening for them while the ODB keeps them.
    """
    inactive = deepcopy(document)

    for items in inactive.values():
        for item in items:
            item[_is_active_key] = False

    import_document(inactive)

# ################################################################################################################################

def find_by_name(client:'AdminClient', service_name:'str', name:'str') -> 'anydictnone':
    """ One object of a get-list service by its name, or None when the server has none of that name - how a proof
    learns the id of an object it imported. A list service answers with the list itself, unwrapped.
    """
    items, _ = client.get_list(service_name, cluster_id=default_cluster_id)

    for item in items:
        if item['name'] == name:
            return item

    return None

# ################################################################################################################################

def get_id_by_name(client:'AdminClient', service_name:'str', name:'str') -> 'int':
    """ The id of an object the proof just imported, by its name - the import put it there, so it is found.
    """
    item = find_by_name(client, service_name, name)

    if item is None:
        raise Exception(f'Object `{name}` not found through {service_name}')

    out = item['id']
    return out

# ################################################################################################################################
# ################################################################################################################################
