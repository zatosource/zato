# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.incidents.store import IncidentStore
from zato.common.odb.model import Base, GenericObject

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

# The cluster all the test diagnoses belong to.
_cluster_id = 1

# ################################################################################################################################
# ################################################################################################################################

def _new_store() -> 'IncidentStore':
    """ A store over a fresh in-memory database with just the generic_object table.
    """
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine, tables=[GenericObject.__table__])

    session = sessionmaker(bind=engine)

    out = IncidentStore(session, _cluster_id)
    return out

# ################################################################################################################################

def _new_details(object_name:'str'='CRM API', created_iso:'str'='2026-08-09T10:00:00') -> 'stranydict':
    out = {
        'object_name': object_name,
        'source': 'rest-outgoing',
        'rule': 'crm-errors',
        'alert_id': 123,
        'count': 1,
        'severity': 'warning',
        'message': 'Error rate on `CRM API` is 80% over the last 300s',
        'link': '',
        'evidence': {'alert': {}, 'connection': {}, 'audit_trail': []},
        'diagnosis': 'The remote server replied with HTTP 503 for every call.',
        'confidence': 'high',
        'remediation': {'action': 'resubmit'},
        'is_parsed': True,
        'created_iso': created_iso,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestIncidentStore:

    def test_a_created_diagnosis_reads_back_in_full(self) -> 'None':
        store = _new_store()
        details = _new_details()

        store.create('alert.123', details)
        diagnosis = store.get('alert.123')

        assert diagnosis is not None
        assert diagnosis['name'] == 'alert.123'
        assert diagnosis['object_name'] == 'CRM API'
        assert diagnosis['diagnosis'] == details['diagnosis']
        assert diagnosis['remediation'] == {'action': 'resubmit'}
        assert diagnosis['alert_id'] == 123

    def test_an_unknown_name_reads_back_as_none(self) -> 'None':
        store = _new_store()

        diagnosis = store.get('alert.no-such-alert')

        assert diagnosis is None

    def test_the_listing_is_newest_first(self) -> 'None':
        store = _new_store()

        store.create('alert.older', _new_details(created_iso='2026-08-09T10:00:00'))
        store.create('alert.newer', _new_details(created_iso='2026-08-09T11:00:00'))

        diagnoses = store.get_list()

        assert len(diagnoses) == 2
        assert diagnoses[0]['name'] == 'alert.newer'
        assert diagnoses[1]['name'] == 'alert.older'

    def test_exists_sees_only_stored_diagnoses(self) -> 'None':
        store = _new_store()

        store.create('alert.123', _new_details())

        assert store.exists('alert.123') is True
        assert store.exists('alert.456') is False

# ################################################################################################################################
# ################################################################################################################################
