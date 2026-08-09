# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.api import Incidents
from zato.common.incidents.store import IncidentStore
from zato.common.odb.model import Base, GenericObject

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

# The cluster all the test incidents belong to.
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
        'history': [{'action': 'raised', 'actor': 'zato', 'time_iso': created_iso, 'note': ''}],
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestIncidentStore:

    def test_a_created_incident_reads_back_in_full(self) -> 'None':
        store = _new_store()
        details = _new_details()

        store.create('incident.abc', details, Incidents.Status.Awaiting_Approval)
        incident = store.get('incident.abc')

        assert incident is not None
        assert incident['name'] == 'incident.abc'
        assert incident['status'] == Incidents.Status.Awaiting_Approval
        assert incident['object_name'] == 'CRM API'
        assert incident['diagnosis'] == details['diagnosis']
        assert incident['remediation'] == {'action': 'resubmit'}
        assert incident['history'][0]['action'] == 'raised'

    def test_an_unknown_name_reads_back_as_none(self) -> 'None':
        store = _new_store()

        incident = store.get('incident.no-such-incident')

        assert incident is None

    def test_the_listing_is_newest_first(self) -> 'None':
        store = _new_store()

        store.create('incident.older', _new_details(created_iso='2026-08-09T10:00:00'), Incidents.Status.Awaiting_Approval)
        store.create('incident.newer', _new_details(created_iso='2026-08-09T11:00:00'), Incidents.Status.Awaiting_Approval)

        incidents = store.get_list()

        assert len(incidents) == 2
        assert incidents[0]['name'] == 'incident.newer'
        assert incidents[1]['name'] == 'incident.older'

    def test_the_listing_narrows_to_one_status(self) -> 'None':
        store = _new_store()

        store.create('incident.open', _new_details(), Incidents.Status.Awaiting_Approval)
        store.create('incident.closed', _new_details(), Incidents.Status.Rejected)

        incidents = store.get_list(Incidents.Status.Rejected)

        assert len(incidents) == 1
        assert incidents[0]['name'] == 'incident.closed'

    def test_an_update_changes_the_status_and_the_details(self) -> 'None':
        store = _new_store()
        details = _new_details()

        store.create('incident.abc', details, Incidents.Status.Awaiting_Approval)

        details['history'].append({
            'action': 'approved', 'actor': 'admin', 'time_iso': '2026-08-09T12:00:00', 'note': ''})

        store.update('incident.abc', details, Incidents.Status.Approved)
        incident = store.get('incident.abc')

        assert incident is not None
        assert incident['status'] == Incidents.Status.Approved
        assert len(incident['history']) == 2
        assert incident['history'][1]['actor'] == 'admin'

    def test_has_open_sees_incidents_awaiting_a_decision(self) -> 'None':
        store = _new_store()

        store.create('incident.abc', _new_details(object_name='CRM API'), Incidents.Status.Awaiting_Approval)

        assert store.has_open('CRM API') is True
        assert store.has_open('Billing API') is False

    def test_has_open_ignores_resolved_and_rejected_incidents(self) -> 'None':
        store = _new_store()

        store.create('incident.resolved', _new_details(object_name='CRM API'), Incidents.Status.Resolved)
        store.create('incident.rejected', _new_details(object_name='CRM API'), Incidents.Status.Rejected)

        assert store.has_open('CRM API') is False

# ################################################################################################################################
# ################################################################################################################################
