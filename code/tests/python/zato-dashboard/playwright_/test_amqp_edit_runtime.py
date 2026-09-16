# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# kombu
from kombu import Connection

# Zato
from zato.cli.enmasse.client import get_server_client
from zato.common.api import AMQP
from zato.common.crypto.api import CryptoManager
from zato.common.test.playwright_pubsub import create_amqp_channel, create_outgoing_amqp, find_row_by_name, \
    navigate_to_page, submit_edit_form
from zato.common.test.rabbitmq_ import drain_queue, get_queue_depth, publish_to_exchange
from zato.common.util.tcp import get_free_port

# The broker fixture is resolved by pytest through this import
from amqp_fixtures import rabbitmq_broker # noqa: F401 # pyright: ignore[reportUnusedImport]

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.client import ZatoClient
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.amqp.edit.runtime.' + CryptoManager.generate_hex_string(32) + '.'

_Outgoing_AMQP_Page_Url = '/zato/outgoing/amqp/?cluster=1'
_Channel_AMQP_Page_Url = '/zato/channel/amqp/?cluster=1'

# The JS namespaces the dialogs of both pages are opened through
_Outgoing_AMQP_Namespace = 'outgoing.amqp'
_Channel_AMQP_Namespace = 'channel.amqp'

# RabbitMQ's default account, always allowed to connect over localhost
_Broker_Username = 'guest'
_Broker_Password = 'guest'

# The service every test channel invokes
_Channel_Service = 'demo.ping'

# The service that publishes through an outgoing connection by name
_Publish_Service = 'zato.outgoing.amqp.publish'

# The create form fills this in for a channel, so it is how many consumers a channel runs
_Channel_Pool_Size = AMQP.DEFAULT.POOL_SIZE

# An edit or a deletion of a channel stops every consumer it has first, which takes a few seconds per consumer
_Channel_Change_Timeout = 90000

# An edit or a deletion of an outgoing connection only has producers to stop
_Outconn_Change_Timeout = 10000

# How long to wait for a queue to reach the expected consumer count or depth
_Queue_Wait_Timeout = 60

# For how long the consumer count is watched after it has settled
_Settle_Window = 3.0

_Poll_Interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

def _get_broker_address(broker_config:'anydict') -> 'str':
    """ Returns the address of the private broker in the format AMQP connection forms expect.
    """
    amqp_port = broker_config['amqp_port']
    out = f'amqp://127.0.0.1:{amqp_port}//'
    return out

# ################################################################################################################################

def _get_unreachable_address() -> 'str':
    """ Returns an address of a broker that does not exist - a free local port nothing listens on.
    """
    port = get_free_port()
    out = f'amqp://127.0.0.1:{port}//'
    return out

# ################################################################################################################################

def _get_consumer_count(amqp_url:'str', queue:'str') -> 'int':
    """ Returns how many consumers are attached to a queue, using a passive declare.
    """
    with Connection(amqp_url) as connection:
        channel = connection.channel()
        declaration = channel.queue_declare(queue=queue, passive=True)

        out = declaration.consumer_count
        return out

# ################################################################################################################################

def _wait_for_consumer_count(amqp_url:'str', queue:'str', expected:'int') -> 'None':
    """ Waits until exactly the expected number of consumers is attached to a queue.
    """
    deadline = time.monotonic() + _Queue_Wait_Timeout

    while time.monotonic() < deadline:
        consumer_count = _get_consumer_count(amqp_url, queue)

        if consumer_count == expected:
            return

        time.sleep(_Poll_Interval)

    consumer_count = _get_consumer_count(amqp_url, queue)
    raise Exception(
        f'Queue `{queue}` has {consumer_count} consumers, expected {expected} within {_Queue_Wait_Timeout}s')

# ################################################################################################################################

def _assert_consumer_count_holds(amqp_url:'str', queue:'str', expected:'int') -> 'None':
    """ Watches a queue for the settle window and asserts its consumer count never grows past what is expected.
    """
    deadline = time.monotonic() + _Settle_Window

    while time.monotonic() < deadline:
        consumer_count = _get_consumer_count(amqp_url, queue)
        assert consumer_count <= expected, \
            f'Queue `{queue}` has {consumer_count} consumers, expected at most {expected}'

        time.sleep(_Poll_Interval)

