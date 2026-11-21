# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager

from .conftest import Topic_Pull

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_publication_on_postgresql(postgresql_server:'any_') -> 'None':
    """ A publication on PostgreSQL commits under the lock timeout of the transaction.
    """
    server, _push_endpoint = postgresql_server
    backend = server.server.pubsub_backend

    data = 'pg.lock.' + CryptoManager.generate_hex_string(8)
    result = backend.publish(Topic_Pull, data)

    assert result.msg_id

# ################################################################################################################################
# ################################################################################################################################
