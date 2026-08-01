# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato - the suite's own parts
from _outconn_messages import build_adt_a01, build_orm_o01, build_oru_of_size, build_oru_r01, get_msh_field, get_segment, \
    Utf8_Encoding
from _outconn_api import create_outconn, send_one, wait_until_ready
from _outconn_receivers import next_delivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import OutconnEnvironment
    from zato.common.typing_ import any_

    any_ = any_
    OutconnEnvironment = OutconnEnvironment

# ################################################################################################################################
# ################################################################################################################################

# How large the message the size test sends is. A megabyte is what a report with a history in it
# comes to, and it is well past the size one read off a socket brings in.
_One_Megabyte = 1024 * 1024

# The bound a connection is held to by the test that sends a message past it - small enough that
# the message which crosses it is quick to build and quick to send
_Small_Max_Message_Size = 4096

# How many observation segments the repeating-segments message carries
_Observation_Count = 20

# The non-standard framing bytes the framing test sets. Neither is the standard one, so a listener
# still reading the standard ones never sees the end of a message.
_Custom_Start_Sequence = '02'
_Custom_End_Sequence   = '03 0d'

# How long a send that is never going to be answered waits before giving up, in milliseconds. It is
# short because the test is over once the send has given up.
_Short_Recv_Timeout = 2000

# How long a send waits for an acknowledgment of a megabyte, in milliseconds. The default of a
# quarter of a second is what an everyday message is answered inside, and a real parser needs
# rather longer than that to read a megabyte and build a reply to it - which is the whole reason
# the field is on the connection.
_Large_Message_Recv_Timeout = 30000

# The names the encoding test sends, each of them written in a script that a message limited to
# what fits in seven bits could not carry
_Non_Ascii_Names = [
    ('Ostrowski', 'Zbigniew'),
    ('Müller', 'Jürgen'),
    ('Kovács', 'Erzsébet'),
    ('Οικονόμου', 'Αθανάσιος'),
    ('Иванова', 'Екатерина'),
    ('田中', '太郎'),
]

# ################################################################################################################################
# ################################################################################################################################

class TestOutconnEverydayMessages:
    """ What an outgoing connection is asked to carry on any day of the week, sent from a live
    server to the receiving stacks a hospital actually runs.
    """

# ################################################################################################################################

    def test_adt_a01_is_accepted_and_arrives(
        self,
        outconn_environment:'OutconnEnvironment',
        receiver:'any_',
    ) -> 'None':
        """ An admission message is acknowledged with AA, the acknowledgment names the message it
        answers, and the listener's own record shows the message that was sent.
        """
        client = outconn_environment.client
        name = create_outconn(outconn_environment, 'adt', receiver.address)

        wait_until_ready(client, name)
        delivered_before = len(receiver.deliveries)

        result = send_one(client, name, build_adt_a01('ADT-0001'))

        assert result['is_sent'], result['error_text']
        assert result['ack_code'] == 'AA'
        assert result['is_accepted']

        # The acknowledgment answers this message rather than some other one
        assert 'MSA|AA|ADT-0001' in result['ack_text']

        # .. and the listener's own record is what says it took delivery, an acknowledgment on
        # its own only saying that something at the far end answered
        arrived = next_delivery(receiver, delivered_before)

        assert get_msh_field(arrived, 10) == 'ADT-0001'
        assert 'ADT^A01' in get_msh_field(arrived, 9)
        assert 'Doe^John' in get_segment(arrived, 'PID')

# ################################################################################################################################

    def test_oru_r01_with_repeating_observations(
        self,
        outconn_environment:'OutconnEnvironment',
        receiver:'any_',
    ) -> 'None':
        """ A results message carrying twenty observation segments arrives with every one of them,
        which is where a parser that only ever saw one of everything gives itself away.
        """
        client = outconn_environment.client
        name = create_outconn(outconn_environment, 'oru', receiver.address)

        wait_until_ready(client, name)
        delivered_before = len(receiver.deliveries)

        result = send_one(client, name, build_oru_r01('ORU-0001', _Observation_Count))

        assert result['is_sent'], result['error_text']
        assert result['is_accepted']
        assert 'MSA|AA|ORU-0001' in result['ack_text']

        arrived = next_delivery(receiver, delivered_before)

        observation_lines = []

        for segment in arrived.split('\r'):
            if segment.startswith('OBX|'):
                observation_lines.append(segment)

        assert len(observation_lines) == _Observation_Count

        # The first and the last of them are checked by name, so that the right number of
        # segments in the wrong order would not pass either
        assert observation_lines[0].startswith('OBX|1|NM|WBC1^')
        assert observation_lines[-1].startswith(f'OBX|{_Observation_Count}|NM|WBC{_Observation_Count}^')

