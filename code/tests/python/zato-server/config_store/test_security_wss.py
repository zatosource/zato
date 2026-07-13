# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# PyPI
import pytest

# Zato
from zato.common.test.client import AdminClient as ZatoClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anydictnone, anylist
    anydict, anydictnone, anylist = anydict, anydictnone, anylist

# ################################################################################################################################
# ################################################################################################################################

SERVICE = 'zato.security.wss'

# Sample paths to PEM files a definition keeps - stored as opaque attributes, not read at creation time.
_signing_key_path = '/opt/zato/pki/wss-signing-key.pem'
_signing_certificate_chain_path = '/opt/zato/pki/wss-signing-chain.pem'
_decryption_key_path = '/opt/zato/pki/wss-decryption-key.pem'
_peer_certificate_path = '/opt/zato/pki/wss-peer-certificate.pem'
_trust_anchors_path = '/opt/zato/pki/wss-trust-anchors.pem'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'anydict') -> 'ZatoClient':
    base_url = f'http://{zato_server["host"]}:{zato_server["port"]}'

    out = ZatoClient(base_url, zato_server['password'])
    return out

# ################################################################################################################################

def _find_by_name(data:'anylist', name:'str') -> 'anydictnone':
    """ Returns the get-list item of the given name or None if there is no such item.
    """
    for item in data:
        if item['name'] == name:
            out = item
            break
    else:
        out = None

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSecurityWSS:
    created_ids = []

    def test_01_get_list_empty(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        assert isinstance(data, list)

# ################################################################################################################################

    def test_02_create_username_token(self, client:'ZatoClient') -> 'None':
        resp = client.create(f'{SERVICE}.create',
            cluster_id=1,
            name='test-wss-username-token',
            is_active=True,
            username='testwssuser1',
            mode='username_token',
            use_digest=True,
        )
        assert 'id' in resp
        assert resp['name'] == 'test-wss-username-token'
        self.__class__.created_ids.append(resp['id'])

# ################################################################################################################################

    def test_03_username_token_round_trip(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        item = _find_by_name(data, 'test-wss-username-token')

        assert item is not None
        assert item['is_active'] is True
        assert item['username'] == 'testwssuser1'
        assert item['mode'] == 'username_token'
        assert item['use_digest'] is True

# ################################################################################################################################

    def test_04_create_x509(self, client:'ZatoClient') -> 'None':
        resp = client.create(f'{SERVICE}.create',
            cluster_id=1,
            name='test-wss-x509',
            is_active=True,
            username='testwssuser2',
            mode='x509',
            sign=True,
            encrypt=True,
            signing_key=_signing_key_path,
            signing_certificate_chain=_signing_certificate_chain_path,
            decryption_key=_decryption_key_path,
            peer_certificate=_peer_certificate_path,
            trust_anchors=_trust_anchors_path,
        )
        assert 'id' in resp
        self.__class__.created_ids.append(resp['id'])

# ################################################################################################################################

    def test_05_x509_round_trip(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        item = _find_by_name(data, 'test-wss-x509')

        assert item is not None
        assert item['mode'] == 'x509'
        assert item['sign'] is True
        assert item['encrypt'] is True
        assert item['signing_key'] == _signing_key_path
        assert item['signing_certificate_chain'] == _signing_certificate_chain_path
        assert item['decryption_key'] == _decryption_key_path
        assert item['peer_certificate'] == _peer_certificate_path
        assert item['trust_anchors'] == _trust_anchors_path

# ################################################################################################################################

    def test_06_create_saml(self, client:'ZatoClient') -> 'None':
        resp = client.create(f'{SERVICE}.create',
            cluster_id=1,
            name='test-wss-saml',
            is_active=True,
            username='testwssuser3',
            mode='saml',
            issuer='https://idp.example.com/test',
            subject='CN=Test Subject',
            audience='https://api.example.com/test',
            sign=True,
            signing_key=_signing_key_path,
            signing_certificate_chain=_signing_certificate_chain_path,
        )
        assert 'id' in resp
        self.__class__.created_ids.append(resp['id'])

# ################################################################################################################################

    def test_07_saml_round_trip(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        item = _find_by_name(data, 'test-wss-saml')

        assert item is not None
        assert item['mode'] == 'saml'
        assert item['issuer'] == 'https://idp.example.com/test'
        assert item['subject'] == 'CN=Test Subject'
        assert item['audience'] == 'https://api.example.com/test'
        assert item['sign'] is True
        assert item['signing_key'] == _signing_key_path
        assert item['signing_certificate_chain'] == _signing_certificate_chain_path

# ################################################################################################################################

    def test_08_create_inactive(self, client:'ZatoClient') -> 'None':
        resp = client.create(f'{SERVICE}.create',
            cluster_id=1,
            name='test-wss-inactive',
            is_active=False,
            username='testwssuser4',
            mode='username_token',
            use_digest=False,
        )
        assert 'id' in resp
        self.__class__.created_ids.append(resp['id'])

        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        item = _find_by_name(data, 'test-wss-inactive')

        assert item is not None
        assert item['is_active'] is False
        assert item['use_digest'] is False

# ################################################################################################################################

    def test_09_edit_one(self, client:'ZatoClient') -> 'None':
        item_id = self.__class__.created_ids[0]
        resp = client.edit(f'{SERVICE}.edit',
            id=item_id,
            cluster_id=1,
            name='test-wss-username-token-edited',
            is_active=True,
            username='testwssuser1-edited',
            mode='username_token',
            use_digest=False,
        )
        assert resp['id'] == item_id

# ################################################################################################################################

    def test_10_get_list_after_edit(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)
        item = _find_by_name(data, 'test-wss-username-token-edited')

        assert item is not None
        assert item['username'] == 'testwssuser1-edited'
        assert item['use_digest'] is False

        assert _find_by_name(data, 'test-wss-username-token') is None

# ################################################################################################################################

    def test_11_delete_all(self, client:'ZatoClient') -> 'None':
        for item_id in self.__class__.created_ids[:]:
            _ = client.delete(f'{SERVICE}.delete', id=item_id)
            self.__class__.created_ids.remove(item_id)

# ################################################################################################################################

    def test_12_get_list_final(self, client:'ZatoClient') -> 'None':
        data, _meta = client.get_list(f'{SERVICE}.get-list', cluster_id=1)

        remaining = []
        for item in data:
            if item['name'].startswith('test-wss-'):
                remaining.append(item)

        assert len(remaining) == 0

# ################################################################################################################################
# ################################################################################################################################
