# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import socket
import time
from base64 import b64encode
from urllib.request import Request, urlopen

# Zato
from zato.common.hl7.mllp.codec import FrameDecoder, frame_encode

# ################################################################################################################################
# ################################################################################################################################

_start_sequence   = b'\x0b'
_end_sequence     = b'\x1c\x0d'
_socket_timeout   = 5.0
_recv_buffer_size = 4096
_max_message_size = 2_000_000

_connection_type_channel = 'channel-hl7-mllp'
_generic_service_name    = 'zato.generic.connection'
_http_soap_service_name  = 'zato.http-soap'

_listener_bind_wait_seconds = 3
_rest_channel_settle_seconds = 2

# ################################################################################################################################
# ################################################################################################################################

def _build_adt_a01(control_id:'str') -> 'bytes':
    """ Builds a standard ADT^A01 message as UTF-8 bytes.
    """
    message = (
        f'MSH|^~\\&|TestSend|TestFac|ZatoRecv|ZatoFac|20260507120000||ADT^A01|{control_id}|P|2.5\r'
        f'PID|||12345^^^MRN||Doe^John||19800101|M\r'
        f'PV1||I|ICU^Room1'
    )

    out = message.encode('utf-8')
    return out

# ################################################################################################################################
# ################################################################################################################################

def _send_mllp(host:'str', port:'int', payload_bytes:'bytes') -> 'bytes':
    """ Opens a raw TCP socket, sends an MLLP-framed message, and reads the ACK response.
    """

    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw_socket.settimeout(_socket_timeout)
    raw_socket.connect((host, port))

    try:

        framed_message = frame_encode(payload_bytes, _start_sequence, _end_sequence)
        raw_socket.sendall(framed_message)

        decoder = FrameDecoder(_start_sequence, _end_sequence, _max_message_size)

        while True:
            chunk = raw_socket.recv(_recv_buffer_size)

            if not chunk:
                raise RuntimeError('Connection closed before receiving a complete ACK')

            decoder.feed(chunk)
            message = decoder.next_message()

            if message is not None:
                out = message
                break

        return out

    finally:
        raw_socket.close()

# ################################################################################################################################
# ################################################################################################################################

def _send_rest(host:'str', port:'int', url_path:'str', payload_bytes:'bytes', password:'str') -> 'bytes':
    """ Sends an HL7 message via HTTP POST to the REST bridge URL path.
    """

    url = f'http://{host}:{port}{url_path}'
    auth = b64encode(f'admin.invoke:{password}'.encode()).decode()

    req = Request(url, data=payload_bytes, method='POST')
    req.add_header('Authorization', f'Basic {auth}')
    req.add_header('Content-Type', 'application/hl7-v2')

    with urlopen(req, timeout=_socket_timeout) as resp:
        out = resp.read()

    return out

# ################################################################################################################################
# ################################################################################################################################

def _port_is_open(host:'str', port:'int') -> 'bool':
    """ Returns True if the port accepts TCP connections.
    """
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.settimeout(2.0)

    try:
        test_socket.connect((host, port))
        test_socket.close()
        return True
    except (ConnectionRefusedError, OSError):
        return False

# ################################################################################################################################
# ################################################################################################################################

def _find_rest_channels_by_name(zato_client:'object', name:'str') -> 'list[dict]':
    """ Returns all http-soap channels matching the given exact name.
    """

    data, _ = zato_client.get_list( # type: ignore[union-attr]
        f'{_http_soap_service_name}.get-list',
        cluster_id=1,
        connection='channel',
        transport='plain_http',
    )

    out = [item for item in data if item['name'] == name]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMLLPRestBridge:
    """ Wire-level tests for the MLLP REST bridge running inside a live Zato server.

    The web-admin view creates the backing REST channel during form submission.
    In live API tests we replicate that flow:
    1. Create the REST channel via zato.http-soap.create
    2. Create the MLLP channel with rest_channel_id pointing to it
    3. Verify both paths work
    4. Delete and verify cleanup
    """

    mllp_channel_id:'int' = 0
    rest_channel_id:'int' = 0
    rest_url_path:'str' = '/test/hl7/mllp-rest-bridge'
    rest_channel_name:'str' = 'hl7.rest.test-mllp-rest-bridge'

