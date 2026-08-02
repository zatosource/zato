# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# lxml
from lxml import etree

# pytest
import pytest

# Zato
from zato.common.api import AS4
from zato.common.as4.common import AS4Exception, EbMSError, NS
from zato.common.as4.config import build_keystore, build_pmode
from zato.common.as4.mpc import count_waiting, queue_message
from zato.common.as4.outbound import new_part
from zato.common.util.xml_.constants import TokenType
from zato.common.util.xml_.core import qname

from .test_audit import audit_db
from .test_security import _new_holder_of_key_assertion
from .test_server_connection import _channel_config, _connect, _make_channel, _make_wrapper, _outgoing_config, \
    Payload, Test_CID
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    any_ = any_
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# Keeps the imported fixture reachable under the name pytest resolves it by.
audit_db = audit_db

# ################################################################################################################################
# ################################################################################################################################

# The credentials the two ends of the test exchanges are configured with.
Test_Username = 'as4-user'
Test_Password = 'as4-password'

# The channel the pull tests exchange a message over.
Test_MPC = 'urn:test:mpc:credentials'

# The business information the pull tests queue their message under, which is what the loopback
# channel and connection are configured for.
_Service = 'urn:test:service'
_Action = 'SubmitInvoice'

# ################################################################################################################################
# ################################################################################################################################

def _with_credentials(config:'any_', username:'str'=Test_Username, password:'str'=Test_Password) -> 'any_':
    """ Puts the credentials on one connection or channel configuration, the way the Dashboard
    saves them. The P-Mode is built when the object is first used, so this is in time for it.
    """
    config['as4_username'] = username
    config['as4_password'] = password

    return config

# ################################################################################################################################

def _find_token(body:'bytes') -> 'any_':
    """ Returns the wsse:UsernameToken of a message as it went over the wire, or None for a message
    that carries none. The body is a MIME envelope, so the XML part of it is what is parsed.
    """
    start = body.index(b'<?xml')
    end = body.index(b'--', start)

    envelope = etree.fromstring(body[start:end])
    security = cast_('any_', envelope.find(f'.//{qname(NS.WSSE, "Security")}'))

    out = security.find(qname(NS.WSSE, 'UsernameToken'))
    return out

# ################################################################################################################################

def _queue_for_pull() -> 'str':
    """ Queues one message on the channel the pull tests read from.
    """
    part = new_part(Payload)

    out = queue_message(Test_MPC, 'party-b', 'party-a', _Service, _Action, [part])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestUsernameTokenConfig:
    """ How the credentials of a connection reach the P-Mode that uses them.
    """

    def test_a_connection_without_credentials_asks_for_no_token(self, rsa_parties:'TestParties') -> 'None':
        wrapper = _make_wrapper(rsa_parties, 'edelivery1')
        pmode = wrapper._get_pmode()

        assert pmode.security.username_token_username == ''
        assert pmode.security.username_token_password == ''

# ################################################################################################################################

    def test_the_configured_credentials_reach_the_pmode(self, rsa_parties:'TestParties') -> 'None':
        wrapper = _make_wrapper(rsa_parties, 'edelivery1')
        _ = _with_credentials(wrapper.config)

        pmode = wrapper._get_pmode()

        assert pmode.security.username_token_username == Test_Username
        assert pmode.security.username_token_password == Test_Password

# ################################################################################################################################

    def test_every_pmode_of_a_channel_asks_for_the_same_credentials(self, rsa_parties:'TestParties') -> 'None':
        channel = _make_channel(rsa_parties, 'edelivery1')
        _ = _with_credentials(channel.config)

        channel.config['as4_extra_pmodes'] = 'urn:test:other|OtherAction'

        pmodes = channel._get_pmodes()
        assert len(pmodes) == 2

        for pmode in pmodes:
            assert pmode.security.username_token_username == Test_Username
            assert pmode.security.username_token_password == Test_Password

# ################################################################################################################################
# ################################################################################################################################

class TestUsernameTokenOnPush:
    """ The credentials a pushed message carries and what the receiving channel makes of them.
    """

    def test_a_message_carries_the_configured_token(self, rsa_parties:'TestParties') -> 'None':
        wrapper = _make_wrapper(rsa_parties, 'edelivery1')
        channel = _make_channel(rsa_parties, 'edelivery1')

        _ = _with_credentials(wrapper.config)
        _ = _with_credentials(channel.config)
        _connect(wrapper, channel)

        result = wrapper.send(Test_CID, Payload)
        assert result.is_ok

        token = _find_token(result.request_body)
        assert token is not None

        username = token.find(qname(NS.WSSE, 'Username'))
        assert username.text == Test_Username

# ################################################################################################################################

    def test_a_connection_without_credentials_sends_no_token(self, rsa_parties:'TestParties') -> 'None':
        wrapper = _make_wrapper(rsa_parties, 'edelivery1')
        channel = _make_channel(rsa_parties, 'edelivery1')
        _connect(wrapper, channel)

        result = wrapper.send(Test_CID, Payload)

        assert result.is_ok
        assert _find_token(result.request_body) is None