# ################################################################################################################################

def _wait_for_empty_queue(amqp_url:'str', queue:'str') -> 'None':
    """ Waits until a queue has no messages left, which means its consumers took them.
    """
    deadline = time.monotonic() + _Queue_Wait_Timeout

    while time.monotonic() < deadline:
        depth = get_queue_depth(amqp_url, queue)

        if depth == 0:
            return

        time.sleep(_Poll_Interval)

    depth = get_queue_depth(amqp_url, queue)
    raise Exception(f'Queue `{queue}` still has {depth} messages after {_Queue_Wait_Timeout}s')

# ################################################################################################################################

def _open_edit_dialog(page:'Page', namespace:'str', item_id:'str') -> 'None':
    """ Opens the edit dialog of an item on either of the AMQP pages.
    """
    page.evaluate(f'$.fn.zato.{namespace}.edit("{item_id}")')
    _ = page.wait_for_selector('#edit-div', state='visible', timeout=5000)

# ################################################################################################################################

def _rename(
    page:'Page',
    base_url:'str',
    page_url:'str',
    namespace:'str',
    item_id:'str',
    new_name:'str',
    timeout:'int',
    ) -> 'None':
    """ Reloads a page, opens the edit dialog of an item, gives it a new name and saves the form.
    """
    navigate_to_page(page, base_url, page_url)
    _open_edit_dialog(page, namespace, item_id)

    page.fill('#id_edit-name', new_name)
    submit_edit_form(page, timeout)

# ################################################################################################################################

