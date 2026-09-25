# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime

# Zato
from zato.server.service import Model, Service

# Project
from adapter_facility.facility_reader import FacilityReader
from common_sync.sync_database import DatabaseSession
from model.facility import Connection_Facility, ReferenceIDs, Source_Consult_Notes, Source_Treatments

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, dictlist, intlist

# ################################################################################################################################
# ################################################################################################################################

# Each source to the method that reads its log.
_readers = {
    Source_Treatments: FacilityReader.read_treatments,
    Source_Consult_Notes: FacilityReader.read_consult_notes,
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ReadLogRequest(Model):
    source: 'str'
    since:  'str'

# ################################################################################################################################

@dataclass(init=False)
class ResolveRequest(Model):
    patient_ids:   'intlist'
    staff_ids:     'intlist'
    condition_ids: 'intlist'
    treatment_ids: 'intlist'

# ################################################################################################################################
# ################################################################################################################################

class ReadLog(Service):
    """ The changes one source logged after a moment given in ISO format.
    """
    name = 'facility.change.read-log'
    input = ReadLogRequest

    def handle(self) -> 'None':

        request:'ReadLogRequest' = self.request.input
        since = datetime.fromisoformat(request.since)

        if request.source not in _readers:
            raise Exception(f'Unknown source -> {request.source}')

        database = DatabaseSession(self.out.sql[Connection_Facility])

        try:
            reader = FacilityReader(database)
            read = _readers[request.source]

            changes:'dictlist' = []

            for change in read(reader, since):
                change_dict = change.to_dict()
                changes.append(change_dict)

        finally:
            database.close()

        self.response.payload = {'changes': changes}

# ################################################################################################################################
# ################################################################################################################################

class ResolveReferences(Service):
    """ What the current tables say about the given IDs.
    """
    name = 'facility.reference.resolve'
    input = ResolveRequest

    def handle(self) -> 'None':

        request:'ResolveRequest' = self.request.input

        ids = ReferenceIDs()
        ids.patient_ids = set(request.patient_ids)
        ids.staff_ids = set(request.staff_ids)
        ids.condition_ids = set(request.condition_ids)
        ids.treatment_ids = set(request.treatment_ids)

        database = DatabaseSession(self.out.sql[Connection_Facility])

        try:
            reader = FacilityReader(database)
            references = reader.resolve(ids)
        finally:
            database.close()

        conditions:'anydict' = {}

        for condition_id, condition in references.conditions.items():
            conditions[condition_id] = {'code': condition.code, 'title': condition.title}

        self.response.payload = {
            'patients': references.patients,
            'staff': references.staff,
            'conditions': conditions,
            'treatments': references.treatments,
        }

# ################################################################################################################################
# ################################################################################################################################