# ################################################################################################################################

    def test_a_channel_asking_for_no_token_accepts_a_message_with_one(self, rsa_parties:'TestParties') -> 'None':
        wrapper = _make_wrapper(rsa_parties, 'edelivery1')
        channel = _make_channel(rsa_parties, 'edelivery1')

        _ = _with_credentials(wrapper.config)
        _connect(wrapper, channel)

        result = wrapper.send(Test_CID, Payload)
        assert result.is_ok

# ################################################################################################################################

    def test_a_message_without_the_token_a_channel_asks_for_is_refused(self, rsa_parties:'TestParties') -> 'None':
        wrapper = _make_wrapper(rsa_parties, 'edelivery1')
        channel = _make_channel(rsa_parties, 'edelivery1')

        _ = _with_credentials(channel.config)
        _connect(wrapper, channel)

        with pytest.raises(AS4Exception) as exception_info:
            _ = wrapper.send(Test_CID, Payload)

        assert EbMSError.Failed_Authentication in str(exception_info.value)

# ################################################################################################################################

    def test_a_message_with_the_wrong_password_is_refused(self, rsa_parties:'TestParties') -> 'None':
        wrapper = _make_wrapper(rsa_parties, 'edelivery1')
        channel = _make_channel(rsa_parties, 'edelivery1')

        _ = _with_credentials(wrapper.config, password='not-the-password')
        _ = _with_credentials(channel.config)
        _connect(wrapper, channel)

        with pytest.raises(AS4Exception) as exception_info:
            _ = wrapper.send(Test_CID, Payload)

        assert EbMSError.Failed_Authentication in str(exception_info.value)

# ################################################################################################################################

    def test_a_message_with_the_wrong_username_is_refused(self, rsa_parties:'TestParties') -> 'None':
        wrapper = _make_wrapper(rsa_parties, 'edelivery1')
        channel = _make_channel(rsa_parties, 'edelivery1')

        _ = _with_credentials(wrapper.config, username='someone-else')
        _ = _with_credentials(channel.config)
        _connect(wrapper, channel)

        with pytest.raises(AS4Exception) as exception_info:
            _ = wrapper.send(Test_CID, Payload)

        assert EbMSError.Failed_Authentication in str(exception_info.value)

# ################################################################################################################################

    def test_a_refused_message_is_not_delivered(self, rsa_parties:'TestParties') -> 'None':
        wrapper = _make_wrapper(rsa_parties, 'edelivery1')
        channel = _make_channel(rsa_parties, 'edelivery1')

        _ = _with_credentials(channel.config)
        _connect(wrapper, channel)

        with pytest.raises(AS4Exception):
            _ = wrapper.send(Test_CID, Payload)

        # Authorization is checked before the payload goes anywhere, so nothing was published.
        assert channel.server.pubsub_backend.published == []

# ################################################################################################################################
# ################################################################################################################################

class TestUsernameTokenOnPull:
    """ The same credentials on a pull request, which is what the networks asking for them
    authorize a pull with.
    """

    def test_a_pull_request_carrying_the_credentials_is_served(
        self,
        audit_db:'any_',
        rsa_parties:'TestParties',
        ) -> 'None':
        message_id = _queue_for_pull()

        wrapper = _make_wrapper(rsa_parties, 'edelivery1', mpc=Test_MPC)
        channel = _make_channel(rsa_parties, 'edelivery1', mpc=Test_MPC)

        _ = _with_credentials(wrapper.config)
        _ = _with_credentials(channel.config)
        _connect(wrapper, channel)

        result = wrapper.pull(Test_CID)

        assert result.has_message
        assert result.user_message.message_id == message_id

# ################################################################################################################################

    def test_a_pull_request_without_the_credentials_is_refused(
        self,
        audit_db:'any_',
        rsa_parties:'TestParties',
        ) -> 'None':
        _ = _queue_for_pull()

        wrapper = _make_wrapper(rsa_parties, 'edelivery1', mpc=Test_MPC)
        channel = _make_channel(rsa_parties, 'edelivery1', mpc=Test_MPC)

        _ = _with_credentials(channel.config)
        _connect(wrapper, channel)

        with pytest.raises(AS4Exception) as exception_info:
            _ = wrapper.pull(Test_CID)

        assert EbMSError.Failed_Authentication in str(exception_info.value)

        # An unauthorized request hands nothing over, so the message is still waiting.
        assert count_waiting(Test_MPC) == 1

# ################################################################################################################################

    def test_a_pull_request_with_the_wrong_password_is_refused(
        self,
        audit_db:'any_',
        rsa_parties:'TestParties',
        ) -> 'None':
        _ = _queue_for_pull()

        wrapper = _make_wrapper(rsa_parties, 'edelivery1', mpc=Test_MPC)
        channel = _make_channel(rsa_parties, 'edelivery1', mpc=Test_MPC)

        _ = _with_credentials(wrapper.config, password='not-the-password')
        _ = _with_credentials(channel.config)
        _connect(wrapper, channel)

        with pytest.raises(AS4Exception) as exception_info:
            _ = wrapper.pull(Test_CID)

        assert EbMSError.Failed_Authentication in str(exception_info.value)
        assert count_waiting(Test_MPC) == 1

