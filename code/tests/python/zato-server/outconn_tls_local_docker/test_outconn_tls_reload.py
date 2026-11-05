# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# local
from certs import reissue_client_material
from _outconn_tls import get_log_offset, invoke, LocalContainer, Main_Path, MaterialKind, Other_Path, start_case, \
    stop_case, wait_for_reload

# ################################################################################################################################
# ################################################################################################################################

# Each case is a connection type, how it names its client certificate, and whether the certificate
# is overwritten where it is or renamed into place.
_cases = [
    pytest.param('rest', 'plain_http', MaterialKind.MTLS,     False, id='rest-mtls-in-place'),
    pytest.param('soap', 'soap',       MaterialKind.MTLS,     True,  id='soap-mtls-rename'),
    pytest.param('soap', 'soap',       MaterialKind.Combined, False, id='soap-combined-in-place'),
    pytest.param('soap', 'soap',       MaterialKind.Separate, True,  id='soap-separate-rename'),
]

# ################################################################################################################################
# ################################################################################################################################

class TestOutconnTLSReload:
    """ An outgoing connection presents a client certificate to a live mutual-TLS endpoint, the certificate
    is replaced in the directory mapped into the local container, and the next request presents the new one
    over a new TLS connection, while an unrelated connection keeps the TLS connection it had.
    """

    @pytest.mark.parametrize('conn_type, transport, material_kind, needs_rename', _cases)
    def test_replaced_certificate_is_presented(
        self,
        local_container:'LocalContainer',
        conn_type:'str',
        transport:'str',
        material_kind:'str',
        needs_rename:'bool',
        ) -> 'None':

        case_name = f'{conn_type}-{material_kind}'

        # The material, the endpoint and both connections are in place ..
        run = start_case(local_container, case_name, conn_type, transport, material_kind)

        try:
            initial_fingerprint = run.material.client_fingerprint

            # .. two requests present the initial certificate over the same TLS connection ..
            first = invoke(run, run.main_conn_name, Main_Path)
            second = invoke(run, run.main_conn_name, Main_Path)

            assert first['client_cert_fingerprint'] == initial_fingerprint, first
            assert second['client_cert_fingerprint'] == initial_fingerprint, second
            assert second['client_port'] == first['client_port'], (first, second)

            # .. the unrelated connection opens a TLS connection of its own ..
            other_before = invoke(run, run.other_conn_name, Other_Path)
            assert other_before['client_cert_fingerprint'] == initial_fingerprint, other_before

            # .. the client certificate and key are replaced under the same CA ..
            log_offset = get_log_offset(run)
            new_fingerprint = reissue_client_material(run.material, needs_rename)

            assert new_fingerprint != initial_fingerprint

            # .. the server is told about it ..
            wait_for_reload(run, log_offset)

            # .. the next request presents the new certificate over a new TLS connection ..
            third = invoke(run, run.main_conn_name, Main_Path)

            assert third['client_cert_fingerprint'] == new_fingerprint, third
            assert third['client_port'] != second['client_port'], (second, third)

            # .. and the unrelated connection still uses the TLS connection it had.
            other_after = invoke(run, run.other_conn_name, Other_Path)

            assert other_after['client_cert_fingerprint'] == initial_fingerprint, other_after
            assert other_after['client_port'] == other_before['client_port'], (other_before, other_after)

        finally:
            stop_case(run)

# ################################################################################################################################
# ################################################################################################################################
