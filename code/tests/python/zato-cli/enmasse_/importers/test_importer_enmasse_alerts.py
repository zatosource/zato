# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads

# pytest
import pytest

# PyYAML
import yaml

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.ftp import FTPImporter
from zato.cli.enmasse.importers.sftp import SFTPImporter
from zato.cli.enmasse.importers.smb import SMBImporter
from zato.common.alerting.object_config import Alerts_Key, storage_name
from zato.common.api import EMAIL, GENERIC
from zato.common.odb.model import Base, Cluster, GenericConn, GenericConnDef, IMAP, SMTP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    any_ = any_
    anydict = anydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The cluster every object in the test database belongs to
_cluster_id = 1

# The email connections an alerts mapping may name - one SMTP, one Microsoft 365 IMAP
# and one generic IMAP which has nothing to send alerts with.
_smtp_name = 'enmasse.alerts.smtp'
_imap_m365_name = 'enmasse.alerts.imap.m365'
_imap_generic_name = 'enmasse.alerts.imap.generic'

# The LLM connection an alerts mapping may name for its explanations
_llm_name = 'enmasse.alerts.llm'

# The same YAML a person would write - one connection moving every alert setting away from its default,
# one moving a few of them and one carrying no alerts mapping at all.
_yaml_text = f"""
sftp:
  - name: enmasse.alerts.sftp.1
    address: sftp.example.com
    username: enmasse
    alerts:
      is_active: false
      consecutive_failures: 5
      warning_failures: 15
      error_failures: 30
      window: 43200
      arrival_overdue: 2
      test_transfers: true
      use_llm: false
      email_connection: smtp:{_smtp_name}
      llm_connection: {_llm_name}

  - name: enmasse.alerts.sftp.2
    address: sftp.example.com
    username: enmasse
    alerts:
      error_failures: 25
      email_connection: imap:{_imap_m365_name}

  - name: enmasse.alerts.sftp.3
    address: sftp.example.com
    username: enmasse

ftp:
  - name: enmasse.alerts.ftp.1
    host: ftp.example.com
    alerts:
      consecutive_failures: 7

smb:
  - name: enmasse.alerts.smb.1
    host: smb.example.com
    alerts:
      window: 3600
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
    """ A real ODB session over an in-memory SQLite database holding one cluster, the generic
    connection tables and the three email connections the alerts mappings may name.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        GenericConnDef.__table__,
        GenericConn.__table__,
        SMTP.__table__,
        IMAP.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)

    smtp = SMTP()
    smtp.name = _smtp_name
    smtp.is_active = True
    smtp.host = 'smtp.example.com'
    smtp.port = 587
    smtp.timeout = 30
    smtp.is_debug = False
    smtp.mode = EMAIL.SMTP.MODE.STARTTLS
    smtp.ping_address = 'ping@example.com'
    smtp.cluster = cluster
    session.add(smtp)

    imap_m365 = _new_imap(_imap_m365_name, EMAIL.IMAP.ServerType.Microsoft365, cluster)
    session.add(imap_m365)

    imap_generic = _new_imap(_imap_generic_name, EMAIL.IMAP.ServerType.Generic, cluster)
    session.add(imap_generic)

    llm = GenericConn()
    llm.name = _llm_name
    llm.type_ = GENERIC.CONNECTION.TYPE.OUTCONN_LLM
    llm.is_active = True
    llm.is_internal = False
    llm.is_channel = False
    llm.is_outconn = True
    llm.cluster = cluster
    session.add(llm)

    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

def _new_imap(name:'str', server_type:'str', cluster:'Cluster') -> 'IMAP':
    out = IMAP()
    out.name = name
    out.is_active = True
    out.host = 'imap.example.com'
    out.port = 993
    out.timeout = 30
    out.debug_level = 0
    out.mode = EMAIL.IMAP.MODE.SSL
    out.get_criteria = '{}'
    out.opaque1 = dumps({'server_type': server_type})
    out.cluster = cluster
    return out

# ################################################################################################################################

@pytest.fixture
def importer() -> 'EnmasseYAMLImporter':
    out = EnmasseYAMLImporter()
    return out

# ################################################################################################################################

@pytest.fixture
def sftp_importer(importer:'EnmasseYAMLImporter') -> 'SFTPImporter':
    out = SFTPImporter(importer)
    return out

# ################################################################################################################################

def _opaque(connection:'GenericConn') -> 'anydict':
    out = loads(connection.opaque1)
    return out

# ################################################################################################################################