# ################################################################################################################################
# ################################################################################################################################

class TestTokenTypeConfig:
    """ Which token type a connection sends its signing certificate under.
    """

    def test_a_connection_without_one_keeps_the_profile_choice(self, rsa_parties:'TestParties') -> 'None':
        config = _outgoing_config(rsa_parties, 'ics2')
        pmode = build_pmode(config)

        # ICS2 requires the whole chain, which is what its preset says and what stays in place.
        assert pmode.security.token_type == TokenType.PKIPath

# ################################################################################################################################

    def test_a_single_certificate_can_be_selected(self, rsa_parties:'TestParties') -> 'None':
        config = _outgoing_config(rsa_parties, 'ics2')
        config['as4_token_type'] = AS4.TokenType.X509v3

        pmode = build_pmode(config)
        assert pmode.security.token_type == TokenType.X509v3

# ################################################################################################################################

    def test_a_certificate_chain_can_be_selected(self, rsa_parties:'TestParties') -> 'None':
        config = _outgoing_config(rsa_parties, 'edelivery1')
        config['as4_token_type'] = AS4.TokenType.PKIPath

        pmode = build_pmode(config)
        assert pmode.security.token_type == TokenType.PKIPath

# ################################################################################################################################

    def test_a_saml_assertion_can_be_selected(self, rsa_parties:'TestParties') -> 'None':
        assertion = _new_holder_of_key_assertion(rsa_parties.sender.signing_certificate)

        config = _outgoing_config(rsa_parties, 'edelivery1')
        config['as4_token_type'] = AS4.TokenType.SAML20
        config['as4_saml_assertion'] = assertion.decode('utf8')

        pmode = build_pmode(config)
        assert pmode.security.token_type == TokenType.SAML20

# ################################################################################################################################

    def test_selecting_saml_without_an_assertion_is_rejected(self, rsa_parties:'TestParties') -> 'None':
        config = _outgoing_config(rsa_parties, 'edelivery1')
        config['as4_token_type'] = AS4.TokenType.SAML20

        with pytest.raises(AS4Exception) as exception_info:
            _ = build_pmode(config)

        assert 'needs a SAML assertion' in str(exception_info.value)

# ################################################################################################################################
# ################################################################################################################################

class TestSAMLAssertionConfig:
    """ The assertion a security token service issued, as configured on a connection.
    """

    def test_a_connection_without_one_has_no_assertion(self, rsa_parties:'TestParties') -> 'None':
        config = _outgoing_config(rsa_parties, 'edelivery1')
        keystore = build_keystore(config, lambda value: value)

        assert keystore.saml_assertion is None

# ################################################################################################################################

    def test_the_configured_assertion_reaches_the_keystore(self, rsa_parties:'TestParties') -> 'None':
        assertion = _new_holder_of_key_assertion(rsa_parties.sender.signing_certificate)

        config = _outgoing_config(rsa_parties, 'edelivery1')
        config['as4_saml_assertion'] = assertion.decode('utf8')

        keystore = build_keystore(config, lambda value: value)
        assert keystore.saml_assertion == assertion

# ################################################################################################################################

    def test_a_message_keyed_by_the_assertion_is_accepted(self, rsa_parties:'TestParties') -> 'None':
        assertion = _new_holder_of_key_assertion(rsa_parties.sender.signing_certificate)

        wrapper = _make_wrapper(rsa_parties, 'edelivery1')
        wrapper.config['as4_token_type'] = AS4.TokenType.SAML20
        wrapper.config['as4_saml_assertion'] = assertion.decode('utf8')

        channel = _make_channel(rsa_parties, 'edelivery1')
        _connect(wrapper, channel)

        result = wrapper.send(Test_CID, Payload)

        # The receiving side resolved the signer out of the assertion's holder-of-key confirmation
        # and delivered the payload on the strength of it.
        assert result.is_ok

        _, message, _, _ = channel.server.pubsub_backend.published[0]
        assert message['data'] == Payload.decode('utf8')

# ################################################################################################################################

    def test_a_channel_can_be_configured_with_an_assertion_too(self, rsa_parties:'TestParties') -> 'None':
        assertion = _new_holder_of_key_assertion(rsa_parties.receiver.signing_certificate)

        config = _channel_config(rsa_parties, 'edelivery1')
        config['as4_saml_assertion'] = assertion.decode('utf8')
        config['as4_token_type'] = AS4.TokenType.SAML20

        keystore = build_keystore(config, lambda value: value)
        pmode = build_pmode(config)

        assert keystore.saml_assertion == assertion
        assert pmode.security.token_type == TokenType.SAML20

# ################################################################################################################################
# ################################################################################################################################