# ################################################################################################################################

    def test_01_create_backing_rest_channel(self, zato_client:'object') -> 'None':
        """ Creates the backing REST channel that the MLLP channel will reference.
        """

        response = zato_client.create( # type: ignore[union-attr]
            f'{_http_soap_service_name}.create',
            cluster_id=1,
            name=self.__class__.rest_channel_name,
            is_active=True,
            is_internal=False,
            url_path=self.__class__.rest_url_path,
            connection='channel',
            transport='plain_http',
            service='test.hl7.mllp.echo',
            data_format='hl7-v2',
            match_slash=False,
            merge_url_params_req=True,
        )

        assert 'id' in response
        self.__class__.rest_channel_id = response['id']

        time.sleep(_rest_channel_settle_seconds)

# ################################################################################################################################

    def test_02_create_mllp_channel_with_rest(self, zato_client:'object', channel_port:'int') -> 'None':
        """ Creates an MLLP channel with use_rest=True and rest_only=False,
        referencing the backing REST channel.
        """

        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name='test-mllp-rest-bridge',
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.echo',
            address=f'127.0.0.1:{channel_port}',
            pool_size=1,
            use_rest=True,
            rest_only=False,
            rest_channel_id=self.__class__.rest_channel_id,
        )

        assert 'id' in response
        assert response['name'] == 'test-mllp-rest-bridge'

        self.__class__.mllp_channel_id = response['id']

        time.sleep(_listener_bind_wait_seconds)

# ################################################################################################################################

    def test_03_mllp_port_is_open(self, channel_port:'int') -> 'None':
        """ Verifies the MLLP listener is active since rest_only=False.
        """
        assert _port_is_open('127.0.0.1', channel_port)

# ################################################################################################################################

    def test_04_send_via_mllp(self, channel_port:'int') -> 'None':
        """ Sends a message via MLLP and verifies the ACK.
        """
        message_bytes = _build_adt_a01('REST-BRIDGE-MLLP-001')
        ack_bytes = _send_mllp('127.0.0.1', channel_port, message_bytes)

        ack_text = ack_bytes.decode('utf-8')
        assert 'MSA|AA|REST-BRIDGE-MLLP-001' in ack_text

# ################################################################################################################################

    def test_05_send_via_rest(self, zato_server:'dict') -> 'None':
        """ Sends a message via REST and verifies no error is returned.
        """

        host = str(zato_server['host'])
        port = int(zato_server['port']) # type: ignore[arg-type]
        password = str(zato_server['password'])

        message_bytes = _build_adt_a01('REST-BRIDGE-REST-001')

        _send_rest(host, port, self.__class__.rest_url_path, message_bytes, password)

        time.sleep(0.5)

# ################################################################################################################################

    def test_06_both_messages_received(self, zato_client:'object') -> 'None':
        """ Verifies the echo service captured messages from both MLLP and REST paths.
        """

        response = zato_client.invoke('test.hl7.mllp.inspect') # type: ignore[union-attr]

        if isinstance(response, str):
            data = json.loads(response)
        else:
            data = response

        messages = data['messages']

        mllp_found = False
        rest_found = False

        for message in messages:
            if 'REST-BRIDGE-MLLP-001' in message:
                mllp_found = True
            if 'REST-BRIDGE-REST-001' in message:
                rest_found = True

        assert mllp_found
        assert rest_found

# ################################################################################################################################

    def test_07_delete_mllp_channel_cleans_up_rest(self, zato_client:'object', channel_port:'int') -> 'None':
        """ Deletes the MLLP channel. Since it has rest_channel_id set,
        the wrapper's _delete should also delete the backing REST channel.
        """

        zato_client.delete( # type: ignore[union-attr]
            f'{_generic_service_name}.delete',
            id=self.__class__.mllp_channel_id,
        )

        time.sleep(_rest_channel_settle_seconds)

        # .. verify the MLLP port is closed ..
        assert not _port_is_open('127.0.0.1', channel_port)

        # .. verify the backing REST channel was removed by the wrapper ..
        matching = _find_rest_channels_by_name(zato_client, self.__class__.rest_channel_name)
        assert len(matching) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestMLLPRestOnlyMode:
    """ Tests for rest_only=True mode where the MLLP listener is not started.
    """

    mllp_channel_id:'int' = 0
    rest_channel_id:'int' = 0
    rest_url_path:'str' = '/test/hl7/mllp-rest-only'
    rest_channel_name:'str' = 'hl7.rest.test-mllp-rest-only'

