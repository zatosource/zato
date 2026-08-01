# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile

# pytest
import pytest

# Zato - the suite's own parts
from _outconn_api import create_outconn, send_one, wait_until_ready
from _outconn_messages import build_adt_a01, get_msh_field, get_segment
from _outconn_proxy import is_haproxy_available, ProxyHandle
from _outconn_receivers import build_receiver, next_delivery, RawSocketReceiver, Receiver_Hapi, Receiver_Hl7apy

# Zato - the suite's own fixture helpers
from conftest import require_toolchain

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import OutconnEnvironment
    from zato.common.typing_ import any_

    any_ = any_
    OutconnEnvironment = OutconnEnvironment

# ################################################################################################################################
# ################################################################################################################################

# How long a send against a listener that is never going to answer waits before giving up, in
# milliseconds. Short, because the test is over the moment the send has given up.
_Rough_Ending_Recv_Timeout = 3000

# How many messages the pool-slot check sends after a connection has failed. One send failing tells
# a test nothing about whether the slot went back, and a run of them through a pool of one tells it
# everything - a leaked slot would leave the second send with nothing to take.
_Pool_Slot_Send_Count = 4

# How many connections a pool has for the test that a failure does not cost it one
_Small_Pool_Size = 2

# ################################################################################################################################
# ################################################################################################################################

class TestOutconnTLS:
    """ A connection over TLS, against a listener that terminates it. Verification is one-way where
    only the receiving end presents anything, and mutual where the sender presents an identity of
    its own, which is what a hospital's own network asks of anything connecting into it.
    """

# ################################################################################################################################

    def test_verified_tls_to_the_python_stack(self, outconn_environment:'OutconnEnvironment') -> 'None':
        """ A connection naming an authority verifies what the listener presents against it and
        sends over the connection that handshake produced.
        """
        client = outconn_environment.client
        certificates = outconn_environment.certificates

        receiver = build_receiver(
            Receiver_Hl7apy,
            cert_path=certificates.server_cert_path,
            key_path=certificates.server_key_path,
        )
        receiver.start()

        try:
            config = {'tls_ca_path': certificates.ca_cert_path}

            name = create_outconn(outconn_environment, 'tls-verified', receiver.address, **config)

            wait_until_ready(client, name)
            delivered_before = len(receiver.deliveries)

            result = send_one(client, name, build_adt_a01('TLS-0001'))

            assert result['is_sent'], result['error_text']
            assert result['is_accepted']

            arrived = next_delivery(receiver, delivered_before)
            assert get_msh_field(arrived, 10) == 'TLS-0001'

        finally:
            receiver.stop()

# ################################################################################################################################

    def test_mutual_tls_to_the_python_stack(self, outconn_environment:'OutconnEnvironment') -> 'None':
        """ A listener that verifies its senders takes a connection presenting a certificate the
        same authority issued, and the message crosses on it.
        """
        client = outconn_environment.client
        certificates = outconn_environment.certificates

        receiver = build_receiver(
            Receiver_Hl7apy,
            cert_path=certificates.server_cert_path,
            key_path=certificates.server_key_path,
            ca_path=certificates.ca_cert_path,
        )
        receiver.start()

        try:
            config = {
                'tls_ca_path': certificates.ca_cert_path,
                'tls_cert_path': certificates.client_cert_path,
                'tls_key_path': certificates.client_key_path,
            }

            name = create_outconn(outconn_environment, 'tls-mutual', receiver.address, **config)

            wait_until_ready(client, name)
            delivered_before = len(receiver.deliveries)

            result = send_one(client, name, build_adt_a01('TLS-0002'))

            assert result['is_sent'], result['error_text']
            assert result['is_accepted']

            arrived = next_delivery(receiver, delivered_before)
            assert get_msh_field(arrived, 10) == 'TLS-0002'

        finally:
            receiver.stop()

# ################################################################################################################################

    def test_a_connection_presenting_nothing_is_turned_away(self, outconn_environment:'OutconnEnvironment') -> 'None':
        """ The same listener refuses a connection that presents no identity, and it refuses it at
        the handshake, so nothing of the message reaches it.
        """
        client = outconn_environment.client
        certificates = outconn_environment.certificates

        receiver = build_receiver(
            Receiver_Hl7apy,
            cert_path=certificates.server_cert_path,
            key_path=certificates.server_key_path,
            ca_path=certificates.ca_cert_path,
        )
        receiver.start()

        try:

            # The authority is named, so what the listener presents is verified, but nothing of
            # this connection's own is, which is what the listener turns it away for
            config = {'tls_ca_path': certificates.ca_cert_path}

            name = create_outconn(outconn_environment, 'tls-unverified', receiver.address, **config)

            delivered_before = len(receiver.deliveries)

            result = send_one(client, name, build_adt_a01('TLS-0003'))

            assert not result['is_sent']
            assert len(receiver.deliveries) == delivered_before

        finally:
            receiver.stop()

