# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import spawn

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.pubsub_database import is_postgresql_mode
from zato.common.test.pubsub_in_process_support import SQLiteWriteLock

from .conftest import Security_Pull, Topic_Pull, Topic_Second
from .helpers import sqlite_db_path, sub_key_for_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def test_publication_after_lock_contention(in_process_server:'any_') -> 'None':
    """ A publication after a contended write still delivers and stores its payload.
    """
    server, _push_endpoint = in_process_server
    backend = server.server.pubsub_backend

    data = 'after.lock.' + CryptoManager.generate_hex_string(8)
    result = backend.publish(Topic_Pull, data)

    assert result.msg_id

    subscription_list = server.server.pubsub_subscription_list
    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    messages = backend.fetch_messages(sub_key, max_messages=10)

    found = False

    for message in messages:
        if message['data'] == data:
            found = True
            break

    assert found

# ################################################################################################################################

def test_enmasse_create_while_sqlite_lock_held(in_process_server:'any_') -> 'None':
    """ An enmasse create held behind the SQLite write lock still delivers after the lock is released.
    """
    server, _push_endpoint = in_process_server

    if is_postgresql_mode(server.db_mode):
        return

    parallel = server.server
    backend = parallel.pubsub_backend

    enmasse_yaml = f"""
pubsub_subscription:
  - security: {Security_Pull}
    delivery_type: pull
    topic_list:
      - {Topic_Pull}
      - {Topic_Second}
"""

    lock = SQLiteWriteLock(sqlite_db_path(server))
    lock.acquire()

    try:
        import_greenlet = spawn(server.apply_enmasse, 'create-while-locked', enmasse_yaml)
        lock.release()
        exit_code = import_greenlet.get()
    finally:
        if lock._process:
            lock.release()

    assert exit_code == 0

    data = 'after.enmasse.lock.' + CryptoManager.generate_hex_string(8)
    result = backend.publish(Topic_Second, data)

    assert result.msg_id

    sub_key = sub_key_for_topic(parallel.pubsub_subscription_list, Topic_Second)
    messages = backend.fetch_messages(sub_key, max_messages=10)

    found = False

    for message in messages:
        if message['data'] == data:
            found = True
            break

    assert found

# ################################################################################################################################
# ################################################################################################################################