# ################################################################################################################################

    def test_01_create_backing_rest_channel(self, zato_client:'object') -> 'None':
        """ Creates the backing REST channel for the rest-only MLLP channel.
        """

        response = zato_client.create( # type: ignore[union-attr]
            f'{_http_soap_service_name}.create',
            cluster_id=1,
            name=self.__class__.rest_channel_name,
            is_active=True,
            is_internal=False,
            url_path=self.__class__.rest_url_path,
            connection='channel',
            transport='plain_http',
            service='test.hl7.mllp.echo',
            data_format='hl7-v2',
            match_slash=False,
            merge_url_params_req=True,
        )

        assert 'id' in response
        self.__class__.rest_channel_id = response['id']

        time.sleep(_rest_channel_settle_seconds)

# ################################################################################################################################

    def test_02_create_mllp_channel_rest_only(self, zato_client:'object', forward_channel_port:'int') -> 'None':
        """ Creates an MLLP channel with rest_only=True. The MLLP listener should not start.
        """

        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name='test-mllp-rest-only',
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.echo',
            address=f'127.0.0.1:{forward_channel_port}',
            pool_size=1,
            use_rest=True,
            rest_only=True,
            rest_channel_id=self.__class__.rest_channel_id,
        )

        assert 'id' in response
        self.__class__.mllp_channel_id = response['id']

        time.sleep(_listener_bind_wait_seconds)

# ################################################################################################################################

    def test_03_mllp_port_is_closed(self, forward_channel_port:'int') -> 'None':
        """ Verifies the MLLP port is NOT listening since rest_only=True.
        """
        assert not _port_is_open('127.0.0.1', forward_channel_port)

# ################################################################################################################################

    def test_04_rest_still_works(self, zato_server:'dict') -> 'None':
        """ Sends a message via REST and verifies it is accepted.
        """

        host = str(zato_server['host'])
        port = int(zato_server['port']) # type: ignore[arg-type]
        password = str(zato_server['password'])

        message_bytes = _build_adt_a01('REST-ONLY-001')

        _send_rest(host, port, self.__class__.rest_url_path, message_bytes, password)

        time.sleep(0.5)

# ################################################################################################################################

    def test_05_message_received_via_rest(self, zato_client:'object') -> 'None':
        """ Verifies the echo service received the REST-delivered message.
        """

        response = zato_client.invoke('test.hl7.mllp.inspect') # type: ignore[union-attr]

        if isinstance(response, str):
            data = json.loads(response)
        else:
            data = response

        messages = data['messages']

        found = False

        for message in messages:
            if 'REST-ONLY-001' in message:
                found = True
                break

        assert found

# ################################################################################################################################

    def test_06_cleanup(self, zato_client:'object') -> 'None':
        """ Deletes the MLLP channel and verifies the backing REST channel is cleaned up.
        """

        zato_client.delete( # type: ignore[union-attr]
            f'{_generic_service_name}.delete',
            id=self.__class__.mllp_channel_id,
        )

        time.sleep(_rest_channel_settle_seconds)

        matching = _find_rest_channels_by_name(zato_client, self.__class__.rest_channel_name)
        assert len(matching) == 0

# ################################################################################################################################
# ################################################################################################################################

def _find_mllp_channel_by_name(zato_client:'object', name:'str') -> 'dict':
    """ Returns the MLLP channel matching the given name from the get-list response.
    """

    data, _ = zato_client.get_list( # type: ignore[union-attr]
        f'{_generic_service_name}.get-list',
        cluster_id=1,
        type_=_connection_type_channel,
    )

    for item in data:
        if item['name'] == name:
            return item

    raise AssertionError(f'MLLP channel {name!r} not found in get-list response')

