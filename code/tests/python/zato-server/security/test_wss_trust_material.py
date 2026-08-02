# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.ext.bunch import Bunch
from zato.common.soap.security.wss import Mode
from zato.server.service.internal.security.wss import has_trust_material

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_signing_key = '/tmp/zato-test-signing-key.pem'
_signing_chain = '/tmp/zato-test-signing-chain.pem'
_peer_certificate = '/tmp/zato-test-peer.pem'
_trust_anchors = '/tmp/zato-test-anchors.pem'

# ################################################################################################################################
# ################################################################################################################################

def _make_input(**kwargs:'any_') -> 'Bunch':
    """ Builds the shape a Create or Edit service sees as its input.
    """
    out = Bunch()
    out.name = 'test.wss.definition'

    for key, value in kwargs.items():
        out[key] = value

    return out

# ################################################################################################################################
# ################################################################################################################################

class HasTrustMaterialTestCase(TestCase):
    """ Whether a WS-Security definition could verify an incoming signature at all.

    The signer's certificate travels inside the message being verified, so a definition with
    verification enabled and neither trust anchors nor a pinned peer certificate has nothing to
    check it against, and every signed message reaching a channel that uses it will be refused. The
    check is what lets the operator hear about that when saving rather than in production.
    """

# ################################################################################################################################

    def test_x509_signing_without_trust_material(self) -> 'None':
        input = _make_input(mode=Mode.X509, sign=True, signing_key=_signing_key,
            signing_certificate_chain=_signing_chain)

        self.assertFalse(has_trust_material(input))

# ################################################################################################################################

    def test_x509_signing_with_trust_anchors(self) -> 'None':
        input = _make_input(mode=Mode.X509, sign=True, trust_anchors=_trust_anchors)

        self.assertTrue(has_trust_material(input))

# ################################################################################################################################

    def test_x509_signing_with_a_pinned_certificate(self) -> 'None':
        input = _make_input(mode=Mode.X509, sign=True, peer_certificate=_peer_certificate)

        self.assertTrue(has_trust_material(input))

# ################################################################################################################################

    def test_x509_encrypting_only_needs_nothing(self) -> 'None':
        # An encrypt-only definition verifies no signature, so it has nothing to establish trust
        # for and must not be flagged for lacking the means to do it.
        input = _make_input(mode=Mode.X509, sign=False, encrypt=True)

        self.assertTrue(has_trust_material(input))

# ################################################################################################################################

    def test_username_token_needs_nothing(self) -> 'None':
        # UsernameToken carries a password, not a signature, so trust material does not apply.
        input = _make_input(mode=Mode.UsernameToken)

        self.assertTrue(has_trust_material(input))

# ################################################################################################################################

    def test_saml_without_trust_material(self) -> 'None':
        # A SAML assertion has to be signed by its issuer, and the issuer's certificate arrives
        # with the assertion, so a receiving definition needs something to chain it to.
        input = _make_input(mode=Mode.SAML, issuer='urn:idp:example')

        self.assertFalse(has_trust_material(input))

# ################################################################################################################################

    def test_saml_with_trust_anchors(self) -> 'None':
        input = _make_input(mode=Mode.SAML, issuer='urn:idp:example', trust_anchors=_trust_anchors)

        self.assertTrue(has_trust_material(input))

# ################################################################################################################################

    def test_an_outgoing_only_definition_is_still_flagged(self) -> 'None':
        # This is why the finding is a warning at save time rather than a refusal. One definition
        # serves both directions - the same sign flag means "sign what we send" on an outgoing
        # connection and "verify what we receive" on a channel - so a signing-only outgoing
        # definition legitimately has no trust material, and refusing it would break a correct
        # configuration. The hard refusal happens at request time, where the direction is known.
        input = _make_input(mode=Mode.X509, sign=True, signing_key=_signing_key,
            signing_certificate_chain=_signing_chain)

        self.assertFalse(has_trust_material(input))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
