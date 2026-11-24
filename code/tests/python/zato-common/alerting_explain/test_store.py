# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import contextmanager

# SQLAlchemy
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.alerting.explain.store import ExplanationStore
from zato.common.odb.model import GenericConn, GenericConnClient, GenericConnDef, GenericConnDefSec, GenericConnSec, \
    GenericObject, SecurityBase, Server
from zato.common.test.config_database import config_database_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import stranydict
    storegen = Iterator[ExplanationStore]

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def _new_store() -> 'storegen':
    """ A store over a new PostgreSQL database of its own with the generic_object table and the tables it refers to.
    """
    tables = [
        SecurityBase.__table__,
        Server.__table__,
        GenericConnDef.__table__,
        GenericConnDefSec.__table__,
        GenericConn.__table__,
        GenericConnSec.__table__,
        GenericConnClient.__table__,
        GenericObject.__table__,
    ]

    with config_database_engine(tables) as engine:
        session = sessionmaker(bind=engine)

        out = ExplanationStore(session)
        yield out

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
        'explanation': 'The remote server replied with HTTP 503 for every call.',
        'confidence': 'high',
        'remediation': {'action': 'resubmit'},
        'is_parsed': True,
        'created_iso': created_iso,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestExplanationStore:

    def test_a_created_explanation_reads_back_in_full(self) -> 'None':
        with _new_store() as store:
            details = _new_details()

            store.create('alert.123', details)
            explanation = store.get('alert.123')

            assert explanation is not None
            assert explanation['name'] == 'alert.123'
            assert explanation['object_name'] == 'CRM API'
            assert explanation['explanation'] == details['explanation']
            assert explanation['remediation'] == {'action': 'resubmit'}
            assert explanation['alert_id'] == 123

    def test_an_unknown_name_reads_back_as_none(self) -> 'None':
        with _new_store() as store:
            explanation = store.get('alert.no-such-alert')

            assert explanation is None

    def test_the_listing_is_newest_first(self) -> 'None':
        with _new_store() as store:
            store.create('alert.older', _new_details(created_iso='2026-08-09T10:00:00'))
            store.create('alert.newer', _new_details(created_iso='2026-08-09T11:00:00'))

            explanations = store.get_list()

            assert len(explanations) == 2
            assert explanations[0]['name'] == 'alert.newer'
            assert explanations[1]['name'] == 'alert.older'

    def test_exists_sees_only_stored_explanations(self) -> 'None':
        with _new_store() as store:
            store.create('alert.123', _new_details())

            assert store.exists('alert.123') is True
            assert store.exists('alert.456') is False

# ################################################################################################################################
# ################################################################################################################################
