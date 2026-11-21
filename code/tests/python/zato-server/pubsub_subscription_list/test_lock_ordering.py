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
from zato_common_core.zato_common_core import SubscriptionList

from .conftest import Security_Pull, Topic_Pull, Topic_Second
from .helpers import add_topic_pending, remove_topic_pending, sqlite_db_path, status_of, sub_key_for_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

def _enmasse_add_second(security_name:'str') -> 'str':
    """ Returns an enmasse file that adds Topic_Second to the pull subscription.
    """
    out = f"""
pubsub_subscription:
  - security: {security_name}
    delivery_type: pull
    topic_list:
      - {Topic_Pull}
      - {Topic_Second}
"""
    return out

# ################################################################################################################################

def _enmasse_remove_pull(security_name:'str') -> 'str':
    """ Returns an enmasse file that leaves the pull subscription on Topic_Second only.
    """
    out = f"""
pubsub_subscription:
  - security: {security_name}
    delivery_type: pull
    topic_list:
      - {Topic_Second}
"""
    return out

# ################################################################################################################################

def test_addition_then_removal_before_publication(in_process_server:'any_') -> 'None':
    """ An addition and a removal whose row writes both fail leave the list governing the publication.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list
    backend = parallel.pubsub_backend

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)

    add_topic_pending(subscription_list, sub_key, Topic_Second)
    remove_topic_pending(subscription_list, sub_key, Topic_Second)

    data = 'lock.order.' + CryptoManager.generate_hex_string(8)
    result = backend.publish(Topic_Second, data)

    assert result.msg_id

    messages = backend.fetch_messages(sub_key, max_messages=20)

    for message in messages:
        assert message['data'] != data

# ################################################################################################################################

def test_publication_behind_lock_with_enmasse_addition(in_process_server:'any_') -> 'None':
    """ A publication queued behind a write lock while an enmasse file adds a topic still confirms the pair.
    """
    server, _push_endpoint = in_process_server

    if is_postgresql_mode(server.db_mode):
        return

    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list
    backend = parallel.pubsub_backend

    lock = SQLiteWriteLock(sqlite_db_path(server))
    lock.acquire()

    try:
        import_greenlet = spawn(server.apply_enmasse, 'add-second', _enmasse_add_second(Security_Pull))

        data = 'behind.lock.' + CryptoManager.generate_hex_string(8)
        publish_greenlet = spawn(backend.publish, Topic_Second, data)

        lock.release()

        exit_code = import_greenlet.get()
        result = publish_greenlet.get()

        assert exit_code == 0
        assert result.msg_id

        sub_key = sub_key_for_topic(subscription_list, Topic_Second)
        assert status_of(subscription_list, sub_key, Topic_Second) == SubscriptionList.STATUS_CONFIRMED

    finally:
        if lock._process:
            lock.release()

# ################################################################################################################################

def test_publication_behind_lock_with_enmasse_removal(in_process_server:'any_') -> 'None':
    """ A publication queued behind a write lock while an enmasse file removes a topic obeys the list.
    """
    server, _push_endpoint = in_process_server

    if is_postgresql_mode(server.db_mode):
        return

    parallel = server.server
    subscription_list = parallel.pubsub_subscription_list
    backend = parallel.pubsub_backend

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)
    add_topic_pending(subscription_list, sub_key, Topic_Second)
    _ = backend.sync_subscription_pairs([(sub_key, Topic_Second.lower())], [])
    subscription_list.mark_committed([(sub_key, Topic_Second.lower())], [])

    lock = SQLiteWriteLock(sqlite_db_path(server))
    lock.acquire()

    try:
        import_greenlet = spawn(server.apply_enmasse, 'remove-pull', _enmasse_remove_pull(Security_Pull))

        data = 'removal.behind.lock.' + CryptoManager.generate_hex_string(8)
        publish_greenlet = spawn(backend.publish, Topic_Pull, data)

        lock.release()

        exit_code = import_greenlet.get()
        result = publish_greenlet.get()

        assert exit_code == 0
        assert result.msg_id

        for candidate, pair_topic, pair_status in subscription_list.statuses():
            if candidate != sub_key:
                continue
            if pair_topic != Topic_Pull.lower():
                continue
            assert pair_status == SubscriptionList.STATUS_PENDING_REMOVAL

        # A governed pair that is not configured is withheld, whether the status is still pending removal or the row is gone
        assert subscription_list.withholds_pair(sub_key, Topic_Pull.lower())

    finally:
        if lock._process:
            lock.release()

# ################################################################################################################################
# ################################################################################################################################
