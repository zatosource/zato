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
from zato.server.service.internal.security.wss import has_x509_operation

# ################################################################################################################################
# ################################################################################################################################

_peer_certificate = '/tmp/zato-test-peer.pem'

# ################################################################################################################################
# ################################################################################################################################

def _make_input(**kwargs) -> 'Bunch':
    """ Builds the shape a Create or Edit service sees as its input.
    """
    out = Bunch()
    out.name = 'test.wss.definition'

    for key, value in kwargs.items():
        out[key] = value

    return out

# ################################################################################################################################
# ################################################################################################################################

class HasX509OperationTestCase(TestCase):
    """ Whether an X.509 definition asks for anything at all.

    Signing and encryption are the two things the mode has, so a definition that asks for neither
    leaves an outgoing message exactly as it was and states no requirement for an incoming one to
    meet. The answer is the same in both directions, which is why saving such a definition is
    refused rather than warned about.
    """

# ################################################################################################################################

    def test_x509_with_neither_operation(self) -> 'None':
        input = _make_input(mode=Mode.X509, sign=False, encrypt=False)

        self.assertFalse(has_x509_operation(input))

# ################################################################################################################################

    def test_x509_with_neither_flag_present(self) -> 'None':
        # Both flags are optional, so a definition arriving from an enmasse YAML file that never
        # mentioned them carries no such keys.
        input = _make_input(mode=Mode.X509)

        self.assertFalse(has_x509_operation(input))

# ################################################################################################################################

    def test_x509_signing_only(self) -> 'None':
        input = _make_input(mode=Mode.X509, sign=True, encrypt=False, peer_certificate=_peer_certificate)

        self.assertTrue(has_x509_operation(input))

# ################################################################################################################################

    def test_x509_encrypting_only(self) -> 'None':
        input = _make_input(mode=Mode.X509, sign=False, encrypt=True)

        self.assertTrue(has_x509_operation(input))

# ################################################################################################################################

    def test_x509_signing_and_encrypting(self) -> 'None':
        input = _make_input(mode=Mode.X509, sign=True, encrypt=True, peer_certificate=_peer_certificate)

        self.assertTrue(has_x509_operation(input))

# ################################################################################################################################

    def test_username_token_needs_neither(self) -> 'None':
        # A UsernameToken carries a password of its own, so the two flags do not apply to it.
        input = _make_input(mode=Mode.UsernameToken, sign=False, encrypt=False)

        self.assertTrue(has_x509_operation(input))

# ################################################################################################################################

    def test_saml_is_left_to_its_own_rules(self) -> 'None':
        # A SAML definition has an assertion to carry, and whether it signs one is checked where
        # the assertion itself is.
        input = _make_input(mode=Mode.SAML, issuer='urn:idp:example', sign=False, encrypt=False)

        self.assertTrue(has_x509_operation(input))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