# ################################################################################################################################
# ################################################################################################################################

class TestMLLPRestBridgePersistence:
    """ Verifies that use_rest, rest_only, and rest_channel_id survive
    create-read-edit-read round-trips through the generic connection API
    on a live server.
    """

    mllp_channel_id:'int' = 0

# ################################################################################################################################

    def test_01_create_with_rest_fields(self, zato_client:'object', error_channel_port:'int') -> 'None':
        """ Creates an MLLP channel with REST bridge fields set.
        """

        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name='test-persist-bridge',
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.echo',
            address=f'127.0.0.1:{error_channel_port}',
            pool_size=1,
            use_rest=True,
            rest_only=False,
            rest_channel_id=777,
        )

        assert 'id' in response
        self.__class__.mllp_channel_id = response['id']

        time.sleep(_listener_bind_wait_seconds)

# ################################################################################################################################

    def test_02_read_back_after_create(self, zato_client:'object') -> 'None':
        """ Reads the channel back and verifies REST bridge fields persisted.
        """

        item = _find_mllp_channel_by_name(zato_client, 'test-persist-bridge')

        assert item['use_rest'] is True
        assert item['rest_only'] is False
        assert int(item['rest_channel_id']) == 777

# ################################################################################################################################

    def test_03_edit_to_rest_only(self, zato_client:'object', error_channel_port:'int') -> 'None':
        """ Edits the channel to set rest_only=True.
        """

        zato_client.edit( # type: ignore[union-attr]
            f'{_generic_service_name}.edit',
            id=self.__class__.mllp_channel_id,
            cluster_id=1,
            name='test-persist-bridge',
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.echo',
            address=f'127.0.0.1:{error_channel_port}',
            pool_size=1,
            use_rest=True,
            rest_only=True,
            rest_channel_id=777,
        )

        time.sleep(_rest_channel_settle_seconds)

# ################################################################################################################################

    def test_04_read_back_rest_only(self, zato_client:'object') -> 'None':
        """ Verifies rest_only=True persisted after edit.
        """

        item = _find_mllp_channel_by_name(zato_client, 'test-persist-bridge')

        assert item['use_rest'] is True
        assert item['rest_only'] is True
        assert int(item['rest_channel_id']) == 777

# ################################################################################################################################

    def test_05_edit_toggle_off_rest(self, zato_client:'object', error_channel_port:'int') -> 'None':
        """ Edits the channel to set use_rest=False and clears rest_channel_id.
        """

        zato_client.edit( # type: ignore[union-attr]
            f'{_generic_service_name}.edit',
            id=self.__class__.mllp_channel_id,
            cluster_id=1,
            name='test-persist-bridge',
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.echo',
            address=f'127.0.0.1:{error_channel_port}',
            pool_size=1,
            use_rest=False,
            rest_only=False,
            rest_channel_id=0,
        )

        time.sleep(_rest_channel_settle_seconds)

# ################################################################################################################################

    def test_06_read_back_rest_off(self, zato_client:'object') -> 'None':
        """ Verifies use_rest=False and rest_channel_id=0 persisted.
        """

        item = _find_mllp_channel_by_name(zato_client, 'test-persist-bridge')

        assert item['use_rest'] is False
        assert item['rest_only'] is False
        assert int(item.get('rest_channel_id') or 0) == 0

# ################################################################################################################################

    def test_07_cleanup(self, zato_client:'object') -> 'None':
        """ Deletes the test channel.
        """

        zato_client.delete( # type: ignore[union-attr]
            f'{_generic_service_name}.delete',
            id=self.__class__.mllp_channel_id,
        )

        time.sleep(_rest_channel_settle_seconds)

        data, _ = zato_client.get_list( # type: ignore[union-attr]
            f'{_generic_service_name}.get-list',
            cluster_id=1,
            type_=_connection_type_channel,
        )

        names = [item['name'] for item in data]
        assert 'test-persist-bridge' not in names

# ################################################################################################################################
# ################################################################################################################################
