# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode
from time import monotonic, sleep

# pytest
import pytest

# Zato
from zato.common.api import AS2
from zato.common.crypto.api import CryptoManager

# Zato - the shared Playwright helpers
from as2_outconn import create_as2_outconn, delete_as2_outconn, edit_as2_outconn, open_as2_outconn_page, \
    wait_for_as2_outconn_row
from as4_keys import new_party
from soap_outconn import invoke_service_in_ide

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict
    from client import ZatoClient

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.as2.live.' + CryptoManager.generate_hex_string(32) + '.'

# The pre-deployed fixture services this suite drives and routes to
_Invoker_Service  = 'test.as2live.invoke'
_Receiver_Service = 'test.as2live.receiver'

# The Dashboard page holding our own side of the inbound channel's key material
_Keystore_Page_Url = '/zato/as2/keystore/?cluster=1'

# The services the keystore snapshot and its restore go through
_Keystore_Get  = 'zato.channel.as2.keystore.get'
_Keystore_Edit = 'zato.channel.as2.keystore.edit'

# How long to keep retrying an invocation while a UI change propagates to the server
_Propagation_Timeout = 60

# How long to sleep between the attempts above
_Propagation_Poll_Interval = 1.0

# Log lines this suite's exchanges and propagation retries can produce on the server
_AS2_Log_Patterns = ('AS2 delivery not confirmed', 'AS2 request rejected')

# The DER-encoded OID of CMS EnvelopedData - its presence at the front of the wire body
# is what says the outermost layer is encryption.
_Enveloped_Data_OID = bytes([0x06, 0x09, 0x2A, 0x86, 0x48, 0x86, 0xF7, 0x0D, 0x01, 0x07, 0x03])

# How far into the wire body the OID above may sit - it belongs to the outermost ContentInfo.
_OID_Search_Window = 64

# ################################################################################################################################
# ################################################################################################################################

def _open_invoker_in_ide(page:'Page', base_url:'str') -> 'None':
    """ Opens the pre-deployed AS2 invoker service in the IDE and waits until the Invoke button is usable.
    """
    _ = page.goto(f'{base_url}/zato/service/ide/service/{_Invoker_Service}/?cluster=1')
    _ = page.wait_for_selector('#invoke-service:not([disabled])', state='visible', timeout=15000)

# ################################################################################################################################

def _wait_for_invoker_service(page:'Page', base_url:'str') -> 'None':
    """ Opens the invoker service in the IDE and keeps clicking Invoke with a readiness
    probe until the service responds, confirming it deployed during server boot.
    """
    _open_invoker_in_ide(page, base_url)

    deadline = monotonic() + _Propagation_Timeout
    last_error = None

    while monotonic() < deadline:
        try:
            response = invoke_service_in_ide(page, {'mode': 'ping'})
        except Exception as probe_error:
            last_error = probe_error
            sleep(_Propagation_Poll_Interval)
        else:
            if response.get('is_ready'):
                return
            sleep(_Propagation_Poll_Interval)

    raise Exception(f'Service `{_Invoker_Service}` did not deploy within {_Propagation_Timeout}s, last: {last_error!r}')

# ################################################################################################################################

def _invoke_until(page:'Page', base_url:'str', request:'anydict', is_done_func:'any_') -> 'anydict':
    """ Invokes the fixture service from the IDE until its reply satisfies the given
    condition, retrying while the pair configured a moment ago in the browser
    propagates to the server.
    """
    _open_invoker_in_ide(page, base_url)

    deadline = monotonic() + _Propagation_Timeout
    last_reply = None

    while monotonic() < deadline:
        out = invoke_service_in_ide(page, request)
        last_reply = out

        if is_done_func(out):
            return out

        sleep(_Propagation_Poll_Interval)

    raise Exception(f'The reply never satisfied the condition within {_Propagation_Timeout}s, last: {last_reply}')

# ################################################################################################################################

def _is_reply_ok(reply:'anydict') -> 'bool':
    """ Matches a delivery reply whose MDN reconciled - a reply the send itself
    errored out on carries only its error field and no delivery report at all.
    """
    if 'is_ok' not in reply:
        return False

    out = reply['is_ok']
    return out

# ################################################################################################################################

