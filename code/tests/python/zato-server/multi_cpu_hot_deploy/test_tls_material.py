# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import unittest
from uuid import uuid4

# local
from certs import build_tls_material, reissue_client_material
from http_test_server import HTTPSTestServer

# Zato
from zato.common.test.conftest_base_multi_cpu import enmasse_import, invoke_on_slot, ModuleCtx as MultiCPUCtx, \
     MultiCPUTestConfig, wait_for_every_slot

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long every slot has to present a certificate, in seconds
    Reload_Deadline = 60.0

    # The address the endpoint listens on and the path the connection invokes
    Host = '127.0.0.1'
    URL_Path = '/multi-cpu/tls-material'

    # The service that invokes the connection
    Invoke_Service = 'test.multi-cpu.outconn-invoke'

# ################################################################################################################################
# ################################################################################################################################

class TestTLSMaterialAcrossWorkers(unittest.TestCase):
    """ A client certificate replaced in the TLS material directory is presented by an outgoing connection
    from every worker.
    """

    def _get_fingerprint(self, endpoint:'HTTPSTestServer', conn_name:'str', slot:'int') -> 'str':
        """ Invokes the connection through the worker of a slot and returns the fingerprint of the certificate
        that the endpoint received, or an empty string if the invocation did not reach the endpoint.
        """
        marker = uuid4().hex
        status, _ = invoke_on_slot(slot, ModuleCtx.Invoke_Service, {'conn_name': conn_name, 'marker': marker})

        out = ''

        if status == MultiCPUCtx.Status_OK:
            for record in endpoint.recorded_requests:
                if record['query'] == {'marker': marker}:
                    out = record['client_cert_fingerprint']

        return out

# ################################################################################################################################

    def _wait_for_fingerprint(self, endpoint:'HTTPSTestServer', conn_name:'str', fingerprint:'str') -> 'None':

        def _presents(slot:'int') -> 'bool':
            out = self._get_fingerprint(endpoint, conn_name, slot) == fingerprint
            return out

        wait_for_every_slot(_presents, f'client certificate {fingerprint}', ModuleCtx.Reload_Deadline)

# ################################################################################################################################

    def test_client_certificate_change(self) -> 'None':
        """ A client certificate, presented by a connection that reads it, and the certificate that replaces it.
        """
        suffix = uuid4().hex[:12]
        conn_name = f'test.multi-cpu.tls-material.{suffix}'

        directory = os.path.join(MultiCPUTestConfig.server_directory, MultiCPUCtx.TLS_Material_Directory, suffix)
        os.makedirs(directory)

        material = build_tls_material(ModuleCtx.Host, directory)

        endpoint = HTTPSTestServer(require_client_cert=True, host=ModuleCtx.Host, tls_material=material)
        endpoint.start()

        try:
            enmasse_import({
                'outgoing_rest': [{
                    'name': conn_name,
                    'host': f'https://{ModuleCtx.Host}:{endpoint.port}',
                    'url_path': ModuleCtx.URL_Path,
                    'data_format': 'json',
                    'timeout': 20,
                    'tls_verify': False,
                    'tls_client_cert': material.client_combined_path,
                }],
            })

            self._wait_for_fingerprint(endpoint, conn_name, material.client_fingerprint)

            # The new certificate is renamed over the current one, which the listener reports to the server
            fingerprint = reissue_client_material(material, needs_rename=True)
            self._wait_for_fingerprint(endpoint, conn_name, fingerprint)

        finally:
            endpoint.stop()

# ################################################################################################################################
# ################################################################################################################################