# ################################################################################################################################

    def test_orm_o01_is_accepted_and_arrives(
        self,
        outconn_environment:'OutconnEnvironment',
        receiver:'any_',
    ) -> 'None':
        """ An order message is the third of the types an interface is asked for by name, and it is
        acknowledged and recorded the way the other two are.
        """
        client = outconn_environment.client
        name = create_outconn(outconn_environment, 'orm', receiver.address)

        wait_until_ready(client, name)
        delivered_before = len(receiver.deliveries)

        result = send_one(client, name, build_orm_o01('ORM-0001'))

        assert result['is_sent'], result['error_text']
        assert result['is_accepted']
        assert 'MSA|AA|ORM-0001' in result['ack_text']

        arrived = next_delivery(receiver, delivered_before)

        assert get_msh_field(arrived, 10) == 'ORM-0001'
        assert get_segment(arrived, 'ORC').startswith('ORC|NW|ORD-001')

# ################################################################################################################################
# ################################################################################################################################

class TestOutconnEncoding:
    """ What a message carrying names outside ASCII looks like on the receiving side. Everything an
    outgoing connection sends goes onto the wire as UTF-8, so what is under test is whether a name
    written in any script survives the crossing byte for byte.
    """

# ################################################################################################################################

    def test_non_ascii_names_arrive_unchanged(
        self,
        outconn_environment:'OutconnEnvironment',
        receiver:'any_',
    ) -> 'None':
        """ Every name is read back on the receiving side exactly as it was sent, with MSH-18
        naming the encoding the bytes are in.
        """
        client = outconn_environment.client
        name = create_outconn(outconn_environment, 'encoding', receiver.address)

        wait_until_ready(client, name)

        for index, (family_name, given_name) in enumerate(_Non_Ascii_Names):

            control_id = f'ENC-{index:04}'
            delivered_before = len(receiver.deliveries)

            result = send_one(client, name, build_adt_a01(control_id, family_name, given_name, Utf8_Encoding))

            assert result['is_sent'], result['error_text']
            assert result['is_accepted']

            arrived = next_delivery(receiver, delivered_before)

            assert get_msh_field(arrived, 10) == control_id
            assert get_msh_field(arrived, 18) == Utf8_Encoding

            # The name is compared as it was written rather than as anything about how it
            # travelled, which is the whole of what this test is for
            assert f'{family_name}^{given_name}' in get_segment(arrived, 'PID')

# ################################################################################################################################

    def test_a_message_naming_no_encoding_still_arrives(
        self,
        outconn_environment:'OutconnEnvironment',
        receiver:'any_',
    ) -> 'None':
        """ A message with MSH-18 left empty is what most senders in the field write, and its
        non-ASCII names have to reach the other side whole all the same.
        """
        client = outconn_environment.client
        name = create_outconn(outconn_environment, 'encoding-unnamed', receiver.address)

        wait_until_ready(client, name)
        delivered_before = len(receiver.deliveries)

        family_name, given_name = _Non_Ascii_Names[0]
        result = send_one(client, name, build_adt_a01('ENC-NONE', family_name, given_name))

        assert result['is_sent'], result['error_text']
        assert result['is_accepted']

        arrived = next_delivery(receiver, delivered_before)

        assert get_msh_field(arrived, 18) == ''
        assert f'{family_name}^{given_name}' in get_segment(arrived, 'PID')

# ################################################################################################################################
# ################################################################################################################################

class TestOutconnMessageSize:
    """ What a connection does with a message at the size a report with a history in it comes to,
    and with one past the size the connection was told to carry.
    """

