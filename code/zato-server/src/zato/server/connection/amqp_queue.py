# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a broker says about a queue, asked outside of any consumer.

# Zato
from zato.server.connection.amqp_ import get_conn_url, get_connection_class

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The suffix the broker sees these short-lived connections under
_conn_suffix = 'queue-depth'

_tls_scheme = 'amqps://'

# ################################################################################################################################
# ################################################################################################################################

def get_queue_depth(name:'str', address:'str', username:'str', password:'str', queue:'str') -> 'int':
    """ How many messages wait in a queue, as the broker says it, read with a passive declare over a connection
    opened for this one question and closed right after it.
    """
    conn_url = get_conn_url(address, username, password)
    is_tls = conn_url.startswith(_tls_scheme)

    conn_class = get_connection_class(name, _conn_suffix, is_tls)

    with conn_class(conn_url) as connection:
        channel:'any_' = connection.channel()

        # A passive declare only asks about a queue that already exists, it never creates one
        declaration = channel.queue_declare(queue=queue, passive=True)
        out = declaration.message_count

    return out

# ################################################################################################################################
# ################################################################################################################################