def _by_name(connections:'any_') -> 'anydict':
    out = {}

    for connection in connections:
        out[connection.name] = connection

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAlertsImport:

    def test_every_alert_setting_is_stored_under_its_prefix(
        self,
        yaml_config:'stranydict',
        session:'any_',
        sftp_importer:'SFTPImporter',
    ) -> 'None':
        """ Each value of the alerts mapping lands in the opaque attributes under the alert_ prefix
        and the mapping itself is not stored.
        """
        created, _ = sftp_importer.sync_definitions(yaml_config['sftp'], session)
        connection = _by_name(created)['enmasse.alerts.sftp.1']

        opaque = _opaque(connection)

        assert opaque[storage_name('is_active')] is False
        assert opaque[storage_name('consecutive_failures')] == 5
        assert opaque[storage_name('warning_failures')] == 15
        assert opaque[storage_name('error_failures')] == 30
        assert opaque[storage_name('window')] == 43200
        assert opaque[storage_name('arrival_overdue')] == 2
        assert opaque[storage_name('test_transfers')] is True
        assert opaque[storage_name('use_llm')] is False
        assert opaque[storage_name('email_connection')] == f'smtp:{_smtp_name}'
        assert opaque[storage_name('llm_connection')] == _llm_name

        assert Alerts_Key not in opaque

# ################################################################################################################################

    def test_settings_left_out_take_the_defaults(
        self,
        yaml_config:'stranydict',
        session:'any_',
        sftp_importer:'SFTPImporter',
    ) -> 'None':
        """ A mapping naming a few settings only has the rest stored at their defaults,
        so that every stored connection carries every field.
        """
        created, _ = sftp_importer.sync_definitions(yaml_config['sftp'], session)
        connection = _by_name(created)['enmasse.alerts.sftp.2']

        opaque = _opaque(connection)

        assert opaque[storage_name('error_failures')] == 25
        assert opaque[storage_name('email_connection')] == f'imap:{_imap_m365_name}'
        assert opaque[storage_name('llm_connection')] == ''

        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('consecutive_failures')] == 3
        assert opaque[storage_name('warning_failures')] == 10
        assert opaque[storage_name('window')] == 86400
        assert opaque[storage_name('arrival_overdue')] == 1
        assert opaque[storage_name('test_transfers')] is False
        assert opaque[storage_name('use_llm')] is True

# ################################################################################################################################

    def test_a_connection_without_the_mapping_runs_on_defaults(
        self,
        yaml_config:'stranydict',
        session:'any_',
        sftp_importer:'SFTPImporter',
    ) -> 'None':
        """ A connection with no alerts mapping at all is stored with every alert setting at its default.
        """
        created, _ = sftp_importer.sync_definitions(yaml_config['sftp'], session)
        connection = _by_name(created)['enmasse.alerts.sftp.3']

        opaque = _opaque(connection)

        assert opaque[storage_name('is_active')] is True
        assert opaque[storage_name('consecutive_failures')] == 3
        assert opaque[storage_name('warning_failures')] == 10
        assert opaque[storage_name('error_failures')] == 20
        assert opaque[storage_name('window')] == 86400
        assert opaque[storage_name('arrival_overdue')] == 1
        assert opaque[storage_name('test_transfers')] is False
        assert opaque[storage_name('use_llm')] is True
        assert opaque[storage_name('email_connection')] == ''

# ################################################################################################################################

    def test_an_update_makes_the_yaml_the_source_of_truth(
        self,
        yaml_config:'stranydict',
        session:'any_',
        sftp_importer:'SFTPImporter',
    ) -> 'None':
        """ Importing again with a setting moved back to its default, and another one dropped from the mapping,
        stores the defaults for both rather than keeping what the first run stored.
        """
        definitions = yaml_config['sftp']

        created, _ = sftp_importer.sync_definitions(definitions, session)
        assert len(created) == 3

        # The first run took the mapping out of the definitions, so the second one gets a fresh copy
        definitions = yaml.safe_load(_yaml_text)['sftp']
        definitions[0]['alerts'] = {'consecutive_failures': 3, 'use_llm': False}

        created_again, updated = sftp_importer.sync_definitions(definitions, session)
        assert len(created_again) == 0
        assert len(updated) == 3

        connection = _by_name(updated)['enmasse.alerts.sftp.1']
        opaque = _opaque(connection)

        assert opaque[storage_name('consecutive_failures')] == 3
        assert opaque[storage_name('use_llm')] is False
        assert opaque[storage_name('error_failures')] == 20
        assert opaque[storage_name('email_connection')] == ''

