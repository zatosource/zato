# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from json import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

# What the services of a test server receive is kept in files of the server's directory, one JSON line per item,
# because a message is delivered by whichever worker owns its subscriber key and read back through any other.
_received_dir_name = 'test-received'

# ################################################################################################################################
# ################################################################################################################################

def _get_store_path(service:'Service', store_name:'str') -> 'str':
    out = os.path.join(service.server.base_dir, _received_dir_name, store_name + '.jsonl')
    return out

# ################################################################################################################################

def record(service:'Service', store_name:'str', item:'any_') -> 'None':
    """ Appends one item to a store, in a single write, so the lines of concurrent writers never interleave.
    """
    path = _get_store_path(service, store_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    line = dumps(item) + '\n'

    with open(path, 'a') as f:
        _ = f.write(line)

# ################################################################################################################################

def read_items(service:'Service', store_name:'str') -> 'anylist':
    """ Returns each item of a store, in the order in which they were recorded.
    """
    path = _get_store_path(service, store_name)

    # A store that nothing was recorded to yet holds no items
    if not os.path.exists(path):
        return []

    with open(path) as f:
        out = [loads(line) for line in f]

    return out

# ################################################################################################################################

def clear(service:'Service', store_name:'str') -> 'None':
    """ Removes every item of a store.
    """
    path = _get_store_path(service, store_name)

    if os.path.exists(path):
        os.remove(path)

# ################################################################################################################################
# ################################################################################################################################