def _delete(
    page:'Page',
    base_url:'str',
    page_url:'str',
    namespace:'str',
    item_id:'str',
    name:'str',
    timeout:'int',
    ) -> 'None':
    """ Reloads a page, deletes an item through its confirmation popup and waits for its row to disappear.
    """
    navigate_to_page(page, base_url, page_url)

    page.evaluate(f'$.fn.zato.{namespace}.delete_("{item_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)

    page.click('#popup_ok')

    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
    _ = page.wait_for_selector(row_selector, state='detached', timeout=timeout)

    row = find_row_by_name(page, name)
    assert row is None, f'Expected no row for `{name}` after deletion'

# ################################################################################################################################

def _publish(client:'ZatoClient', conn_name:'str', exchange:'str', routing_key:'str', payload:'str') -> 'any_':
    """ Publishes a message through a named outgoing connection and returns the service response.
    """
    request = {
        'conn_name': conn_name,
        'exchange': exchange,
        'routing_key': routing_key,
        'request_data': payload,
    }

    out = client.invoke(_Publish_Service, request)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAMQPEditRuntime:
    """ Edits of AMQP channels and outgoing connections reach the runtime - a renamed object answers to its new name,
    a new address is what messages go to, and a deleted object leaves nothing running behind.
    """

# ################################################################################################################################

    def test_outgoing_amqp_rename(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ A renamed outgoing connection publishes under its new name and no longer under the old one,
        and its deletion afterwards leaves no error behind.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        client = get_server_client(zato_dashboard['server_dir'])

        amqp_url = rabbitmq_broker['amqp_url']
        exchange = rabbitmq_broker['exchange']
        routing_key = rabbitmq_broker['routing_key']
        queue = rabbitmq_broker['queue']
        address = _get_broker_address(rabbitmq_broker)

        old_name = _Test_Name_Prefix + 'outconn'
        new_name = old_name + '.renamed'

        # Create the connection against the fixture broker ..
        item_id = create_outgoing_amqp(page, base_url, old_name, address, _Broker_Username, _Broker_Password)

        # .. rename it ..
        _rename(
            page, base_url, _Outgoing_AMQP_Page_Url, _Outgoing_AMQP_Namespace, item_id, new_name,
            _Outconn_Change_Timeout)

        # .. drain anything left on the fixture queue ..
        _ = drain_queue(amqp_url, queue, timeout=1)

        # .. a publish through the new name lands on the queue ..
        payload = 'rename-payload-' + CryptoManager.generate_hex_string()
        response = _publish(client, new_name, exchange, routing_key, payload)
        assert response.ok, f'Publish through `{new_name}` failed -> {response.details}'

        messages = drain_queue(amqp_url, queue)
        assert messages == [payload], f'Expected exactly `{payload}` on the queue, got: {messages}'

        # .. a publish through the old name is refused ..
        response = _publish(client, old_name, exchange, routing_key, payload)
        assert not response.ok, f'Publish through the old name `{old_name}` should have failed -> {response.data}'

        # .. and the renamed connection can be deleted.
        _delete(
            page, base_url, _Outgoing_AMQP_Page_Url, _Outgoing_AMQP_Namespace, item_id, new_name,
            _Outconn_Change_Timeout)

# ################################################################################################################################

    def test_channel_amqp_rename(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ A renamed channel consumes under its new name with the same number of consumers as before,
        the consumers of the old name are gone, and its deletion afterwards stops them all.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        amqp_url = rabbitmq_broker['amqp_url']
        exchange = rabbitmq_broker['exchange']
        routing_key = rabbitmq_broker['routing_key']
        queue = rabbitmq_broker['queue']
        address = _get_broker_address(rabbitmq_broker)

        old_name = _Test_Name_Prefix + 'channel'
        new_name = old_name + '.renamed'

        # Create the channel on the fixture queue ..
        item_id = create_amqp_channel(
            page, base_url, old_name, address, _Broker_Username, _Broker_Password, queue, _Channel_Service)

        # .. its whole pool of consumers attaches to the queue ..
        _wait_for_consumer_count(amqp_url, queue, _Channel_Pool_Size)

        # .. rename it ..
        _rename(
            page, base_url, _Channel_AMQP_Page_Url, _Channel_AMQP_Namespace, item_id, new_name, _Channel_Change_Timeout)

        # .. the pool attaches again under the new name and never doubles up ..
        _wait_for_consumer_count(amqp_url, queue, _Channel_Pool_Size)
        _assert_consumer_count_holds(amqp_url, queue, _Channel_Pool_Size)

        # .. the renamed channel takes messages off the queue ..
        payload = 'rename-payload-' + CryptoManager.generate_hex_string()
        publish_to_exchange(amqp_url, exchange, routing_key, payload)
        _wait_for_empty_queue(amqp_url, queue)

        # .. and its deletion detaches every consumer.
        _delete(
            page, base_url, _Channel_AMQP_Page_Url, _Channel_AMQP_Namespace, item_id, new_name, _Channel_Change_Timeout)
        _wait_for_consumer_count(amqp_url, queue, 0)

# ################################################################################################################################

    def test_outgoing_amqp_address_edit(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ An outgoing connection pointed at a broker that does not exist cannot publish,
        and it publishes as soon as its address is edited to point at the fixture broker.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        client = get_server_client(zato_dashboard['server_dir'])

        amqp_url = rabbitmq_broker['amqp_url']
        exchange = rabbitmq_broker['exchange']
        routing_key = rabbitmq_broker['routing_key']
        queue = rabbitmq_broker['queue']
        address = _get_broker_address(rabbitmq_broker)

        name = _Test_Name_Prefix + 'outconn.address'

        # Create the connection against a broker that does not exist ..
        unreachable_address = _get_unreachable_address()
        item_id = create_outgoing_amqp(page, base_url, name, unreachable_address, _Broker_Username, _Broker_Password)

        # .. a publish through it fails ..
        payload = 'address-payload-' + CryptoManager.generate_hex_string()
        response = _publish(client, name, exchange, routing_key, payload)
        assert not response.ok, \
            f'Publish through `{name}` should have failed with no broker behind it -> {response.data}'

        # .. edit only the address so it points at the fixture broker ..
        navigate_to_page(page, base_url, _Outgoing_AMQP_Page_Url)
        _open_edit_dialog(page, _Outgoing_AMQP_Namespace, item_id)

        page.fill('#id_edit-address', address)
        submit_edit_form(page, _Outconn_Change_Timeout)

        # .. drain anything left on the fixture queue ..
        _ = drain_queue(amqp_url, queue, timeout=1)

        # .. and the same publish now lands on the queue.
        response = _publish(client, name, exchange, routing_key, payload)
        assert response.ok, f'Publish through `{name}` failed after the address edit -> {response.details}'

        messages = drain_queue(amqp_url, queue)
        assert messages == [payload], f'Expected exactly `{payload}` on the queue, got: {messages}'

# ################################################################################################################################
# ################################################################################################################################