# ################################################################################################################################

    def test_ftp_and_smb_carry_the_same_settings(
        self,
        yaml_config:'stranydict',
        session:'any_',
        importer:'EnmasseYAMLImporter',
    ) -> 'None':
        """ FTP and SMB connections store their alert settings the way SFTP ones do.
        """
        created, _ = FTPImporter(importer).sync_definitions(yaml_config['ftp'], session)
        opaque = _opaque(created[0])

        assert opaque[storage_name('consecutive_failures')] == 7
        assert opaque[storage_name('window')] == 86400

        created, _ = SMBImporter(importer).sync_definitions(yaml_config['smb'], session)
        opaque = _opaque(created[0])

        assert opaque[storage_name('consecutive_failures')] == 3
        assert opaque[storage_name('window')] == 3600

# ################################################################################################################################
# ################################################################################################################################

class TestAlertsImportRejections:

    def _definition(self, alerts:'anydict') -> 'anydict':
        out = {
            'name': 'enmasse.alerts.sftp.rejected',
            'address': 'sftp.example.com',
            'username': 'enmasse',
            Alerts_Key: alerts,
        }
        return out

# ################################################################################################################################

    def test_a_missing_email_connection_is_rejected(
        self,
        session:'any_',
        sftp_importer:'SFTPImporter',
    ) -> 'None':
        """ Naming an SMTP connection that does not exist is refused rather than stored,
        which would leave the alerts going nowhere.
        """
        definition = self._definition({'email_connection': 'smtp:enmasse.no.such.connection'})

        with pytest.raises(Exception) as context:
            _ = sftp_importer.sync_definitions([definition], session)

        message = str(context.value)
        assert 'enmasse.no.such.connection' in message
        assert 'smtp' in message
        assert 'enmasse.alerts.sftp.rejected' in message

# ################################################################################################################################

    def test_a_generic_imap_connection_is_rejected(
        self,
        session:'any_',
        sftp_importer:'SFTPImporter',
    ) -> 'None':
        """ Only a Microsoft 365 IMAP connection can send alerts, so a generic one is refused
        the same way a connection that does not exist is.
        """
        definition = self._definition({'email_connection': f'imap:{_imap_generic_name}'})

        with pytest.raises(Exception) as context:
            _ = sftp_importer.sync_definitions([definition], session)

        message = str(context.value)
        assert _imap_generic_name in message
        assert 'not found' in message

# ################################################################################################################################

    def test_an_unknown_kind_is_rejected(
        self,
        session:'any_',
        sftp_importer:'SFTPImporter',
    ) -> 'None':
        """ An email connection value has to name a kind the alerts can send through.
        """
        definition = self._definition({'email_connection': f'pop3:{_smtp_name}'})

        with pytest.raises(Exception) as context:
            _ = sftp_importer.sync_definitions([definition], session)

        message = str(context.value)
        assert 'pop3' in message
        assert 'unknown kind' in message

# ################################################################################################################################

    def test_an_unknown_field_is_rejected(
        self,
        session:'any_',
        sftp_importer:'SFTPImporter',
    ) -> 'None':
        """ A key under alerts that is not a field of the alert type is a mistake in the file,
        not a setting to store.
        """
        definition = self._definition({'consecutive_failure': 5})

        with pytest.raises(Exception) as context:
            _ = sftp_importer.sync_definitions([definition], session)

        message = str(context.value)
        assert 'consecutive_failure' in message

# ################################################################################################################################

    def test_a_missing_llm_connection_is_rejected(
        self,
        session:'any_',
        sftp_importer:'SFTPImporter',
    ) -> 'None':
        """ Naming an LLM connection that does not exist is refused rather than stored,
        which would leave the explanations going nowhere.
        """
        definition = self._definition({'llm_connection': 'enmasse.no.such.llm'})

        with pytest.raises(Exception) as context:
            _ = sftp_importer.sync_definitions([definition], session)

        message = str(context.value)
        assert 'enmasse.no.such.llm' in message
        assert 'LLM connection' in message
        assert 'enmasse.alerts.sftp.rejected' in message

# ################################################################################################################################

    def test_an_empty_llm_connection_is_accepted(
        self,
        session:'any_',
        sftp_importer:'SFTPImporter',
    ) -> 'None':
        """ An empty LLM connection means the deployment's default explains the alerts, which is the default.
        """
        definition = self._definition({'llm_connection': ''})

        created, _ = sftp_importer.sync_definitions([definition], session)
        opaque = _opaque(created[0])

        assert opaque[storage_name('llm_connection')] == ''

# ################################################################################################################################

    def test_an_empty_email_connection_is_accepted(
        self,
        session:'any_',
        sftp_importer:'SFTPImporter',
    ) -> 'None':
        """ An empty email connection means the ruleset-wide notifications only, which is the default.
        """
        definition = self._definition({'email_connection': ''})

        created, _ = sftp_importer.sync_definitions([definition], session)
        opaque = _opaque(created[0])

        assert opaque[storage_name('email_connection')] == ''

# ################################################################################################################################
# ################################################################################################################################
