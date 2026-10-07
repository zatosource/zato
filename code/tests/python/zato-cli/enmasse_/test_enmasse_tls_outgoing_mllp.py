# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The TLS paths of an outgoing MLLP connection in enmasse - a client certificate comes with a CA bundle.

# stdlib
from json import loads

# pytest
import pytest

# PyYAML
import yaml

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.outgoing_mllp import OutgoingMLLPImporter
from zato.cli.enmasse.util.secrets import Session_Key_Crypto_Manager
from zato.common.crypto.api import ServerCryptoManager
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, GenericObject, SecurityBase, Service, SMTP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    any_ = any_
    anydict = anydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

_cluster_id = 1

# One connection verifies the server alone, one presents a client certificate as well
_conn_name_verified = 'enmasse.tls.mllp.verified'
_conn_name_mutual   = 'enmasse.tls.mllp.mutual'

_ca_path   = '/etc/zato/tls/receiving-system-ca.pem'
_cert_path = '/etc/zato/tls/sending-system-cert.pem'
_key_path  = '/etc/zato/tls/sending-system-key.pem'

_yaml_text = f"""
outgoing_mllp:
  - name: {_conn_name_verified}
    address: 10.20.30.40:2575
    tls_ca_path: {_ca_path}

  - name: {_conn_name_mutual}
    address: 10.20.30.41:2575
    tls_ca_path: {_ca_path}
    tls_cert_path: {_cert_path}
    tls_key_path: {_key_path}
"""

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def yaml_config() -> 'stranydict':
    out = yaml.safe_load(_yaml_text)
    return out

# ################################################################################################################################

@pytest.fixture
def session() -> 'any_':
    """ A real ODB session over an in-memory SQLite database holding one cluster, with the crypto manager
    the generic importer encrypts secrets with.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        GenericConnDef.__table__,
        GenericConn.__table__,
        GenericObject.__table__,
        SMTP.__table__,
        Service.__table__,
        SecurityBase.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    session.info[Session_Key_Crypto_Manager] = ServerCryptoManager.from_secret_key(ServerCryptoManager.generate_key())

    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)
    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

@pytest.fixture
def mllp_importer() -> 'OutgoingMLLPImporter':
    out = OutgoingMLLPImporter(EnmasseYAMLImporter())
    return out

# ################################################################################################################################

def _opaque(connection:'any_') -> 'anydict':
    out = loads(connection.opaque1)
    return out

# ################################################################################################################################

def _by_name(items:'any_') -> 'anydict':
    out = {}

    for item in items:
        out[item.name] = item

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOutgoingMLLPTLSImport:

    def test_a_ca_bundle_alone_is_stored(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mllp_importer:'OutgoingMLLPImporter',
    ) -> 'None':
        created, _ = mllp_importer.sync_definitions(yaml_config['outgoing_mllp'], session)
        connection = _by_name(created)[_conn_name_verified]

        opaque = _opaque(connection)

        assert opaque['tls_ca_path'] == _ca_path
        assert opaque['tls_cert_path'] == ''
        assert opaque['tls_key_path'] == ''

# ################################################################################################################################

    def test_a_client_certificate_with_a_ca_bundle_is_stored(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mllp_importer:'OutgoingMLLPImporter',
    ) -> 'None':
        created, _ = mllp_importer.sync_definitions(yaml_config['outgoing_mllp'], session)
        connection = _by_name(created)[_conn_name_mutual]

        opaque = _opaque(connection)

        assert opaque['tls_ca_path'] == _ca_path
        assert opaque['tls_cert_path'] == _cert_path
        assert opaque['tls_key_path'] == _key_path

# ################################################################################################################################

    def test_a_client_certificate_without_a_ca_bundle_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mllp_importer:'OutgoingMLLPImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_mllp']
        del definitions[1]['tls_ca_path']

        with pytest.raises(Exception) as context:
            _ = mllp_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'client certificate' in message
        assert 'CA bundle' in message
        assert 'outgoing MLLP' in message
        assert _conn_name_mutual in message

        stored = session.query(GenericConn).filter_by(name=_conn_name_mutual).first()
        assert stored is None

# ################################################################################################################################

    def test_a_client_certificate_with_an_empty_ca_bundle_is_rejected(
        self,
        yaml_config:'stranydict',
        session:'any_',
        mllp_importer:'OutgoingMLLPImporter',
    ) -> 'None':
        definitions = yaml_config['outgoing_mllp']
        definitions[1]['tls_ca_path'] = ''

        with pytest.raises(Exception) as context:
            _ = mllp_importer.sync_definitions(definitions, session)

        message = str(context.value)
        assert 'client certificate' in message
        assert _conn_name_mutual in message

# ################################################################################################################################
# ################################################################################################################################