# ################################################################################################################################

    def test_verified_tls_to_the_java_stack(self, outconn_environment:'OutconnEnvironment') -> 'None':
        """ The same one-way case against HAPI, which terminates TLS out of a key store rather than
        out of a pair of files - a difference that is entirely the listener's and none of the
        sender's, which is what this asserts.
        """
        require_toolchain(Receiver_Hapi)

        client = outconn_environment.client
        certificates = outconn_environment.certificates

        receiver = build_receiver(
            Receiver_Hapi,
            keystore_path=certificates.server_keystore_path,
            keystore_password=certificates.java_store_password,
        )
        receiver.start()

        try:
            config = {'tls_ca_path': certificates.ca_cert_path}

            name = create_outconn(outconn_environment, 'tls-java', receiver.address, **config)

            wait_until_ready(client, name)
            delivered_before = len(receiver.deliveries)

            result = send_one(client, name, build_adt_a01('TLS-0004'))

            assert result['is_sent'], result['error_text']
            assert result['is_accepted']

            arrived = next_delivery(receiver, delivered_before)
            assert get_msh_field(arrived, 10) == 'TLS-0004'

        finally:
            receiver.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestOutconnRoughEndings:
    """ A listener that takes a connection and then behaves badly. What matters is not only that
    the send is reported as having failed, but that the pool it came out of is no worse off for it.
    """

# ################################################################################################################################

    def test_a_listener_that_never_answers(self, outconn_environment:'OutconnEnvironment') -> 'None':
        """ A connection is accepted, the message is read, and nothing comes back. The send gives
        up when it was told to and the pool is still good for the sends after it.
        """
        client = outconn_environment.client

        receiver = RawSocketReceiver()
        receiver.start()

        try:
            config = {
                'recv_timeout': _Rough_Ending_Recv_Timeout,
                'pool_size': _Small_Pool_Size,
            }

            name = create_outconn(outconn_environment, 'silent', receiver.address, **config)

            for index in range(_Pool_Slot_Send_Count):

                result = send_one(client, name, build_adt_a01(f'SILENT-{index:04}'))

                # Every one of them fails the same way, which it could only do if the slot the
                # one before it took had gone back to the pool
                assert not result['is_sent']
                assert 'Timed out waiting for ACK' in result['error_text']

            # .. and every one of them got as far as connecting, rather than a later one
            # finding the pool empty and never reaching the listener at all
            assert receiver.connection_count >= _Pool_Slot_Send_Count

        finally:
            receiver.stop()

# ################################################################################################################################

    def test_a_listener_that_closes_half_way_through(self, outconn_environment:'OutconnEnvironment') -> 'None':
        """ A connection is accepted, something is read off it and then it is dropped. The send is
        reported as the connection having ended rather than as a timeout, and the pool holds up.
        """
        client = outconn_environment.client

        receiver = RawSocketReceiver(is_closing_early=True)
        receiver.start()

        try:
            config = {
                'recv_timeout': _Rough_Ending_Recv_Timeout,
                'pool_size': _Small_Pool_Size,
            }

            name = create_outconn(outconn_environment, 'half-closed', receiver.address, **config)

            for index in range(_Pool_Slot_Send_Count):

                result = send_one(client, name, build_adt_a01(f'HALF-{index:04}'))

                assert not result['is_sent']
                assert 'Connection closed before receiving a complete ACK' in result['error_text']

            assert receiver.connection_count >= _Pool_Slot_Send_Count

        finally:
            receiver.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestOutconnThroughAProxy:
    """ The everyday case with HAProxy in front of the listener, which is how these connections are
    deployed - a sender is given the proxy's address and never learns the receiver's.
    """

# ################################################################################################################################

    def test_a_message_crosses_a_proxy(
        self,
        outconn_environment:'OutconnEnvironment',
        receiver:'any_',
    ) -> 'None':
        """ A message sent to the proxy's address reaches the listener behind it, and the listener's
        acknowledgment comes back the same way.
        """
        if not is_haproxy_available():
            pytest.skip('HAProxy is not installed, so nothing can stand in front of the listener')

        client = outconn_environment.client

        directory = tempfile.mkdtemp(prefix='zato_mllp_outconn_proxy_')
        proxy = ProxyHandle(directory, receiver.port)
        proxy.start()

        try:
            name = create_outconn(outconn_environment, 'proxied', proxy.address)

            wait_until_ready(client, name)
            delivered_before = len(receiver.deliveries)

            result = send_one(client, name, build_adt_a01('PROXY-0001'))

            assert result['is_sent'], result['error_text']
            assert result['is_accepted']
            assert 'MSA|AA|PROXY-0001' in result['ack_text']

            arrived = next_delivery(receiver, delivered_before)

            assert get_msh_field(arrived, 10) == 'PROXY-0001'
            assert 'Doe^John' in get_segment(arrived, 'PID')

        finally:
            proxy.stop()

            for file_name in os.listdir(directory):
                os.remove(os.path.join(directory, file_name))

            os.rmdir(directory)

# ################################################################################################################################
# ################################################################################################################################
