# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import sys
import tempfile
import time
from http.client import OK
from shutil import rmtree
from subprocess import DEVNULL, Popen

# pytest
import pytest

# Redis
from redis import Redis
from redis.exceptions import RedisError

# Zato
from zato.common.ext.configobj_ import ConfigObj
from zato.common.test import rand_string
from zato.common.test.conftest_base_pubsub import find_free_port
from zato.common.test.playwright_pubsub import create_amqp_topic, create_basic_auth, create_outgoing_amqp, \
    create_outgoing_rest_with_address, create_permission, create_push_rest_subscription, create_topic, get_item_id, \
    navigate_to_page, open_publish_overlay, publish_via_overlay
from zato.common.test.rabbitmq_ import drain_queue
from zato.common.test.receiver import WebhookReceiver
from zato.common.util.api import new_cid

# The certificate generator lives in the zato-common test lib, shared with the redis_ suite
_zato_common_lib_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib'))
if _zato_common_lib_dir not in sys.path:
    sys.path.insert(0, _zato_common_lib_dir)

from live_sql.certificates import generate_certificates

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from config_db_screen import expect_redis_test_error, expect_redis_test_ok, open_redis_screen, run_redis_test, \
    save_redis_connection
from rest_channel import create_channel, invoke_until_status
from server_restart import restart_server

# The broker fixture is resolved by pytest through this import
from amqp_fixtures import rabbitmq_broker # noqa: F401

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.playwright')

_Test_Name_Prefix = 'test.config.db.redis.live.' + rand_string() + '.'

_Echo_Service = 'demo.echo'

# The prefix the CacheAPI puts in front of every key it stores in Redis
_Cache_Key_Prefix = 'zato:cache:'

# The fixture service deployed at server boot from fixtures/services
_Cache_Check_Service = 'test.config-db.cache-check'

# The default Redis server of the quickstart environment - the plain localhost one
_Default_Redis_Port = 6379

# RabbitMQ's default account, always allowed to connect over localhost
_Broker_Username = 'guest'
_Broker_Password = 'guest'

# How long to wait for the TLS Redis server to become ready, in seconds
_TLS_Ready_Timeout = 30

# How long each TLS readiness check may take before it is abandoned, in seconds
_TLS_Ready_Socket_Timeout = 2

# The fields of the Redis form the tests capture and restore
_Form_Fields = ('display_name', 'description', 'host', 'port', 'db', 'username')

# State shared between the sequential tests of this module
_shared_state = {} # type: dict

# ################################################################################################################################
# ################################################################################################################################

def _get_redis_key(port:'int', key:'str', **connect_args:'any_') -> 'any_':
    """ Reads one cache key straight from a Redis server, bypassing the Zato server
    entirely, which proves where the cache write physically landed.
    """
    conn = Redis(host='127.0.0.1', port=port, decode_responses=True, **connect_args)

    out = conn.get(_Cache_Key_Prefix + key)
    conn.close()

    return out

# ################################################################################################################################

def _check_cache(api_client:'any_', suffix:'str') -> 'tuple':
    """ Writes a key through the server's live cache connection via the fixture service
    and returns the key along with the value the service read back.
    """
    key = 'test.config-db.cache.' + suffix + '.' + new_cid()
    value = 'cache-value-' + new_cid()

    response = api_client.invoke(_Cache_Check_Service, {'key': key, 'value': value})

    assert response['read_value'] == value, f'Expected `{value}` read back, got: {response}'

    out = key, value
    return out

# ################################################################################################################################

