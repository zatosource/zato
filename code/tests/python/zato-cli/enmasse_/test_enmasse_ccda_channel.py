# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A REST channel that converts C-CDA documents on arrival - its data format imported as the channel's own, exported back
# as it was written, a change of format being an update rather than a second channel, and the same file imported twice
# changing nothing.

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.exporters.channel_rest import ChannelExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.channel_rest import ChannelImporter
from zato.common.api import DATA_FORMAT, HL7
from zato.common.odb.model import Base, Cluster, GenericObject, HTTPSOAP, SecurityBase, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

_ccda = HL7.CCDA

_cluster_id = 1
_service_name = 'enmasse.ccda.service'

# The two channels of the file - one converting C-CDA documents, one taking HL7 v2 messages
_ccda_name = 'enmasse.ccda.channel'
_ccda_path = '/enmasse/ccda'

_v2_name = 'enmasse.ccda.channel.v2'
_v2_path = '/enmasse/ccda/v2'

_definitions:'anylist' = [
    {
        'name': _ccda_name,
        'service': _service_name,
        'url_path': _ccda_path,
        'data_format': _ccda.Data_Format,
    },
    {
        'name': _v2_name,
        'service': _service_name,
        'url_path': _v2_path,
        'data_format': HL7.Const.Version.v2.id,
    },
]

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def session() -> 'any_':
    """ A real ODB session over an in-memory SQLite database holding one cluster and the service the channels invoke.
    """
    engine = create_engine('sqlite://')

    tables = [
        Cluster.__table__,
        GenericObject.__table__,
        Service.__table__,
        SecurityBase.__table__,
        HTTPSOAP.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    session_factory = sessionmaker(bind=engine)
    session = session_factory()

    cluster = Cluster(_cluster_id, 'test-cluster', '', 'sqlite')
    session.add(cluster)
    session.add(Service(None, _service_name, True, 'enmasse.ccda.Service', False, cluster))
    session.commit()

    yield session

    session.close()
    engine.dispose()

# ################################################################################################################################

def _sync(session:'any_', definitions:'anylist') -> 'tuple':
    """ One import of the definitions, on a fresh importer the way each enmasse run is.
    """
    importer = ChannelImporter(EnmasseYAMLImporter())

    copies = []
    for definition in definitions:
        copies.append(dict(definition))

    out = importer.sync_channel_rest(copies, session)
    session.commit()

    return out

# ################################################################################################################################

def _stored(session:'any_', name:'str') -> 'any_':
    out = session.query(HTTPSOAP).filter_by(name=name).one()
    return out

# ################################################################################################################################

def _exported(session:'any_') -> 'anydict':
    exporter = ChannelExporter(EnmasseYAMLExporter())

    out = {}
    for item in exporter.export(session, _cluster_id):
        out[item['name']] = item

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_format_is_imported_as_the_channels_own(session:'any_') -> 'None':
    created, updated = _sync(session, _definitions)

    assert len(created) == 2
    assert len(updated) == 0

    assert _stored(session, _ccda_name).data_format == _ccda.Data_Format
    assert _stored(session, _v2_name).data_format == HL7.Const.Version.v2.id

    # Both are HL7 channels to the Dashboard page that lists them
    for name in (_ccda_name, _v2_name):
        assert _stored(session, name).data_format.startswith(DATA_FORMAT.HL7)

# ################################################################################################################################

def test_the_format_is_exported_as_it_was_written(session:'any_') -> 'None':
    _ = _sync(session, _definitions)

    exported = _exported(session)

    assert exported[_ccda_name]['data_format'] == _ccda.Data_Format
    assert exported[_ccda_name]['service'] == _service_name
    assert exported[_ccda_name]['url_path'] == _ccda_path

    assert exported[_v2_name]['data_format'] == HL7.Const.Version.v2.id

# ################################################################################################################################

def test_the_same_file_twice_changes_nothing(session:'any_') -> 'None':
    _ = _sync(session, _definitions)
    before = _exported(session)

    created, updated = _sync(session, _definitions)

    assert len(created) == 0
    assert len(updated) == 0
    assert _exported(session) == before

# ################################################################################################################################

def test_a_change_of_format_is_an_update(session:'any_') -> 'None':
    _ = _sync(session, _definitions)

    changed = dict(_definitions[1], data_format=_ccda.Data_Format)
    created, updated = _sync(session, [changed])

    assert len(created) == 0
    assert len(updated) == 1

    assert _stored(session, _v2_name).data_format == _ccda.Data_Format
    assert session.query(HTTPSOAP).filter_by(name=_v2_name).count() == 1

# ################################################################################################################################

def test_the_export_reimports_as_the_same_channels(session:'any_') -> 'None':
    _ = _sync(session, _definitions)
    exported = _exported(session)

    created, updated = _sync(session, list(exported.values()))

    assert len(created) == 0
    assert len(updated) == 0
    assert _exported(session) == exported

# ################################################################################################################################
# ################################################################################################################################