def _wire_body(reply:'anydict') -> 'bytes':
    """ Returns the raw MIME body one delivery went over the wire with.
    """
    out = b64decode(reply['request_body'])
    return out

# ################################################################################################################################

def _set_channel_keystore(page:'Page', base_url:'str', party:'any_') -> 'None':
    """ Points the inbound AS2 channel's keystore at the given party through
    the Dashboard keystore page.
    """
    _ = page.goto(f'{base_url}{_Keystore_Page_Url}')
    _ = page.wait_for_selector('#keystore-form', state='visible')

    page.fill('#id_as2_signing_key', party.key)
    page.fill('#id_as2_signing_cert_chain', party.certificate)
    page.fill('#id_as2_decryption_key', party.key)

    # An earlier save may have left the message showing - hide it so the wait below
    # only passes once this save's response has arrived.
    _ = page.evaluate("$('#user-message-div').hide()")

    page.click('#keystore-form input[type="submit"]')
    _ = page.wait_for_selector('#user-message-div', state='visible')

    message = page.inner_text('#user-message')
    assert 'Keystore saved' in message

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def original_keystore(api_client:'ZatoClient') -> 'any_':
    """ Snapshots the inbound channel's keystore before this module runs and puts it back
    afterwards - the tests themselves change it through the browser only.
    """
    original = api_client.invoke(_Keystore_Get)

    yield original

    restore_request = {}

    for name in AS2.Keystore_Fields:
        restore_request[name] = original[name]

    _ = api_client.invoke(_Keystore_Edit, restore_request)

# ################################################################################################################################
# ################################################################################################################################

class _Loopback:
    """ One configured loopback pair - the sending connection pointed at this server's
    own inbound AS2 channel and the reverse connection the channel resolves the
    arriving identity pair against.
    """
    def __init__(self) -> 'None':
        self.sender_name = ''
        self.sender_id = ''
        self.receiver_id = ''

# ################################################################################################################################

def _new_loopback(
    page:'Page',
    zato_dashboard:'anydict',
    channel_party:'any_',
    sender_party:'any_',
    name_infix:'str',
    sender_options:'anydict',
    ) -> '_Loopback':
    """ Creates both sides of one loopback exchange through the Dashboard - the identities
    are unique per run so the exchange reconciles against itself only.
    """
    base_url = zato_dashboard['dashboard_url']
    server_port = zato_dashboard['server_port']

    suffix = CryptoManager.generate_hex_string()
    sender_identity = f'ZatoRetail.{suffix}'
    receiver_identity = f'PartnerCorp.{suffix}'

    # The message goes to this server's own inbound AS2 channel.
    endpoint_url = f'http://127.0.0.1:{server_port}{AS2.Default.Channel_URL_Path}'

    out = _Loopback()
    out.sender_name = _Test_Name_Prefix + name_infix

    # The sending side of the exchange ..
    sender_form = {
        'as2_from': sender_identity,
        'as2_to': receiver_identity,
        'as2_partner_cert': channel_party.certificate,
        'as2_signing_key': sender_party.key,
        'as2_signing_cert_chain': sender_party.certificate,
        'as2_decryption_key': sender_party.key,
    }
    sender_form.update(sender_options)

    out.sender_id = create_as2_outconn(page, base_url, out.sender_name, endpoint_url, sender_form)

    # .. and the receiving side - the inbound channel matches the reversed identity pair
    # against this connection and routes the payload to the pre-deployed receiver service.
    receiver_name = _Test_Name_Prefix + name_infix + '.reverse'

    out.receiver_id = create_as2_outconn(page, base_url, receiver_name, 'https://as2.example.com/exchange', {
        'as2_from': receiver_identity,
        'as2_to': sender_identity,
        'as2_partner_cert': sender_party.certificate,
        'as2_signing_key': channel_party.key,
        'as2_signing_cert_chain': channel_party.certificate,
        'as2_decryption_key': channel_party.key,
        'inbound_service': _Receiver_Service,
    })

    return out

# ################################################################################################################################

def _delete_loopback(page:'Page', loopback:'_Loopback') -> 'None':
    """ Removes both sides of one loopback exchange through the Dashboard.
    """
    delete_as2_outconn(page, loopback.sender_id)
    delete_as2_outconn(page, loopback.receiver_id)

