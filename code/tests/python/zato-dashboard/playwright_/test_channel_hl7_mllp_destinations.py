# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# pytest
import pytest

# Zato
from hl7_client.fhir_receiver import FHIRReceiver
from hl7_client.mllp_receiver import MLLPReceiver
from hl7_client.rest_receiver import RESTReceiver
from hl7_client.smtp_receiver import SMTPReceiver
from mllp_channel import create_channel, create_outgoing_connection, delete_channel, delete_outgoing_connection, \
    get_item_id, save_channel, send_python, send_with_both_clients, wait_for_item, wait_for_port, \
    wait_until_accepted, wait_until_routed, Host
from rest_outconn import create_outconn as create_rest_outconn, delete_outconn as delete_rest_outconn, \
    get_outconn_id, open_outconn_page
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.mllp.dest.' + CryptoManager.generate_hex_string(32) + '.'

# The fixture service that says what each destination receives - the REST one a message of
# its own, the FHIR one a resource, and the MLLP one nothing at all
_Populate_Service = 'test.hl7.mllp.wire.populate'

# What the populate service appends to what the REST destination alone receives - the same
# text the service module defines
_Rest_Note_Segment = 'NTE|1||For the care team alone'

# The senders each scenario's routing criteria are about - each unique so no message of one
# scenario ever lands on the channel of another
_Fanout_App    = 'FANOUT_SENDER'
_Populate_App  = 'POPULATE_SENDER'
_Same_Time_App = 'SAME_TIME_SENDER'
_In_Order_App  = 'IN_ORDER_SENDER'
_Respond_App   = 'RESPOND_SENDER'

# What the fan-out e-mail destination is configured with and asserted on
_Smtp_To      = 'care-team@example.com'
_Smtp_Subject = 'HL7 admission message'

# How long the slow receiver takes over each message in the delivery-mode scenario - long
# enough for the ordering of arrivals to be unambiguous
_Slow_Receiver_Delay = 3.0

# How long the slow receiver's connection waits for the ACK the receiver holds back -
# well beyond the delay, so a held-back ACK is a wait rather than a timeout
_Slow_Receiver_Recv_Timeout_Ms = 20000

# What the responding receiver of the respond-from scenario writes into MSA-3 of its
# acknowledgments, so the external clients can tell its answer from anyone else's
_Respond_Note = 'ANSWERED_BY_RECEIVER'

# How long the delivery-mode assertions wait beyond the slow receiver's own delay
_Mode_Timeout = 30

# How long a delivery that must never happen is given to prove it will not
_Absence_Wait = 3.0

# The FHIR dashboard page the FHIR outgoing connection is created through
_Fhir_Page_Url = '/zato/outgoing/hl7/fhir/?cluster=1&type_=outconn-hl7-fhir'

# The SMTP dashboard page the e-mail connection is created through
_Smtp_Page_Url = '/zato/email/smtp/?cluster=1'

# ################################################################################################################################
# ################################################################################################################################

def _wait_until_quiet(deliveries:'anylist') -> 'int':
    """ Returns how many deliveries a receiver holds once no more arrive. The probes that
    register a route are delivered too and there is nothing in a delivery to tell them from
    a test's own sends, so what they left behind has to settle before the sends begin.
    """
    count = len(deliveries)
    deadline = time.monotonic() + _Absence_Wait * 10

    while time.monotonic() < deadline:

        time.sleep(_Absence_Wait)

        if len(deliveries) == count:
            break

        count = len(deliveries)

    return count

# ################################################################################################################################

def _create_fhir_connection(page:'Page', base_url:'str', name:'str', address:'str') -> 'None':
    """ Creates an outgoing FHIR connection through its own page.
    """
    _ = page.goto(f'{base_url}{_Fhir_Page_Url}')
    _ = page.wait_for_selector('#data-table', state='visible')

    page.click('#markup .page_prompt a:has-text("Create a new connection")')
    _ = page.wait_for_selector('#create-div', state='visible')

    page.fill('#id_name', name)
    page.fill('#id_address', address)

    # The security select starts on its blank choice and the form treats it as required -
    # a chosen widget hides the select itself, so the value goes in through jQuery
    page.evaluate('$("#id_security_id").val("ZATO_NONE").trigger("chosen:updated").trigger("change")')

    page.click('#create-div input[type="submit"]')
    _ = page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    _ = page.wait_for_selector(f'#data-table tbody tr:has(td:text-is("{name}"))', state='visible', timeout=5000)