def _publish_to_amqp_topic(page:'Page', base_url:'str', rabbitmq_broker:'anydict', label:'str') -> 'None': # noqa: F811
    """ Publishes through the overlay of the module's AMQP-backed topic and asserts
    the message flowed through AMQP to the broker's queue.
    """
    topic_name = _shared_state['amqp_topic_name']

    # The list is paginated so filter it by the topic's name first ..
    navigate_to_page(page, base_url, f'/zato/pubsub/topic/?cluster=1&query={topic_name}')
    item_id = get_item_id(page, topic_name)

    # .. drain anything left on the queue ..
    _ = drain_queue(rabbitmq_broker['amqp_url'], rabbitmq_broker['queue'], timeout=1)

    # .. publish through the overlay ..
    payload = f'amqp-roundtrip-{label}-' + new_cid()

    open_publish_overlay(page, item_id)
    publish_via_overlay(page, payload)

    # .. and the message landed on the RabbitMQ queue, not anywhere near Redis.
    messages = drain_queue(rabbitmq_broker['amqp_url'], rabbitmq_broker['queue'])

    assert len(messages) == 1, f'Expected exactly one message, got: {messages}'
    assert messages[0] == payload, f'Expected `{payload}`, got `{messages[0]}`'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def webhook_receiver() -> 'any_':
    """ A module-scoped local HTTP receiver for push subscription deliveries.
    """
    receiver_port = find_free_port()
    output_directory = tempfile.mkdtemp(prefix='zato_test_config_db_redis_')

    receiver = WebhookReceiver(receiver_port, output_directory)
    receiver.start()

    yield receiver

    receiver.stop()

# ################################################################################################################################

def _wait_until_tls_ready(port:'int', ca_cert:'str', process:'Popen') -> 'None':
    """ Polls the TLS server until it accepts encrypted connections, up to a timeout.
    """
    deadline = time.monotonic() + _TLS_Ready_Timeout

    while time.monotonic() < deadline:

        # There is no point in waiting further if the server already exited
        if process.poll() is not None:
            raise Exception(f'Redis TLS server exited with code {process.returncode}')

        conn = Redis(
            host='localhost',
            port=port,
            ssl=True,
            ssl_ca_certs=ca_cert,
            socket_connect_timeout=_TLS_Ready_Socket_Timeout,
            socket_timeout=_TLS_Ready_Socket_Timeout,
        )
        try:
            # A successful ping means the server is up and TLS works ..
            _ = conn.ping()
            conn.close()
            return
        except RedisError:
            # .. otherwise, the server is still starting up.
            conn.close()
            time.sleep(0.1)

    raise Exception(f'Redis TLS server did not become ready within {_TLS_Ready_Timeout}s')

# ################################################################################################################################

