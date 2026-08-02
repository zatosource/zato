# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock

# Zato
from zato.common.exception import Unauthorized
from zato.common.soap.common import Content_Type, SOAPVersion
from zato.common.soap.envelope import attach_body, build_envelope, to_bytes
from zato.common.soap.message import SOAPMessage
from zato.common.soap.security.usernametoken import add_username_token
from zato.common.soap.security.wss import Mode
from zato.server.connection.http_soap.channel_soap import parse_soap_request
from zato.server.connection.http_soap.url_data import URLData
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_test_cid = 'zcid-test-0001'
_test_path = '/test/soap'
_test_operation = 'submitSingleMessage'

_ns_cdc = 'urn:cdc:iisb:2011'

_username = 'MYUSER'
_password = 'MYPASS'

# ################################################################################################################################
# ################################################################################################################################

def _make_envelope(username:'str | None'=None, password:'str | None'=None) -> 'bytes':
    """ Builds the wire bytes of a request, optionally carrying a UsernameToken.
    """
    message = SOAPMessage()
    message.namespace = _ns_cdc
    message.facilityID = 'FL0001'

    envelope = build_envelope(SOAPVersion.V12)
    _ = attach_body(envelope, message, _test_operation)

    if username is not None:
        _ = add_username_token(envelope, username, cast_('any_', password))

    out = to_bytes(envelope)
    return out

# ################################################################################################################################

def _username_token_definition() -> 'stranydict':
    """ The config of a channel's UsernameToken definition.
    """
    out = {
        'mode': Mode.UsernameToken,
        'username': _username,
        'password': _password,
    }

    return out

# ################################################################################################################################

def _url_data() -> 'URLData':
    """ A URLData with everything it does not need for WS-Security mocked out. The channel data has
    to be a real list rather than a mock, since it is sorted during construction.
    """
    out = URLData(MagicMock(), channel_data=[])
    return out

# ################################################################################################################################
# ################################################################################################################################

class HandleSecurityWSSTestCase(unittest.TestCase):
    """ Enforcing a channel's WS-Security definition on an incoming envelope.

    Two things are being checked throughout: that the right answer comes back, and that enforcement
    runs against the envelope the channel already parsed rather than a second parse of the same
    bytes - which is what makes a decrypted body visible to the service.
    """

# ################################################################################################################################

    def _enforce(self, body:'bytes', with_context:'bool'=True, enforce_auth:'bool'=True) -> 'anydict':
        """ Runs enforcement the way the dispatcher does and returns the result along with the
        request context, so a test can see what enforcement recorded on it.
        """
        wsgi_environ:'anydict' = {}
        context = None

        if with_context:
            channel_item:'anydict' = {
                'id': 1,
                'name': 'test.soap.channel',
                'soap_version': SOAPVersion.V12,
                'use_mtom': False,
            }
            context = parse_soap_request(_test_cid, body, Content_Type[SOAPVersion.V12], channel_item)
            wsgi_environ['zato.request.soap'] = context

        url_data = _url_data()

        result = url_data._handle_security_wss(_test_cid, _username_token_definition(), _test_path,
            body, wsgi_environ, enforce_auth=enforce_auth)

        out:'anydict' = {'result': result, 'context': context}
        return out

# ################################################################################################################################

    def test_correct_credentials_are_admitted(self) -> 'None':
        body = _make_envelope(_username, _password)

        out = self._enforce(body)

        self.assertTrue(out['result'])

# ################################################################################################################################

    def test_a_wrong_password_is_refused(self) -> 'None':
        body = _make_envelope(_username, 'THE-WRONG-PASSWORD')

        with self.assertRaises(Unauthorized):
            _ = self._enforce(body)

# ################################################################################################################################

    def test_a_wrong_username_is_refused(self) -> 'None':
        body = _make_envelope('SOMEBODY-ELSE', _password)

        with self.assertRaises(Unauthorized):
            _ = self._enforce(body)

# ################################################################################################################################

    def test_a_message_with_no_token_is_refused(self) -> 'None':
        body = _make_envelope()

        with self.assertRaises(Unauthorized):
            _ = self._enforce(body)

# ################################################################################################################################

    def test_the_refusal_carries_no_challenge(self) -> 'None':
        # WS-Security credentials live in the message, so there is no HTTP scheme for a client to
        # retry under and a WWW-Authenticate header would name one that does not apply.
        body = _make_envelope(_username, 'THE-WRONG-PASSWORD')

        with self.assertRaises(Unauthorized) as ctx:
            _ = self._enforce(body)

        self.assertIsNone(ctx.exception.challenge)

# ################################################################################################################################

    def test_without_enforcement_a_failure_is_reported_rather_than_raised(self) -> 'None':
        # This is the path that asks whether a definition would admit a message, which a channel
        # with several definitions uses to try each in turn - so a refusal has to be an answer
        # rather than the end of the request.
        body = _make_envelope(_username, 'THE-WRONG-PASSWORD')

        out = self._enforce(body, enforce_auth=False)

        self.assertFalse(out['result'])

# ################################################################################################################################

    def test_a_body_without_a_context_is_parsed_here(self) -> 'None':
        # A REST channel with a WS-Security definition has no parsed envelope, so enforcement has to
        # parse the body itself rather than assuming the context is there.
        body = _make_envelope(_username, _password)

        out = self._enforce(body, with_context=False)

        self.assertTrue(out['result'])

# ################################################################################################################################

    def test_a_malformed_body_without_a_context_is_not_a_credential_failure(self) -> 'None':
        # Only a security failure is a credential failure. A body that does not parse is a bad
        # request, and reporting it as a 401 would tell the caller its credentials were wrong when
        # the credentials were never read at all.
        with self.assertRaises(Exception) as ctx:
            _ = self._enforce(b'this is not an envelope', with_context=False)

        self.assertNotIsInstance(ctx.exception, Unauthorized)

# ################################################################################################################################

    def test_a_username_token_records_no_signature(self) -> 'None':
        # A UsernameToken carries no signature, so there is nothing for the payload resolution to
        # hold the body against - and recording something here would claim coverage that does not
        # exist.
        body = _make_envelope(_username, _password)

        out = self._enforce(body)

        self.assertIsNone(out['context'].verified_signature)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
