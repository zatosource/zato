# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK
from threading import Thread

# Zato
from pubsub_exactly_once.database import add_insert_delay, postgresql_only, remove_insert_delay, restart_database, \
    sqlite_only, terminate_session, wait_for_delayed_session
from pubsub_exactly_once.harness import get_engine, Hold_Timeout, import_enmasse, new_keys, publish_input, publish_inputs, \
    Settle_Timeout, stage_batch, verify
from pubsub_exactly_once.rest import ack, drain, publish, pull_by_key
from pubsub_exactly_once.server import kill_server, kill_worker, start_server
from zato.common.test.exactly_once.config import TestConfig
from zato.common.test.exactly_once.control import arm_write_hold, count_invocations, hold, release, release_write_hold, \
    wait_for_invocations, wait_for_write_hold, wait_until_held
from zato.common.test.exactly_once.verify import count_deliveries

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

# How many input messages each test publishes
_batch_count = 10

# The topics of the cycle of a pull client
_orders_topic   = 'orders'
_invoices_topic = 'invoices'

# How long the request of an acknowledgement is waited for after the server was killed, in seconds
_request_join_timeout = 60.0

# ################################################################################################################################
# ################################################################################################################################

class _BackgroundAck:
    """ An acknowledgement sent in a thread of its own, whose server may be killed before it responds.
    """

    def __init__(self, payload:'anydict') -> 'None':
        self.payload = payload
        self.thread = Thread(target=self.run, daemon=True)

# ################################################################################################################################

    def run(self) -> 'None':

        # The connection of the request is closed when the server is killed, which is the outcome this test expects.
        try:
            _ = ack(TestConfig.orders_username, TestConfig.orders_password, self.payload)
        except OSError:
            pass

# ################################################################################################################################
# ################################################################################################################################

def test_worker_killed_during_processing(zato_server:'any_') -> 'None':
    """ A batch whose worker is killed while its last key is held relays each key once,
    once the new worker delivered the batch again.
    """
    prefix, keys = new_keys(_batch_count)
    last_key = keys[-1]

    stage_batch(keys)
    kill_worker()

    # The invocation that the killed worker held is gone, only its control file remains.
    release(last_key)

    _ = verify(prefix, keys)
    assert count_invocations(last_key) >= 2

# ################################################################################################################################

def test_server_killed_during_processing(zato_server:'any_') -> 'None':
    """ A batch whose server is killed while its last key is held relays each key once,
    once the server started again delivered the batch again.
    """
    prefix, keys = new_keys(_batch_count)
    last_key = keys[-1]

    stage_batch(keys)
    kill_server()

    release(last_key)
    start_server()

    _ = verify(prefix, keys)
    assert count_invocations(last_key) >= 2

# ################################################################################################################################

@postgresql_only
def test_session_terminated_during_commit(zato_server:'any_') -> 'None':
    """ A batch whose database session is terminated while it inserts its publications relays each key once.
    """
    prefix, keys = new_keys(_batch_count)
    delayed_key = keys[5]

    # The insert of the output of one key waits in its transaction ..
    add_insert_delay(delayed_key)

    try:
        publish_inputs(keys)

        # .. where its session is terminated.
        pid = wait_for_delayed_session()
        terminate_session(pid)

    finally:
        remove_insert_delay()

    _ = verify(prefix, keys)

# ################################################################################################################################

@postgresql_only
def test_database_restarted_during_batch(zato_server:'any_') -> 'None':
    """ A batch whose database is killed and started again while its last key is held relays each key once.
    """
    prefix, keys = new_keys(_batch_count)
    last_key = keys[-1]

    stage_batch(keys)
    restart_database()

    release(last_key)

    _ = verify(prefix, keys)

# ################################################################################################################################

@postgresql_only
def test_server_killed_during_pull_ack(zato_server:'any_') -> 'None':
    """ An acknowledgement whose server is killed while it inserts its publication is repeated once the server
    started again, and the order is acknowledged with its publication stored once.
    """
    _ = drain(TestConfig.orders_username, TestConfig.orders_password)
    _ = drain(TestConfig.verifier_username, TestConfig.verifier_password)

    _, keys = new_keys(1)
    key = keys[0]

    # An order is published and pulled ..
    order_payload:'anydict' = {'data': {'key': key}}
    order_result = publish(TestConfig.publisher_username, TestConfig.publisher_password, _orders_topic, order_payload)

    assert order_result.status_code == OK, order_result

    order_msg_id = order_result.body['msg_id']
    message = pull_by_key(TestConfig.orders_username, TestConfig.orders_password, key)
    meta = message['meta']

    invoice_msg_id = f'{order_msg_id}.invoice'

    consumed = {
        'msg_id': meta['msg_id'],
        'delivery_attempt': meta['delivery_attempt'],
    }

    invoice = {
        'topic_name': _invoices_topic,
        'data': {'key': key},
        'msg_id': invoice_msg_id,
        'correl_id': key,
    }

    ack_payload:'anydict' = {
        'consumed': [consumed],
        'publish': [invoice],
    }

    # .. the insert of its invoice waits in its transaction, where the server is killed ..
    add_insert_delay(key)

    try:
        background = _BackgroundAck(ack_payload)
        background.thread.start()

        pid = wait_for_delayed_session()
        kill_server()

        background.thread.join(_request_join_timeout)

        # .. and the session that the killed server left in the delay is ended ..
        terminate_session(pid)

    finally:
        remove_insert_delay()

    # .. the server starts again ..
    start_server()

    # .. and the same acknowledgement repeated succeeds ..
    result = ack(TestConfig.orders_username, TestConfig.orders_password, ack_payload)

    assert result.status_code == OK, result
    assert result.body['published'] == [invoice_msg_id], result

    # .. with the order acknowledged and its invoice received once.
    engine = get_engine()
    assert count_deliveries(engine, order_msg_id) == 0

    received:'anylist' = []
    messages = drain(TestConfig.verifier_username, TestConfig.verifier_password)

    for item in messages:
        item_meta = item['meta']
        received.append(item_meta['msg_id'])

    assert received == [invoice_msg_id], received

# ################################################################################################################################

@sqlite_only
def test_subscription_edit_during_batch_commit(zato_server:'any_') -> 'None':
    """ A batch whose commit waits for the write lock while its delivery is stopped and started again,
    and whose new delivery processes it again, relays each key once.
    """
    prefix, keys = new_keys(_batch_count)

    gate_key = keys[0]
    batch_keys = keys[1:]
    lock_key = batch_keys[0]

    # The first key keeps the delivery busy while the others are published ..
    hold(gate_key)
    publish_input(gate_key)
    wait_until_held(gate_key, Hold_Timeout)

    publish_inputs(batch_keys)

    # .. the first invocation of the next batch takes the write lock of the process ..
    arm_write_hold(lock_key)
    release(gate_key)
    wait_for_write_hold(Hold_Timeout)

    try:

        # .. the batch is processed and its commit waits for the lock ..
        wait_for_invocations(batch_keys, 1, Hold_Timeout)

        # .. the delivery is stopped and started again, and the new delivery processes the same batch ..
        import_enmasse(False)
        import_enmasse(True)

        wait_for_invocations(batch_keys, 2, Settle_Timeout)

    # .. and the lock is released, which lets both commits of the batch proceed.
    finally:
        release_write_hold()

    _ = verify(prefix, keys)

# ################################################################################################################################
# ################################################################################################################################