@pytest.fixture(scope='module')
def redis_tls_server() -> 'any_':
    """ A local redis-server process that accepts TLS connections only,
    on a dynamic port with throwaway certificates.
    """
    certificates_dir = tempfile.mkdtemp(prefix='zato-config-db-redis-certificates-')
    certificate_paths = generate_certificates(certificates_dir)

    tls_port = find_free_port()

    command = [
        'redis-server',
        '--port', '0',
        '--tls-port', str(tls_port),
        '--tls-cert-file', certificate_paths.server_cert,
        '--tls-key-file', certificate_paths.server_key,
        '--tls-ca-cert-file', certificate_paths.ca_cert,
        '--tls-auth-clients', 'no',
        '--save', '',
        '--appendonly', 'no',
    ]

    process = Popen(command, stdout=DEVNULL, stderr=DEVNULL)

    _wait_until_tls_ready(tls_port, certificate_paths.ca_cert, process)

    yield {
        'port': tls_port,
        'ca_cert': certificate_paths.ca_cert,
    }

    process.terminate()
    _ = process.wait()

    rmtree(certificates_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################

class TestConfigDBRedisLive:
    """ The Redis connection is reconfigured on the fly through the Config DB Redis screen -
    self.cache moves to the saved server immediately, the configuration is persisted
    in server.conf and survives a restart, TLS works end to end, and neither Redis-backed
    nor AMQP-backed pub/sub topics are disturbed.
    """

    # The dashboard returns HTTP 500 for a failed connection test on purpose
    @pytest.mark.expect_log_errors('Internal Server Error')
    def test_01_failed_test_shows_error(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A connection test against a port nothing listens on renders the error row.
        Nothing is saved so the live configuration stays as it was.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Remember the original form values so the last test can restore them ..
        open_redis_screen(page, base_url)

        original_values = {} # type: anydict

        for field in _Form_Fields:
            original_values[field] = page.input_value(f'#id_{field}')

        _shared_state['original_values'] = original_values

        # .. a port with nothing behind it ..
        unreachable_port = find_free_port()

        # .. the test must fail and say so on the screen.
        run_redis_test(page, base_url, {'host': '127.0.0.1', 'port': unreachable_port})
        expect_redis_test_error(page)

# ################################################################################################################################

    def test_02_amqp_topic_roundtrip_before_save(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ An AMQP-backed topic routes through an outgoing AMQP connection,
        not through the [redis] section - this is the baseline roundtrip
        the later tests repeat after the Redis save and after the restart.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        amqp_port = rabbitmq_broker['amqp_port']
        address = f'amqp://127.0.0.1:{amqp_port}//'

        # The outgoing connection the topic publishes through ..
        outconn_name = _Test_Name_Prefix + 'amqp.outconn'
        _ = create_outgoing_amqp(page, base_url, outconn_name, address, _Broker_Username, _Broker_Password)

        # .. the AMQP-backed topic itself, publishing to the fixture queue's binding ..
        topic_name = _Test_Name_Prefix + 'amqp.topic'
        _ = create_amqp_topic(
            page, base_url, topic_name, outconn_name, rabbitmq_broker['exchange'], rabbitmq_broker['routing_key'], '')

        _shared_state['amqp_topic_name'] = topic_name

        # .. and the baseline roundtrip flows through AMQP.
        _publish_to_amqp_topic(page, base_url, rabbitmq_broker, 'before-save')

# ################################################################################################################################

    def test_03_save_moves_cache(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'any_',
        ) -> 'None':
        """ Saving the session's dedicated Redis through the screen makes self.cache
        write to that server immediately - the key is physically there and it is
        not on the default localhost server.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        session_redis_port = zato_dashboard['queue_bridge_redis_port']

        # Save the session's Redis as the server's connection ..
        save_redis_connection(page, base_url, {
            'display_name': _Test_Name_Prefix + 'connection',
            'description': 'The session Redis, saved by the live test',
            'host': '127.0.0.1',
            'port': session_redis_port,
            'db': 0,
            'ssl': False,
            'ssl_verify': True,
        })

        # .. write through self.cache via the fixture service ..
        key, value = _check_cache(api_client, 'save')

        # .. the key is physically on the saved server ..
        stored = _get_redis_key(session_redis_port, key)
        assert stored is not None, f'Expected `{key}` on the saved Redis, got nothing'
        assert json.loads(stored) == value, f'Expected `{value}` on the saved Redis, got: {stored}'

        # .. and it is not on the default localhost server the cache used before.
        stored_on_default = _get_redis_key(_Default_Redis_Port, key)
        assert stored_on_default is None, f'Expected `{key}` to be absent from the default Redis, got: {stored_on_default}'

# ################################################################################################################################

    def test_04_server_conf_persisted(self, zato_dashboard:'anydict') -> 'None':
        """ The save landed in the [redis] section of server.conf on disk,
        which is what a restart rebuilds the connections from.
        """
        server_dir = zato_dashboard['server_dir']
        session_redis_port = zato_dashboard['queue_bridge_redis_port']

        # The vendored ConfigObj returns typed values - ints and booleans, not strings
        server_conf_path = os.path.join(server_dir, 'config', 'repo', 'server.conf')
        server_conf = ConfigObj(server_conf_path)

        redis_section = server_conf['redis']

        assert redis_section['host'] == '127.0.0.1', f'Expected host 127.0.0.1 on disk, got: {redis_section["host"]}'
        assert redis_section['port'] == session_redis_port, \
            f'Expected port {session_redis_port} on disk, got: {redis_section["port"]}'
        assert redis_section['ssl'] is False, f'Expected ssl False on disk, got: {redis_section["ssl"]}'

# ################################################################################################################################

    def test_05_rest_and_redis_pubsub_stay_healthy(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        webhook_receiver:'WebhookReceiver',
        ) -> 'None':
        """ After the save, a REST channel serves traffic and a Redis-backed topic
        delivers a publish to its push subscriber - the pub/sub backend keeps
        its startup connection and stays healthy.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # A REST channel answers ..
        channel_name = _Test_Name_Prefix + 'channel'
        url_path = '/test/config-db/redis/live/' + rand_string()

        _ = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
            'data_format': 'json',
        })

        response = invoke_until_status(server_port, url_path, OK, data='{"health":"check"}')
        assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

        # .. and a Redis-backed topic delivers to its push subscriber ..
        sec_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'pubsub')

        topic = create_topic(page, base_url, _Test_Name_Prefix, 'redis-topic')
        topic_name = topic['name']

        _ = create_permission(page, base_url, sec_info['name'], 'subscriber', 'sub', topic_name)

        rest_name = _Test_Name_Prefix + 'push.rest'
        create_outgoing_rest_with_address(page, base_url, rest_name, f'http://127.0.0.1:{webhook_receiver.port}', '/push')
        create_push_rest_subscription(page, base_url, sec_info['name'], topic_name, rest_name)

        # .. publish through the overlay ..
        marker = 'redis-pubsub-health-' + new_cid()

        navigate_to_page(page, base_url, f'/zato/pubsub/topic/?cluster=1&query={topic_name}')
        item_id = get_item_id(page, topic_name)

        open_publish_overlay(page, item_id)
        publish_via_overlay(page, f'{{"value": "{marker}"}}')

        # .. and the message arrived at the receiver.
        messages = webhook_receiver.wait_for_delivery(1)

        assert len(messages) == 1, f'Expected exactly one delivery, got: {messages}'
        assert marker in json.dumps(messages), f'Expected `{marker}` in the delivery, got: {messages}'