# ################################################################################################################################

def _delete_fhir_connection(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Deletes an outgoing FHIR connection through its own page.
    """
    _ = page.goto(f'{base_url}{_Fhir_Page_Url}')
    _ = page.wait_for_selector('#data-table', state='visible')

    item_id = get_item_id(page, name)

    page.evaluate(f'$.fn.zato.outgoing.hl7.fhir.delete_("{item_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

# ################################################################################################################################

def _create_smtp_connection(page:'Page', base_url:'str', name:'str', port:'int') -> 'None':
    """ Creates an outgoing SMTP connection through its own page, in the plain mode the
    test's aiosmtpd receiver speaks.
    """
    _ = page.goto(f'{base_url}{_Smtp_Page_Url}')
    _ = page.wait_for_selector('#data-table', state='visible')

    page.click('#markup .page_prompt a:has-text("Create a new SMTP connection")')
    _ = page.wait_for_selector('#create-div', state='visible')

    page.fill('#id_name', name)
    page.fill('#id_host', Host)
    page.fill('#id_port', str(port))
    page.fill('#id_from_address', 'zato@example.com')
    _ = page.select_option('#id_mode', 'plain')

    page.click('#create-div input[type="submit"]')
    _ = page.wait_for_selector('#create-div', state='hidden', timeout=10000)

    _ = page.wait_for_selector(f'#data-table tbody tr:has(td:text-is("{name}"))', state='visible', timeout=5000)

# ################################################################################################################################

def _delete_smtp_connection(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Deletes an outgoing SMTP connection through its own page.
    """
    _ = page.goto(f'{base_url}{_Smtp_Page_Url}')
    _ = page.wait_for_selector('#data-table', state='visible')

    item_id = get_item_id(page, name)

    page.evaluate(f'$.fn.zato.email.smtp.delete_("{item_id}")')
    _ = page.wait_for_selector('#popup_container', state='visible', timeout=5000)
    page.click('#popup_ok')
    time.sleep(0.5)

# ################################################################################################################################

def _mllp_destination(connection:'str') -> 'anydict':
    out = {'connection': connection, 'type': 'hl7-mllp', 'is_active': True, 'options': {}}
    return out

# ################################################################################################################################

def _rest_destination(connection:'str') -> 'anydict':
    out = {'connection': connection, 'type': 'rest', 'is_active': True, 'options': {'method': 'POST'}}
    return out

# ################################################################################################################################

def _fhir_destination(connection:'str') -> 'anydict':
    out = {'connection': connection, 'type': 'hl7-fhir', 'is_active': True,
        'options': {'method': 'POST', 'path': '/Patient'}}
    return out

# ################################################################################################################################

def _smtp_destination(connection:'str') -> 'anydict':
    out = {'connection': connection, 'type': 'smtp', 'is_active': True,
        'options': {'to': _Smtp_To, 'subject': _Smtp_Subject}}
    return out

# ################################################################################################################################

def _text_has(control_id:'str') -> 'any_':
    """ A predicate matching a receiver item whose .text carries this control id.
    """
    def _predicate(item:'any_') -> 'bool':
        out = control_id in item.text
        return out

    return _predicate

# ################################################################################################################################

def _body_has(control_id:'str') -> 'any_':
    """ A predicate matching a receiver item whose .body carries this control id.
    """
    def _predicate(item:'any_') -> 'bool':
        out = control_id in item.body
        return out

    return _predicate

# ################################################################################################################################

def _delete_rest_connection(page:'Page', base_url:'str', name:'str') -> 'None':
    """ Deletes an outgoing REST connection through its own page.
    """
    open_outconn_page(page, base_url)

    outconn_id = get_outconn_id(page, name)
    delete_rest_outconn(page, outconn_id)

# ################################################################################################################################
# ################################################################################################################################

class TestChannelHL7MLLPDestinations:
    """ Creates channels with destinations of every type through the wizard and proves, from
    outside over the wire, that what arrives on the channel reaches every receiver - the
    receivers being the same libraries other systems receive with: hl7apy for MLLP, aiosmtpd
    for e-mail and fhir.resources validating what the FHIR destination sends. The destination
    list, the delivery mode and the destination that replies are all answers the wizard has to
    read back before it can save a channel again, so each is proved once more after a save.
    """

    @pytest.mark.expect_log_errors('No matching MLLP channel for message')
    def test_destination_fanout(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ One message fans out to MLLP, REST and e-mail receivers at once, each getting
        the message exactly as it arrived on the channel.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        mllp_port = zato_dashboard['mllp_port']

        channel_name = _Test_Name_Prefix + 'fanout'
        mllp_conn    = _Test_Name_Prefix + 'fanout-mllp'
        rest_conn    = _Test_Name_Prefix + 'fanout-rest'
        smtp_conn    = _Test_Name_Prefix + 'fanout-smtp'

        # The receiving side - each receiver is a real server on its own port
        mllp_receiver = MLLPReceiver()
        rest_receiver = RESTReceiver()
        smtp_receiver = SMTPReceiver()

        mllp_receiver.start()
        rest_receiver.start()
        smtp_receiver.start()

        try:
            # The outgoing connections the destinations point at, each created through its own page ..
            create_outgoing_connection(page, base_url, mllp_conn, f'{Host}:{mllp_receiver.port}')
            _ = create_rest_outconn(page, base_url, rest_conn, f'http://{Host}:{rest_receiver.port}',
                {'url_path': '/deliver'})
            _create_smtp_connection(page, base_url, smtp_conn, smtp_receiver.port)

            # .. the channel itself, with no service - the destinations alone take the message ..
            destinations = [
                _mllp_destination(mllp_conn),
                _rest_destination(rest_conn),
                _smtp_destination(smtp_conn),
            ]

            create_channel(page, base_url, channel_name,
                criteria={'msh3_sending_app': _Fanout_App}, destinations=destinations)

            # .. and the wire work starts once the channel answers for its route.
            wait_for_port(mllp_port)
            _ = wait_until_accepted(mllp_port, _Fanout_App)

            # Each sender's message must reach every receiver ..
            self._check_fanout(mllp_port, mllp_receiver, rest_receiver, smtp_receiver)

            # .. and it still must once the channel has been saved through the wizard again
            # with nothing changed, which is the whole destination list - the connection of
            # each, the type of each and the options of each - read back and posted anew.
            save_channel(page, base_url, channel_name)
            _ = wait_until_accepted(mllp_port, _Fanout_App)

            self._check_fanout(mllp_port, mllp_receiver, rest_receiver, smtp_receiver)

        finally:
            delete_channel(page, base_url, channel_name)
            delete_outgoing_connection(page, base_url, mllp_conn)
            _delete_rest_connection(page, base_url, rest_conn)
            _delete_smtp_connection(page, base_url, smtp_conn)

            mllp_receiver.stop()
            rest_receiver.stop()
            smtp_receiver.stop()

# ################################################################################################################################

    def _check_fanout(
        self,
        mllp_port:'int',
        mllp_receiver:'MLLPReceiver',
        rest_receiver:'RESTReceiver',
        smtp_receiver:'SMTPReceiver',
        ) -> 'None':
        """ What each external client sends reaches all three receivers - the MLLP one as the
        message arrived, the REST one as the body of a POST, and the e-mail one under the
        subject and to the recipient the destination's options name.
        """
        for control_id, result in send_with_both_clients(mllp_port, _Fanout_App):

            assert result.msa_1 == 'AA', f'Expected AA, got: {result}'

            # The MLLP receiver got the message as it arrived ..
            delivery = wait_for_item(
                mllp_receiver.deliveries, _text_has(control_id), f'MLLP delivery of {control_id}')
            assert _Fanout_App in delivery.text, f'Expected the sender in the delivery, got: {delivery.text}'

            # .. so did the REST receiver, as the body of a POST ..
            request = wait_for_item(
                rest_receiver.requests, _body_has(control_id), f'REST delivery of {control_id}')
            assert request.method == 'POST', f'Expected a POST, got: {request.method}'
            assert request.path == '/deliver', f'Expected /deliver, got: {request.path}'

            # .. and so did the e-mail receiver, under the subject and to the recipient
            # the destination's options name.
            email = wait_for_item(
                smtp_receiver.messages, _body_has(control_id), f'e-mail delivery of {control_id}')
            assert email.recipients == [_Smtp_To], f'Expected `{_Smtp_To}`, got: {email.recipients}'
            assert email.subject == _Smtp_Subject, f'Expected `{_Smtp_Subject}`, got: {email.subject}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors('No matching MLLP channel for message')
    def test_payload_population(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A service decides per destination - the REST receiver gets a message of the
        service's own making, the FHIR receiver a specification-valid resource, and the
        MLLP receiver nothing at all.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        mllp_port = zato_dashboard['mllp_port']

        channel_name = _Test_Name_Prefix + 'populate'
        mllp_conn    = _Test_Name_Prefix + 'populate-mllp'
        rest_conn    = _Test_Name_Prefix + 'populate-rest'
        fhir_conn    = _Test_Name_Prefix + 'populate-fhir'

        mllp_receiver = MLLPReceiver()
        rest_receiver = RESTReceiver()
        fhir_receiver = FHIRReceiver()

        mllp_receiver.start()
        rest_receiver.start()
        fhir_receiver.start()

        try:
            create_outgoing_connection(page, base_url, mllp_conn, f'{Host}:{mllp_receiver.port}')
            _ = create_rest_outconn(page, base_url, rest_conn, f'http://{Host}:{rest_receiver.port}',
                {'url_path': '/deliver'})
            _create_fhir_connection(page, base_url, fhir_conn, f'http://{Host}:{fhir_receiver.port}')

            destinations = [
                _mllp_destination(mllp_conn),
                _rest_destination(rest_conn),
                _fhir_destination(fhir_conn),
            ]

            create_channel(page, base_url, channel_name, service=_Populate_Service,
                criteria={'msh3_sending_app': _Populate_App}, destinations=destinations)

            wait_for_port(mllp_port)
            _ = wait_until_accepted(mllp_port, _Populate_App)

            # The probes that registered the route were delivered as well and one resource looks
            # like another, so their deliveries are counted in before any send of this test's own
            fhir_count_before = _wait_until_quiet(fhir_receiver.resources)

            control_ids = []

            for control_id, result in send_with_both_clients(mllp_port, _Populate_App):
                assert result.msa_1 == 'AA', f'Expected AA, got: {result}'
                control_ids.append(control_id)

            for control_id in control_ids:

                # The REST receiver got the message the service made for it - the original
                # plus the note segment the service appended ..
                request = wait_for_item(
                    rest_receiver.requests, _body_has(control_id), f'REST delivery of {control_id}')
                assert _Rest_Note_Segment in request.body, f'Expected the note segment, got: {request.body}'

            # .. the FHIR receiver got one resource per send - the resource itself is the
            # service's own, so what tells the sends apart is how many arrived ..
            expected_fhir_count = fhir_count_before + len(control_ids)

            deadline = time.monotonic() + _Absence_Wait * 10

            while len(fhir_receiver.resources) < expected_fhir_count:
                if time.monotonic() > deadline:
                    raise Exception(f'Expected {expected_fhir_count} FHIR deliveries, got {len(fhir_receiver.resources)}')
                time.sleep(0.2)

            # .. each of them a real Patient the fhir.resources model of the specification accepts ..
            for resource in fhir_receiver.resources[fhir_count_before:]:
                assert resource.is_valid, f'Expected a specification-valid resource, got: {resource.error}'
                assert resource.document['resourceType'] == 'Patient', f'Unexpected resource: {resource.document}'
                assert resource.document['name'][0]['family'] == 'Johnson', f'Unexpected resource: {resource.document}'

            # .. and the MLLP receiver, whose destination the service dropped, got nothing
            # of these messages at all.
            time.sleep(_Absence_Wait)

            for delivery in mllp_receiver.deliveries:
                for control_id in control_ids:
                    assert control_id not in delivery.text, f'The dropped destination received: {delivery.text}'

        finally:
            delete_channel(page, base_url, channel_name)
            delete_outgoing_connection(page, base_url, mllp_conn)
            _delete_rest_connection(page, base_url, rest_conn)
            _delete_fhir_connection(page, base_url, fhir_conn)

            mllp_receiver.stop()
            rest_receiver.stop()
            fhir_receiver.stop()

# ################################################################################################################################

    @pytest.mark.expect_log_errors('No matching MLLP channel for message')
    def test_delivery_modes(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ The same two destinations behave differently under each delivery mode - with
        in-order the fast receiver waits behind the slow one, with same-time it does not.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        mllp_port = zato_dashboard['mllp_port']

        same_time_channel = _Test_Name_Prefix + 'same-time'
        in_order_channel  = _Test_Name_Prefix + 'in-order'
        slow_conn         = _Test_Name_Prefix + 'mode-slow'
        fast_conn         = _Test_Name_Prefix + 'mode-fast'

        # The first receiver takes its time over each message, the second does not
        slow_receiver = MLLPReceiver(delay=_Slow_Receiver_Delay)
        fast_receiver = MLLPReceiver()

        slow_receiver.start()
        fast_receiver.start()

        try:
            # The slow receiver holds each ACK back longer than the form's default receive
            # timeout, so the connection pointing at it gets a timeout beyond the delay
            create_outgoing_connection(page, base_url, slow_conn, f'{Host}:{slow_receiver.port}',
                recv_timeout_ms=_Slow_Receiver_Recv_Timeout_Ms)
            create_outgoing_connection(page, base_url, fast_conn, f'{Host}:{fast_receiver.port}')

            # Both channels declare the slow destination first, the fast one second - the
            # delivery mode alone is what differs between the two
            destinations = [
                _mllp_destination(slow_conn),
                _mllp_destination(fast_conn),
            ]

            create_channel(page, base_url, same_time_channel,
                criteria={'msh3_sending_app': _Same_Time_App},
                destinations=destinations, delivery_mode='same-time')

            create_channel(page, base_url, in_order_channel,
                criteria={'msh3_sending_app': _In_Order_App},
                destinations=destinations, delivery_mode='in-order')

            wait_for_port(mllp_port)
            _ = wait_until_accepted(mllp_port, _Same_Time_App)
            _ = wait_until_accepted(mllp_port, _In_Order_App)

            # With same-time, the fast receiver's copy arrives while the slow receiver
            # is still busy with its own ..
            control_id = 'py.' + CryptoManager.generate_hex_string()
            result = send_python(mllp_port, control_id, _Same_Time_App)
            assert result.msa_1 == 'AA', f'Expected AA, got: {result}'

            slow_delivery, fast_delivery = self._wait_for_both(slow_receiver, fast_receiver, control_id)

            overlap_details = f'fast at {fast_delivery.arrived_at}, slow done at {slow_delivery.completed_at}'
            assert fast_delivery.arrived_at < slow_delivery.completed_at, \
                f'Same-time deliveries should overlap - {overlap_details}'

            # .. and with in-order, the fast receiver is only reached once the slow
            # receiver has finished ..
            self._check_in_order(mllp_port, slow_receiver, fast_receiver)

            # .. which is still so once that channel has been saved through the wizard again
            # with nothing changed - a mode the wizard failed to read back would leave the
            # channel on the one a new channel starts with, and the two would overlap.
            save_channel(page, base_url, in_order_channel)
            _ = wait_until_accepted(mllp_port, _In_Order_App)

            self._check_in_order(mllp_port, slow_receiver, fast_receiver)

        finally:
            delete_channel(page, base_url, same_time_channel)
            delete_channel(page, base_url, in_order_channel)
            delete_outgoing_connection(page, base_url, slow_conn)
            delete_outgoing_connection(page, base_url, fast_conn)

            slow_receiver.stop()
            fast_receiver.stop()

# ################################################################################################################################

    def _check_in_order(
        self,
        mllp_port:'int',
        slow_receiver:'MLLPReceiver',
        fast_receiver:'MLLPReceiver',
        ) -> 'None':
        """ One message on the in-order channel, whose fast receiver may only be reached
        once the slow one has finished with its own copy.
        """
        control_id = 'py.' + CryptoManager.generate_hex_string()
        result = send_python(mllp_port, control_id, _In_Order_App)
        assert result.msa_1 == 'AA', f'Expected AA, got: {result}'

        slow_delivery, fast_delivery = self._wait_for_both(slow_receiver, fast_receiver, control_id)

        order_details = f'fast at {fast_delivery.arrived_at}, slow done at {slow_delivery.completed_at}'
        assert fast_delivery.arrived_at >= slow_delivery.completed_at, \
            f'In-order deliveries should be serialized - {order_details}'

# ################################################################################################################################

    def _wait_for_both(
        self,
        slow_receiver:'MLLPReceiver',
        fast_receiver:'MLLPReceiver',
        control_id:'str',
        ) -> 'tuple':
        """ Waits until each receiver has the message with this control id and returns the
        two deliveries, the slow receiver's one first.
        """
        deadline = time.monotonic() + _Mode_Timeout
        slow_delivery = None
        fast_delivery = None

        while time.monotonic() < deadline:

            for item in slow_receiver.deliveries:
                if control_id in item.text:
                    slow_delivery = item

            for item in fast_receiver.deliveries:
                if control_id in item.text:
                    fast_delivery = item

            if slow_delivery and fast_delivery:
                out = slow_delivery, fast_delivery
                return out

            time.sleep(0.2)

        raise Exception(f'Both deliveries of {control_id} did not arrive within {_Mode_Timeout}s')

# ################################################################################################################################

    @pytest.mark.expect_log_errors('No matching MLLP channel for message')
    def test_respond_from_destination(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A channel replying from its MLLP destination answers its senders with what that
        destination's receiver said, which both external clients read off their sockets.
        """
        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        mllp_port = zato_dashboard['mllp_port']

        channel_name = _Test_Name_Prefix + 'respond-from'
        mllp_conn    = _Test_Name_Prefix + 'respond-mllp'

        # The receiver marks each of its acknowledgments in MSA-3, so an answer of its
        # making cannot be mistaken for the listener's own
        receiver = MLLPReceiver(ack_note=_Respond_Note)
        receiver.start()

        try:
            create_outgoing_connection(page, base_url, mllp_conn, f'{Host}:{receiver.port}')

            create_channel(page, base_url, channel_name,
                criteria={'msh3_sending_app': _Respond_App},
                destinations=[_mllp_destination(mllp_conn)],
                respond_from=mllp_conn)

            # Every client's reply is the receiver's acknowledgment, control id and all ..
            wait_for_port(mllp_port)
            self._check_reply_from_receiver(mllp_port)

            # .. and it still is once the channel has been saved through the wizard again with
            # nothing changed, the destination that replies being one of the answers the
            # wizard has to read back before it can post it anew.
            save_channel(page, base_url, channel_name)
            self._check_reply_from_receiver(mllp_port)

        finally:
            delete_channel(page, base_url, channel_name)
            delete_outgoing_connection(page, base_url, mllp_conn)

            receiver.stop()

# ################################################################################################################################

    def _check_reply_from_receiver(self, mllp_port:'int') -> 'None':
        """ What each external client reads off its socket is the acknowledgment the
        destination's receiver made, its note in MSA-3 being how they tell that answer from
        the listener's own.
        """
        wait_until_routed(mllp_port, _Respond_Note, _Respond_App)

        for control_id, result in send_with_both_clients(mllp_port, _Respond_App):

            assert result.msa_1 == 'AA', f'Expected AA, got: {result}'
            assert result.msa_2 == control_id, f'Expected the control id echoed, got: {result}'
            assert result.msa_3 == _Respond_Note, f'Expected the receiver to answer, got: {result}'

# ################################################################################################################################
# ################################################################################################################################
