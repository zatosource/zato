# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from threading import RLock
from unittest import main, TestCase
from unittest.mock import MagicMock, Mock

# Zato
from zato.server.service.internal.hot_deploy import Create

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strlist, stranydict
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Cert_Path = '/opt/hot-deploy/ssl/outgoing/client-cert.pem'
    Key_Path  = '/opt/hot-deploy/ssl/outgoing/client-key.pem'
    CA_Path   = '/opt/hot-deploy/ssl/outgoing/ca.pem'
    Other_Path = '/opt/hot-deploy/ssl/outgoing/other/client-cert.pem'

# ################################################################################################################################
# ################################################################################################################################

class _ConfigDict:
    """ The part of a config store's dictionary of outgoing connections that the reload method reads.
    """
    def __init__(self, items:'anydict') -> 'None':
        self._items = items

    def copy_keys(self) -> 'strlist':
        out = list(self._items)
        return out

    def __getitem__(self, name:'str') -> 'anydict':
        out = self._items[name]
        return out

# ################################################################################################################################
# ################################################################################################################################

def _get_wrapper(config:'stranydict') -> 'Mock':
    """ Builds an outgoing connection's wrapper that records whether its TLS material was reloaded.
    """
    out = Mock()
    out.config = {
        'tls_client_cert': None,
        'tls_client_key': None,
    }
    out.config.update(config)
    return out

# ################################################################################################################################

def _get_service(rest:'anydict', soap:'anydict') -> 'Create':
    """ Builds the hot-deploy service with a config store that holds the given REST and SOAP wrappers.
    """
    rest_items = {}
    soap_items = {}

    for name, wrapper in rest.items():
        rest_items[name] = {'conn': wrapper}

    for name, wrapper in soap.items():
        soap_items[name] = {'conn': wrapper}

    service = Create.__new__(Create)
    service.logger = logging.getLogger(__name__)

    service.server = MagicMock()
    service.server.config_manager.update_lock = RLock()
    service.server.config_manager.config_store.out_plain_http = _ConfigDict(rest_items)
    service.server.config_manager.config_store.out_soap = _ConfigDict(soap_items)

    return service

# ################################################################################################################################
# ################################################################################################################################

class TLSMaterialReloadTestCase(TestCase):
    """ Tests which outgoing connections a changed certificate, key or CA file refreshes.
    """

    def test_rest_mtls_certificate(self) -> 'None':
        wrapper = _get_wrapper({'tls_client_cert': ModuleCtx.Cert_Path, 'tls_client_key': ModuleCtx.Key_Path})
        service = _get_service({'my.rest': wrapper}, {})

        service._reload_tls_material(ModuleCtx.Cert_Path)

        wrapper.reload_tls_material.assert_called_once_with()

# ################################################################################################################################

    def test_rest_mtls_key(self) -> 'None':
        wrapper = _get_wrapper({'tls_client_cert': ModuleCtx.Cert_Path, 'tls_client_key': ModuleCtx.Key_Path})
        service = _get_service({'my.rest': wrapper}, {})

        service._reload_tls_material(ModuleCtx.Key_Path)

        wrapper.reload_tls_material.assert_called_once_with()

# ################################################################################################################################

    def test_rest_mtls_ca_certs(self) -> 'None':
        wrapper = _get_wrapper({'tls_client_cert': ModuleCtx.Cert_Path, 'ca_certs_path': ModuleCtx.CA_Path})
        service = _get_service({'my.rest': wrapper}, {})

        service._reload_tls_material(ModuleCtx.CA_Path)

        wrapper.reload_tls_material.assert_called_once_with()

# ################################################################################################################################

    def test_soap_per_connection_combined_pem(self) -> 'None':

        # A single file holds both the certificate and its key, so the key field is empty
        wrapper = _get_wrapper({'tls_client_cert': ModuleCtx.Cert_Path, 'tls_client_key': ''})
        service = _get_service({}, {'my.soap': wrapper})

        service._reload_tls_material(ModuleCtx.Cert_Path)

        wrapper.reload_tls_material.assert_called_once_with()

# ################################################################################################################################

    def test_soap_per_connection_separate_key(self) -> 'None':
        wrapper = _get_wrapper({'tls_client_cert': ModuleCtx.Cert_Path, 'tls_client_key': ModuleCtx.Key_Path})
        service = _get_service({}, {'my.soap': wrapper})

        service._reload_tls_material(ModuleCtx.Key_Path)

        wrapper.reload_tls_material.assert_called_once_with()

# ################################################################################################################################

    def test_soap_mtls_ca_certs(self) -> 'None':
        wrapper = _get_wrapper({'tls_client_cert': ModuleCtx.Cert_Path, 'ca_certs_path': ModuleCtx.CA_Path})
        service = _get_service({}, {'my.soap': wrapper})

        service._reload_tls_material(ModuleCtx.CA_Path)

        wrapper.reload_tls_material.assert_called_once_with()

# ################################################################################################################################

    def test_paths_are_compared_after_normalization(self) -> 'None':

        # The connection names the file through a redundant separator and a parent directory
        configured_path = '/opt/hot-deploy/ssl//outgoing/other/../client-cert.pem'

        wrapper = _get_wrapper({'tls_client_cert': configured_path})
        service = _get_service({'my.rest': wrapper}, {})

        service._reload_tls_material(ModuleCtx.Cert_Path)

        wrapper.reload_tls_material.assert_called_once_with()

# ################################################################################################################################

    def test_connections_with_other_files_are_not_reloaded(self) -> 'None':
        matching_rest = _get_wrapper({'tls_client_cert': ModuleCtx.Cert_Path})
        matching_soap = _get_wrapper({'tls_client_cert': ModuleCtx.Cert_Path})

        other_rest = _get_wrapper({'tls_client_cert': ModuleCtx.Other_Path})
        other_soap = _get_wrapper({'tls_client_cert': ModuleCtx.Other_Path, 'ca_certs_path': ModuleCtx.CA_Path})
        no_tls = _get_wrapper({})

        rest = {'my.rest': matching_rest, 'other.rest': other_rest, 'no.tls': no_tls}
        soap = {'my.soap': matching_soap, 'other.soap': other_soap}

        service = _get_service(rest, soap)
        service._reload_tls_material(ModuleCtx.Cert_Path)

        matching_rest.reload_tls_material.assert_called_once_with()
        matching_soap.reload_tls_material.assert_called_once_with()

        other_rest.reload_tls_material.assert_not_called()
        other_soap.reload_tls_material.assert_not_called()
        no_tls.reload_tls_material.assert_not_called()

# ################################################################################################################################

    def test_file_no_connection_reads(self) -> 'None':
        wrapper = _get_wrapper({'tls_client_cert': ModuleCtx.Cert_Path})
        service = _get_service({'my.rest': wrapper}, {})

        # HAProxy's own certificate is in the same directory and no outgoing connection reads it
        service._reload_tls_material('/opt/hot-deploy/ssl/zato.pem')

        wrapper.reload_tls_material.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
