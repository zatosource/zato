# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import threading
from typing import NamedTuple

# Zato - the suite's own parts
from _clients import send_many_with_java
from _messages import Ack_Accepted, build_message, find_recorded, get_acknowledged_control_id, get_segment, \
     new_control_id
from _services import MLLPChannel, Open_Channels, TLS_Channel

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _certs import TestCertificates
    from conftest import MLLPEnvironment

    MLLPEnvironment = MLLPEnvironment
    TestCertificates = TestCertificates

# ################################################################################################################################
# ################################################################################################################################

# Where the clients connect, which is HAProxy on this machine rather than the listener itself
_Host = '127.0.0.1'

# How many messages travel down one connection when what is being looked at is the connection
# carrying messages for more than one channel rather than any concurrency between connections
_Messages_Per_Connection = 9
_Single_Connection = 1

# How many messages one run of the concurrent test sends and how many connections they are spread
# over. The two are set apart so that each connection carries several messages and each channel
# takes messages from several connections, which is the crossing the test is here for. Neither is
# large - what is being looked at is that nothing is mixed up, not how much can be put through.
_Concurrent_Message_Count    = 24
_Concurrent_Connection_Count = 6

# How many messages each bind is given in the run that drives both of them at the same time,
# and what the two senders of that run are known by
_Per_Bind_Message_Count    = 12
_Per_Bind_Connection_Count = 4

_Plain_Sender   = 'plain'
_Secured_Sender = 'secured'

# ################################################################################################################################
# ################################################################################################################################

class SentMessage(NamedTuple):
    """ One message a batch is made of, and what is expected to become of it.
    """

    # What makes this message its own, both in the answer that echoes it and in what a service recorded
    control_id: 'str'

    # The channel the message's sending application routes it to
    channel: 'MLLPChannel'

    # The message itself, which is what the service is expected to have recorded, character for character
    text: 'str'

# ################################################################################################################################

def _build_batch(channels:'list', message_count:'int') -> 'list':
    """ Builds messages dealt out over the channels one after another, so that a batch that travels
    several connections has each of them carrying messages for more than one channel.
    """
    out = []

    for index in range(message_count):

        channel = channels[index % len(channels)]
        control_id = new_control_id()

        out.append(SentMessage(
            control_id = control_id,
            channel    = channel,
            text       = build_message(channel.sending_application, control_id),
        ))

    return out

# ################################################################################################################################

def _get_texts(batch:'list') -> 'list':
    """ Returns what is handed to the client, which is the messages of a batch alone.
    """
    out = [item.text for item in batch]
    return out

# ################################################################################################################################

def _assert_all_were_answered(acks:'list', batch:'list') -> 'None':
    """ Checks that every message sent was answered, that each answer says the message was taken,
    and that no two answers refer to the same message. Which answer came back for which message
    is not said by the order they arrived in, so they are matched by what each of them echoes.
    """
    answered = []

    for ack in acks:

        msa_fields = get_segment(ack.decode('utf8'), 'MSA')
        assert msa_fields[1] == Ack_Accepted, f'A message was not taken: `{ack!r}`'

        answered.append(get_acknowledged_control_id(ack))

    expected = [item.control_id for item in batch]
    assert sorted(answered) == sorted(expected), 'The answers do not account for exactly the messages sent'

# ################################################################################################################################

def _assert_all_arrived(messages_file:'str', batch:'list') -> 'None':
    """ Checks that each message reached the service of the channel its sending application routes
    to, once and unchanged. A message recorded by another channel's service, twice or not at all is
    what a listener that mixed up concurrent connections would leave behind.
    """
    for item in batch:

        matching = find_recorded(messages_file, item.control_id)

        assert len(matching) == 1, f'Expected the message once at {item.channel.label}, found it {len(matching)} times'
        assert matching[0]['channel'] == item.channel.label, f'The message reached {matching[0]["channel"]}'
        assert matching[0]['message'] == item.text, 'The message was changed on its way to the service'

# ################################################################################################################################
# ################################################################################################################################

def test_one_connection_carries_messages_for_several_channels(mllp_environment:'MLLPEnvironment') -> 'None':
    """ Messages for different channels sent one after another down a single connection are each
    routed on their own, so what the first message matched does not govern what is read after it.
    """
    batch = _build_batch(Open_Channels, _Messages_Per_Connection)

    acks = send_many_with_java(_Host, mllp_environment.ports.mllp_plain, _get_texts(batch), _Single_Connection)

    _assert_all_were_answered(acks, batch)
    _assert_all_arrived(mllp_environment.messages_file, batch)

# ################################################################################################################################

def test_several_connections_send_to_several_channels_at_once(mllp_environment:'MLLPEnvironment') -> 'None':
    """ Connections held open at the same time, each carrying messages for more than one channel,
    are served without any of them being answered for another or reaching another's service.
    """
    batch = _build_batch(Open_Channels, _Concurrent_Message_Count)

    acks = send_many_with_java(
        _Host, mllp_environment.ports.mllp_plain, _get_texts(batch), _Concurrent_Connection_Count)

    _assert_all_were_answered(acks, batch)
    _assert_all_arrived(mllp_environment.messages_file, batch)

# ################################################################################################################################

def test_the_plain_and_secured_binds_are_driven_at_the_same_time(mllp_environment:'MLLPEnvironment') -> 'None':
    """ Senders on both binds at once are kept apart - the one whose certificate the load balancer
    verified reaches the channel that requires it, and neither run's messages land in the other's.
    """
    plain_batch = _build_batch(Open_Channels, _Per_Bind_Message_Count)
    secured_batch = _build_batch([TLS_Channel], _Per_Bind_Message_Count)

    acks = {}
    failures = {}

    def send(
        name:'str',
        port:'int',
        batch:'list',
        certificates:'TestCertificates | None',
    ) -> 'None':

        try:
            acks[name] = send_many_with_java(
                _Host, port, _get_texts(batch), _Per_Bind_Connection_Count, certificates)
        except Exception as e:

            # A failure here is on a thread of its own, where it would go no further than its own
            # output, so it is held for the test body to raise once both senders are done
            failures[name] = e

    threads = [
        threading.Thread(
            target=send, args=(_Plain_Sender, mllp_environment.ports.mllp_plain, plain_batch, None)),
        threading.Thread(
            target=send,
            args=(_Secured_Sender, mllp_environment.ports.mllp_tls, secured_batch, mllp_environment.certificates)),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert not failures, f'A sender failed: {failures}'

    _assert_all_were_answered(acks[_Plain_Sender], plain_batch)
    _assert_all_were_answered(acks[_Secured_Sender], secured_batch)

    _assert_all_arrived(mllp_environment.messages_file, plain_batch)
    _assert_all_arrived(mllp_environment.messages_file, secured_batch)

# ################################################################################################################################
# ################################################################################################################################
