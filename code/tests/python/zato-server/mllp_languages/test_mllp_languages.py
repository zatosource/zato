# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato - the suite's own parts
from _clients import send_with_java
from _messages import Ack_Accepted, Ack_Rejected, assert_ack_echoes_message, build_message, find_recorded, \
     new_control_id, read_received
from _services import Plain_Channel, TLS_Channel

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import MLLPEnvironment

    MLLPEnvironment = MLLPEnvironment

# ################################################################################################################################
# ################################################################################################################################

def test_java_client_over_a_plain_connection(mllp_environment:'MLLPEnvironment') -> 'None':
    """ A Java client sending over the plaintext bind reaches the channel that takes it and reads
    back an acknowledgment that echoes the header of what it sent.
    """
    control_id = new_control_id()
    message = build_message(Plain_Channel.sending_application, control_id)

    ack = send_with_java('127.0.0.1', mllp_environment.ports.mllp_plain, message)

    assert_ack_echoes_message(ack, control_id, Ack_Accepted)

    # .. and the message reached the service the channel invokes, unchanged.
    matching = find_recorded(mllp_environment.messages_file, control_id)

    assert len(matching) == 1, f'Expected the message once, found it {len(matching)} times'
    assert matching[0]['channel'] == Plain_Channel.label
    assert matching[0]['message'] == message

# ################################################################################################################################

def test_java_client_over_a_verified_tls_connection(mllp_environment:'MLLPEnvironment') -> 'None':
    """ A Java client presenting the certificate the channel's security definition names reaches
    that channel over the TLS bind, the common name having travelled from HAProxy to the listener.
    """
    control_id = new_control_id()
    message = build_message(TLS_Channel.sending_application, control_id)

    ack = send_with_java(
        '127.0.0.1', mllp_environment.ports.mllp_tls, message, certificates=mllp_environment.certificates)

    assert_ack_echoes_message(ack, control_id, Ack_Accepted)

    matching = find_recorded(mllp_environment.messages_file, control_id)

    assert len(matching) == 1, f'Expected the message once, found it {len(matching)} times'
    assert matching[0]['channel'] == TLS_Channel.label
    assert matching[0]['message'] == message

# ################################################################################################################################

def test_the_secured_channel_turns_away_an_unverified_sender(mllp_environment:'MLLPEnvironment') -> 'None':
    """ The same message sent over the plaintext bind carries no verified certificate, so the
    channel that requires one turns it away and its service never runs.
    """
    control_id = new_control_id()
    message = build_message(TLS_Channel.sending_application, control_id)

    ack = send_with_java('127.0.0.1', mllp_environment.ports.mllp_plain, message)

    assert_ack_echoes_message(ack, control_id, Ack_Rejected)

    received = read_received(mllp_environment.messages_file)

    for entry in received:
        assert control_id not in entry['message'], 'A message the channel turned away still reached a service'

# ################################################################################################################################
# ################################################################################################################################