# ################################################################################################################################

    def test_06_amqp_topic_unaffected_by_save(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ The same AMQP-backed topic still flows through AMQP after the Redis save -
        the save did not reach into the AMQP path.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _publish_to_amqp_topic(page, base_url, rabbitmq_broker, 'after-save')

# ################################################################################################################################

    def test_07_restart_cache_still_on_saved_redis(
        self,
        zato_dashboard:'anydict',
        api_client:'any_',
        ) -> 'None':
        """ After a full restart the cache is rebuilt from server.conf and still
        writes to the saved Redis - the persistence works end to end.
        """
        session_redis_port = zato_dashboard['queue_bridge_redis_port']

        restart_server(zato_dashboard)

        key, value = _check_cache(api_client, 'restart')

        stored = _get_redis_key(session_redis_port, key)
        assert stored is not None, f'Expected `{key}` on the saved Redis after the restart, got nothing'
        assert json.loads(stored) == value, f'Expected `{value}` on the saved Redis after the restart, got: {stored}'

# ################################################################################################################################

    def test_08_amqp_topic_unaffected_by_restart(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        rabbitmq_broker:'anydict', # noqa: F811
        ) -> 'None':
        """ The AMQP-backed topic still flows through AMQP after the restart too,
        with its registry rebuilt from the database.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _publish_to_amqp_topic(page, base_url, rabbitmq_broker, 'after-restart')

# ################################################################################################################################

    def test_09_tls_via_screen(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'any_',
        redis_tls_server:'anydict',
        ) -> 'None':
        """ A TLS-only Redis server is tested and saved through the screen -
        self.cache works over TLS and the key is on the TLS server.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        tls_port = redis_tls_server['port']
        ca_cert = redis_tls_server['ca_cert']

        tls_values = {
            'host': 'localhost',
            'port': tls_port,
            'db': 0,
            'ssl': True,
            'ssl_ca_file': ca_cert,
            'ssl_verify': True,
        }

        # The connection test passes over TLS ..
        run_redis_test(page, base_url, tls_values)
        expect_redis_test_ok(page)

        # .. save it as the server's connection ..
        save_redis_connection(page, base_url, tls_values)

        # .. self.cache now writes over TLS ..
        key, value = _check_cache(api_client, 'tls')

        # .. and the key is physically on the TLS server.
        stored = _get_redis_key(tls_port, key, ssl=True, ssl_ca_certs=ca_cert)
        assert stored is not None, f'Expected `{key}` on the TLS Redis, got nothing'
        assert json.loads(stored) == value, f'Expected `{value}` on the TLS Redis, got: {stored}'

# ################################################################################################################################

    def test_10_restore_original_values(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'any_',
        ) -> 'None':
        """ Restores the original connection through the screen so later tests
        in the session see the environment they expect.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        original_values = dict(_shared_state['original_values'])

        # The original connection has no SSL and no certificate files
        original_values['ssl'] = False
        original_values['ssl_verify'] = True
        original_values['ssl_ca_file'] = ''
        original_values['ssl_cert_file'] = ''
        original_values['ssl_key_file'] = ''

        save_redis_connection(page, base_url, original_values)

        # The cache works against the restored connection too
        _ = _check_cache(api_client, 'restore')

# ################################################################################################################################
# ################################################################################################################################