# ################################################################################################################################

    def test_one_megabyte_message_arrives_whole(
        self,
        outconn_environment:'OutconnEnvironment',
        receiver:'any_',
    ) -> 'None':
        """ A megabyte of results crosses in one piece, which is worth asserting because the read
        buffer is a fraction of that - the message is read in hundreds of reads rather than one.
        """
        client = outconn_environment.client

        message = build_oru_of_size('BIG-0001', _One_Megabyte)
        assert len(message) >= _One_Megabyte

        name = create_outconn(outconn_environment, 'size', receiver.address, recv_timeout=_Large_Message_Recv_Timeout)

        wait_until_ready(client, name)
        delivered_before = len(receiver.deliveries)

        result = send_one(client, name, message)

        assert result['is_sent'], result['error_text']
        assert result['is_accepted']

        arrived = next_delivery(receiver, delivered_before)

        assert get_msh_field(arrived, 10) == 'BIG-0001'

        # Every segment that was sent is a segment that arrived. Length is not what is compared,
        # because a real parser re-encodes what it read and drops the empty fields off the end
        # of a segment while it is at it - what has to survive is the content.
        sent_segments = message.split('\r')
        arrived_segments = arrived.rstrip('\r').split('\r')

        assert len(arrived_segments) == len(sent_segments)

        # .. and the last of them, a megabyte in, is still the one that was sent
        assert arrived_segments[-1] == sent_segments[-1]

# ################################################################################################################################

    def test_a_message_past_the_bound_is_refused_locally(
        self,
        outconn_environment:'OutconnEnvironment',
        receiver:'any_',
    ) -> 'None':
        """ A message larger than the connection was told to carry is turned away here rather than
        sent, so nothing of it reaches the listener at all.
        """
        client = outconn_environment.client

        message = build_oru_of_size('TOO-BIG-0001', _Small_Max_Message_Size * 4)
        assert len(message) > _Small_Max_Message_Size

        name = create_outconn(outconn_environment, 'size-bound', receiver.address, max_msg_size=_Small_Max_Message_Size)

        wait_until_ready(client, name)
        delivered_before = len(receiver.deliveries)

        result = send_one(client, name, message)

        # The send failed here rather than at the far end, there being nothing at the far end
        # that ever saw the message
        assert not result['is_sent']

        # .. and nothing of it reached the listener, which is what makes it a local refusal
        assert len(receiver.deliveries) == delivered_before

# ################################################################################################################################
# ################################################################################################################################

class TestOutconnFraming:
    """ How a message is wrapped for the wire. Both ends of a connection have to agree on it and
    both are configurable, third-party systems being strict about what they will read.
    """

# ################################################################################################################################

    def test_standard_framing_is_what_a_listener_expects(
        self,
        outconn_environment:'OutconnEnvironment',
        receiver:'any_',
    ) -> 'None':
        """ The framing every listener in the field expects is what a connection sends by default,
        which is why nothing has to be said about it for a message to get through.
        """
        client = outconn_environment.client
        config = {'start_seq': '0b', 'end_seq': '1c 0d'}

        name = create_outconn(outconn_environment, 'framing-standard', receiver.address, **config)

        wait_until_ready(client, name)
        delivered_before = len(receiver.deliveries)

        result = send_one(client, name, build_adt_a01('FRAME-0001'))

        assert result['is_sent'], result['error_text']
        assert result['is_accepted']

        arrived = next_delivery(receiver, delivered_before)
        assert get_msh_field(arrived, 10) == 'FRAME-0001'

# ################################################################################################################################

    def test_non_standard_framing_is_not_read_by_a_standard_listener(
        self,
        outconn_environment:'OutconnEnvironment',
        receiver:'any_',
    ) -> 'None':
        """ A connection framing its messages this way is talking to a listener that was told the
        same, and one that was not never sees the end of what it is sent. That is what makes the
        two fields worth having, and what makes getting them wrong so quiet.
        """
        client = outconn_environment.client

        config = {
            'start_seq': _Custom_Start_Sequence,
            'end_seq': _Custom_End_Sequence,

            # The send has to give up on its own rather than hold the test for as long as one
            # with no answer coming would otherwise wait
            'recv_timeout': _Short_Recv_Timeout,
        }

        name = create_outconn(outconn_environment, 'framing-custom', receiver.address, **config)

        delivered_before = len(receiver.deliveries)

        result = send_one(client, name, build_adt_a01('FRAME-0002'))

        # The listener never saw a message end, so it never answered and the send gave up
        assert not result['is_sent']

        # .. and nothing was recorded as having arrived, because as far as the listener is
        # concerned nothing has finished arriving
        assert len(receiver.deliveries) == delivered_before

# ################################################################################################################################
# ################################################################################################################################