# ################################################################################################################################

def _edit_sender(page:'Page', base_url:'str', loopback:'_Loopback', options:'anydict') -> 'None':
    """ Applies changes to the sending connection through the Dashboard edit dialog -
    the page has to be back on the connections list first, because the tests
    drive the IDE in between the edits.
    """
    open_as2_outconn_page(page, base_url, query=loopback.sender_name)
    _ = wait_for_as2_outconn_row(page, loopback.sender_name)

    edit_as2_outconn(page, loopback.sender_id, options)

# ################################################################################################################################
# ################################################################################################################################

class TestAS2LiveLoopback:
    """ The live end-to-end loopback of 13.4.1 - an outgoing AS2 connection created
    through the Dashboard and pointed at this server's own inbound AS2 channel,
    a pre-deployed service builds a typed 850 with the X12 dictionaries and sends it
    through self.as2, the payload arrives through the configured routing and the
    synchronous MDN reconciles on the sending side.
    """

    @pytest.mark.expect_log_errors(*_AS2_Log_Patterns)
    def test_typed_850_loopback(
        self, logged_in_page:'Page', zato_dashboard:'anydict', original_keystore:'any_') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _wait_for_invoker_service(page, base_url)
        _ = invoke_service_in_ide(page, {'mode': 'clear-received'})

        # The channel's own key material goes in through the Dashboard keystore page ..
        channel_party = new_party('as2-live-channel')
        sender_party = new_party('as2-live-sender')

        _set_channel_keystore(page, base_url, channel_party)

        # .. and both sides of the exchange through the connections page.
        loopback = _new_loopback(page, zato_dashboard, channel_party, sender_party, 'loopback', {})

        try:

            # One send now goes service -> self.as2 -> the channel -> the receiver service.
            reply = _invoke_until(page, base_url,
                {'mode': 'send-850', 'connection': loopback.sender_name}, _is_reply_ok)

            # The sender verified the synchronous MDN - signed, processed and MIC-matched.
            assert reply['is_ok'] is True
            assert reply['message_id']
            assert reply['has_mdn'] is True
            assert reply['mdn_signed'] is True
            assert reply['disposition'] == 'processed'
            assert reply['mic_matched'] is True

            # .. and the typed 850 arrived through the configured routing, byte for byte,
            # with the envelope identifiers the channel read out of it.
            received = invoke_service_in_ide(page, {'mode': 'get-received'})['received']
            assert len(received) == 1, f'Expected exactly one routed message, got: {received}'

            # The routed message carries the Message-ID in its normalized form,
            # without the angle brackets the wire form travels with.
            message = received[0]
            assert message['message_id'] == reply['message_id'].strip('<>'), f'Expected the message id, got: {message}'
            assert message['data'] == reply['payload'], f'Expected the payload, got: {message}'
            assert message['edi']['document_type'] == '850', f'Expected an 850, got: {message}'
            assert message['edi']['sender_id'] == 'ZATORETAIL', f'Expected the EDI sender, got: {message}'

        finally:
            _delete_loopback(page, loopback)

# ################################################################################################################################
# ################################################################################################################################

