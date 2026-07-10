# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding

# Zato
from zato.common.as2.rotation import complete_rotation, needs_rotation_completion

# ################################################################################################################################
# ################################################################################################################################

# A fixed moment all the checks run against, so the tests never depend on the clock.
_now = datetime(2026, 7, 10, 12, 0, 0, tzinfo=timezone.utc)

# Activation dates relative to the fixed moment above, with the grace window being one day.
_date_past_grace   = '2026-07-08'
_date_within_grace = '2026-07-10'
_date_future       = '2026-08-01'

# ################################################################################################################################
# ################################################################################################################################

def _certificate_to_pem(certificate):
    out = certificate.public_bytes(Encoding.PEM).decode('ascii')
    return out

# ################################################################################################################################

def _rotation_config(current_cert='', next_cert='', next_cert_from=''):
    """ The certificate rotation fields of one Dashboard-managed AS2 connection.
    """
    out = {
        'as2_partner_cert': current_cert,
        'as2_partner_next_cert': next_cert,
        'as2_partner_next_cert_from': next_cert_from,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestNeedsRotationCompletion:

    def test_date_past_the_grace_window_completes(self, make_rotated_pair):
        next_pem = _certificate_to_pem(make_rotated_pair('partnercorp-next').certificate)

        config = _rotation_config(next_cert=next_pem, next_cert_from=_date_past_grace)

        assert needs_rotation_completion(config, _now)

    def test_date_passed_but_within_the_grace_window_does_not_complete(self, make_rotated_pair):
        next_pem = _certificate_to_pem(make_rotated_pair('partnercorp-next').certificate)

        config = _rotation_config(next_cert=next_pem, next_cert_from=_date_within_grace)

        assert not needs_rotation_completion(config, _now)

    def test_future_date_does_not_complete(self, make_rotated_pair):
        next_pem = _certificate_to_pem(make_rotated_pair('partnercorp-next').certificate)

        config = _rotation_config(next_cert=next_pem, next_cert_from=_date_future)

        assert not needs_rotation_completion(config, _now)

    def test_next_certificate_without_a_date_never_completes(self, make_rotated_pair):
        """ A next certificate with no date is an extra accepted certificate,
        not a scheduled cutover, so it is never promoted automatically.
        """
        next_pem = _certificate_to_pem(make_rotated_pair('partnercorp-next').certificate)

        config = _rotation_config(next_cert=next_pem)

        assert not needs_rotation_completion(config, _now)

    def test_no_next_certificate_never_completes(self, make_rotated_pair):
        current_pem = _certificate_to_pem(make_rotated_pair('partnercorp-current').certificate)

        config = _rotation_config(current_cert=current_pem, next_cert_from=_date_past_grace)

        assert not needs_rotation_completion(config, _now)

# ################################################################################################################################
# ################################################################################################################################

class TestCompleteRotation:

    def test_next_certificate_becomes_the_current_one_verbatim(self, make_rotated_pair):
        current_pem = _certificate_to_pem(make_rotated_pair('partnercorp-current').certificate)
        next_pem = _certificate_to_pem(make_rotated_pair('partnercorp-next').certificate)

        config = _rotation_config(current_cert=current_pem, next_cert=next_pem, next_cert_from=_date_past_grace)

        complete_rotation(config)

        assert config['as2_partner_cert'] == next_pem
        assert config['as2_partner_next_cert'] == ''
        assert config['as2_partner_next_cert_from'] == ''

    def test_a_multi_certificate_pem_moves_verbatim(self, make_rotated_pair):
        """ A next field holding several certificates, e.g. a chain, is promoted as one string,
        with nothing reordered, reformatted or dropped.
        """
        current_pem = _certificate_to_pem(make_rotated_pair('partnercorp-current').certificate)

        first_pem = _certificate_to_pem(make_rotated_pair('partnercorp-next').certificate)
        second_pem = _certificate_to_pem(make_rotated_pair('partnercorp-next-issuer').certificate)
        next_pem = first_pem + second_pem

        config = _rotation_config(current_cert=current_pem, next_cert=next_pem, next_cert_from=_date_past_grace)

        complete_rotation(config)

        assert config['as2_partner_cert'] == next_pem
        assert config['as2_partner_next_cert'] == ''
        assert config['as2_partner_next_cert_from'] == ''

# ################################################################################################################################
# ################################################################################################################################
