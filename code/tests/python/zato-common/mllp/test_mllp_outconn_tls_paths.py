# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from zato.common.api import GENERIC
from zato.common.exception import BadRequest
from zato.common.ext.bunch import Bunch
from zato.common.hl7.exception import HL7Exception
from zato.common.hl7.mllp.tls import validate_client_paths
from zato.server.service.internal.generic.connection import hook, on_mllp_outgoing_create_edit

# ################################################################################################################################
# ################################################################################################################################

_ca_path   = '/etc/zato/tls/receiving-system-ca.pem'
_cert_path = '/etc/zato/tls/sending-system-cert.pem'
_key_path  = '/etc/zato/tls/sending-system-key.pem'

# ################################################################################################################################
# ################################################################################################################################

class _Service:
    """ What the hook reads of the service that runs it.
    """
    cid = 'test-cid'

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingTLSPaths:

    def test_the_hook_is_registered_for_outgoing_mllp(self) -> 'None':
        assert hook[GENERIC.CONNECTION.TYPE.OUTCONN_HL7_MLLP] is on_mllp_outgoing_create_edit

# ################################################################################################################################

    def test_a_ca_bundle_alone_is_accepted(self) -> 'None':
        validate_client_paths({'tls_ca_path': _ca_path, 'tls_cert_path': '', 'tls_key_path': ''})

# ################################################################################################################################

    def test_no_paths_at_all_are_accepted(self) -> 'None':
        validate_client_paths({})

# ################################################################################################################################

    def test_a_client_certificate_with_a_ca_bundle_is_accepted(self) -> 'None':
        validate_client_paths({'tls_ca_path': _ca_path, 'tls_cert_path': _cert_path, 'tls_key_path': _key_path})

# ################################################################################################################################

    def test_a_client_certificate_without_a_ca_bundle_is_refused(self) -> 'None':
        with pytest.raises(HL7Exception) as context:
            validate_client_paths({'tls_ca_path': '', 'tls_cert_path': _cert_path, 'tls_key_path': _key_path})

        message = str(context.value)
        assert 'client certificate' in message
        assert 'CA bundle' in message

# ################################################################################################################################

    def test_a_client_certificate_with_no_ca_bundle_given_is_refused(self) -> 'None':
        with pytest.raises(HL7Exception):
            validate_client_paths({'tls_cert_path': _cert_path})

# ################################################################################################################################

    def test_the_hook_refuses_a_save_with_a_client_certificate_and_no_ca_bundle(self) -> 'None':
        data = Bunch(name='outgoing.mllp.mutual', tls_ca_path='', tls_cert_path=_cert_path, tls_key_path=_key_path)

        with pytest.raises(BadRequest) as context:
            on_mllp_outgoing_create_edit(_Service(), data, None, None)

        message = str(context.value.msg)

        assert context.value.cid == _Service.cid
        assert 'client certificate' in message

# ################################################################################################################################

    def test_the_hook_accepts_a_save_with_a_client_certificate_and_a_ca_bundle(self) -> 'None':
        data = Bunch(name='outgoing.mllp.mutual', tls_ca_path=_ca_path, tls_cert_path=_cert_path, tls_key_path=_key_path)

        on_mllp_outgoing_create_edit(_Service(), data, None, None)

# ################################################################################################################################
# ################################################################################################################################