class TestAS2LiveWireShape:
    """ The toggle flips of 13.4.2 - signing, encryption and compression turned on and off
    through the Dashboard edit dialog, with the raw MIME body of each delivery asserting
    that the wire shape actually changed.
    """

    @pytest.mark.expect_log_errors(*_AS2_Log_Patterns)
    def test_toggles_change_the_wire_shape(
        self, logged_in_page:'Page', zato_dashboard:'anydict', original_keystore:'any_') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _wait_for_invoker_service(page, base_url)

        channel_party = new_party('as2-live-wire-channel')
        sender_party = new_party('as2-live-wire-sender')

        _set_channel_keystore(page, base_url, channel_party)

        # The payload carries a marker so its clear-text presence on the wire is checkable.
        payload = 'WIRESHAPE-' + CryptoManager.generate_hex_string()
        send_request = {'mode': 'send', 'connection': '', 'payload': payload}

        # Everything on first - and binary transfer encoding, so the payload's own bytes
        # are what travels whenever no layer hides them.
        loopback = _new_loopback(page, zato_dashboard, channel_party, sender_party, 'wire', {
            'sign': True,
            'encrypt': True,
            'compress': True,
            'content_transfer_encoding': 'binary',
        })
        send_request['connection'] = loopback.sender_name

        try:

            # With encryption on, the outermost layer is CMS EnvelopedData
            # and the payload is nowhere to be seen in the clear ..
            def _is_encrypted(reply:'anydict') -> 'bool':
                if not _is_reply_ok(reply):
                    return False
                out = _Enveloped_Data_OID in _wire_body(reply)[:_OID_Search_Window]
                return out

            reply = _invoke_until(page, base_url, send_request, _is_encrypted)
            assert payload.encode('utf-8') not in _wire_body(reply)

            # .. with encryption and compression off, the wire is multipart/signed
            # and the payload rides in it in the clear, next to its signature ..
            _edit_sender(page, base_url, loopback, {'encrypt': False, 'compress': False})

            def _is_signed_only(reply:'anydict') -> 'bool':
                if not _is_reply_ok(reply):
                    return False
                body = _wire_body(reply)
                if _Enveloped_Data_OID in body[:_OID_Search_Window]:
                    return False
                out = b'pkcs7-signature' in body
                return out

            reply = _invoke_until(page, base_url, send_request, _is_signed_only)
            assert payload.encode('utf-8') in _wire_body(reply)

            # .. and with signing off too, the wire is the bare MIME entity -
            # no signature part and no CMS layer anywhere.
            _edit_sender(page, base_url, loopback, {'sign': False})

            def _is_plain(reply:'anydict') -> 'bool':
                if not _is_reply_ok(reply):
                    return False
                body = _wire_body(reply)
                if b'pkcs7-signature' in body:
                    return False
                out = payload.encode('utf-8') in body
                return out

            reply = _invoke_until(page, base_url, send_request, _is_plain)
            assert _Enveloped_Data_OID not in _wire_body(reply)[:_OID_Search_Window]

        finally:
            _delete_loopback(page, loopback)

# ################################################################################################################################
# ################################################################################################################################

class TestAS2LiveTamperedMessage:
    """ The error path of 13.4.10 - a message whose signed content was corrupted after
    signing reaches the channel over the real wire and the channel answers with
    the integrity-check-failed MDN.
    """

    @pytest.mark.expect_log_errors(*_AS2_Log_Patterns)
    def test_tampered_message_gets_an_integrity_failure_mdn(
        self, logged_in_page:'Page', zato_dashboard:'anydict', original_keystore:'any_') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        _wait_for_invoker_service(page, base_url)

        channel_party = new_party('as2-live-tamper-channel')
        sender_party = new_party('as2-live-tamper-sender')

        _set_channel_keystore(page, base_url, channel_party)

        # Signed but not encrypted, with binary transfer encoding - so the tampering
        # can flip the payload's own bytes underneath the signature.
        loopback = _new_loopback(page, zato_dashboard, channel_party, sender_party, 'tamper', {
            'sign': True,
            'encrypt': False,
            'compress': False,
            'content_transfer_encoding': 'binary',
        })

        try:

            # A clean send first, so the pair is known to have propagated -
            # whatever the tampered delivery gets back is then about the tampering only.
            clean_request = {'mode': 'send', 'connection': loopback.sender_name, 'payload': 'CLEAN-PROBE'}
            _ = _invoke_until(page, base_url, clean_request, _is_reply_ok)

            # The tampered delivery - the signature stays as it is
            # while the token in the signed content changes underneath it.
            reply = invoke_service_in_ide(page, {
                'mode': 'send-tampered',
                'connection': loopback.sender_name,
                'payload': 'The document carries the TOKEN-BEFORE marker',
                'token': 'TOKEN-BEFORE',
                'replacement': 'TOKEN-CHANGED',
            })

            # The channel answered the POST itself - with an MDN that reports
            # the integrity failure instead of clean processing.
            assert 'error' not in reply, f'Expected an MDN reply, got: {reply}'
            assert reply['http_status'] == 200, f'Expected the MDN over HTTP 200, got: {reply}'
            assert 'integrity-check-failed' in reply['mdn_body'], f'Expected an integrity failure, got: {reply}'

        finally:
            _delete_loopback(page, loopback)

# ################################################################################################################################
# ################################################################################################################################
