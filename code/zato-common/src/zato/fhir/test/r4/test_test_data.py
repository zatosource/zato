# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

import pytest

from datetime import datetime

from zato.fhir.test.r4.v1 import TestData, Scenarios

# ################################################################################################################################
# ################################################################################################################################

US_Core_Race      = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race'
US_Core_Ethnicity = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity'
US_Core_Birthsex  = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex'

Wellness_Visit_Types = [
    'Patient', 'Practitioner', 'PractitionerRole', 'Organization', 'Location',
    'Encounter', 'Observation', 'DiagnosticReport', 'Specimen', 'Procedure',
    'ServiceRequest', 'EpisodeOfCare', 'Composition', 'DocumentReference',
    'List', 'Provenance',
]

def _parse_fhir_dt(s):
    if not s:
        return None
    s = str(s)
    for fmt in ('%Y-%m-%dT%H:%M:%S+00:00', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None

# ################################################################################################################################
# ################################################################################################################################

class TestTestDataAPI:

    @pytest.mark.parametrize('resource_type', Wellness_Visit_Types)
    def test_resource_type_not_empty(self, resource_type):
        resources = getattr(TestData, resource_type)
        assert len(resources) > 0, f'TestData.{resource_type} is empty'

    @pytest.mark.parametrize('resource_type', Wellness_Visit_Types)
    def test_resource_has_id(self, resource_type):
        for resource in getattr(TestData, resource_type):
            assert resource.id, f'{resource_type} resource missing id'

    @pytest.mark.parametrize('resource_type', Wellness_Visit_Types)
    def test_resource_round_trip(self, resource_type):
        for resource in getattr(TestData, resource_type):
            d1 = resource.to_dict()
            cls = type(resource)
            obj2 = cls.from_dict(d1)
            d2 = obj2.to_dict()
            assert d1 == d2, f'{resource_type}/{resource.id}: round-trip mismatch'

    def test_patient_count(self):
        assert len(TestData.Patient) >= 10

    def test_encounter_count(self):
        assert len(TestData.Encounter) >= 30

    def test_observation_count(self):
        assert len(TestData.Observation) >= 360

# ################################################################################################################################
# ################################################################################################################################

class TestScenariosWellnessVisit:

    def test_instance_count(self):
        assert len(Scenarios.wellness_visit) == 10

    @pytest.mark.parametrize('inst', Scenarios.wellness_visit,
                             ids=lambda s: s.patient.id)
    def test_all_scenario_fields_populated(self, inst):
        assert inst.patient is not None
        assert inst.practitioner is not None
        assert inst.practitioner_role is not None
        assert inst.organization is not None
        assert inst.location is not None
        assert inst.encounters
        assert inst.observations
        assert inst.diagnostic_report is not None
        assert inst.specimen is not None
        assert inst.procedure is not None
        assert inst.service_request is not None
        assert inst.episode_of_care is not None
        assert inst.composition is not None
        assert inst.document_ref is not None
        assert inst.list_resource is not None
        assert inst.provenance is not None

    @pytest.mark.parametrize('inst', Scenarios.wellness_visit,
                             ids=lambda s: s.patient.id)
    def test_encounter_count_3_to_5(self, inst):
        n = len(inst.encounters)
        assert 3 <= n <= 5, f'Expected 3-5 encounters, got {n}'

    @pytest.mark.parametrize('inst', Scenarios.wellness_visit,
                             ids=lambda s: s.patient.id)
    def test_encounter_span_at_least_6_months(self, inst):
        dates = []
        for enc in inst.encounters:
            dt = _parse_fhir_dt(enc.period.start)
            assert dt is not None, f'Cannot parse encounter start: {enc.period.start}'
            dates.append(dt)
        dates.sort()
        span_days = (dates[-1] - dates[0]).days
        assert span_days >= 180, f'Encounter span is {span_days} days, need >= 180'

    @pytest.mark.parametrize('inst', Scenarios.wellness_visit,
                             ids=lambda s: s.patient.id)
    def test_linked_resources_per_encounter(self, inst):
        shared_count = 4
        for enc in inst.encounters:
            enc_ref = f'Encounter/{enc.id}'
            obs_count = sum(1 for o in inst.observations
                           if o.encounter and o.encounter.reference == enc_ref)
            linked = 1 + obs_count + shared_count
            assert linked >= 15, \
                f'Encounter {enc.id} has {linked} linked resources, need >= 15'

    @pytest.mark.parametrize('inst', Scenarios.wellness_visit,
                             ids=lambda s: s.patient.id)
    def test_patient_encounter_cross_reference(self, inst):
        pt_ref = f'Patient/{inst.patient.id}'
        for enc in inst.encounters:
            assert enc.subject.reference == pt_ref, \
                f'Encounter {enc.id} subject={enc.subject.reference}, expected {pt_ref}'

    @pytest.mark.parametrize('inst', Scenarios.wellness_visit,
                             ids=lambda s: s.patient.id)
    def test_observation_encounter_cross_reference(self, inst):
        valid_enc_refs = {f'Encounter/{e.id}' for e in inst.encounters}
        for obs in inst.observations:
            assert obs.encounter.reference in valid_enc_refs, \
                f'Observation {obs.id} references unknown encounter: {obs.encounter.reference}'

    @pytest.mark.parametrize('inst', Scenarios.wellness_visit,
                             ids=lambda s: s.patient.id)
    def test_observation_patient_cross_reference(self, inst):
        pt_ref = f'Patient/{inst.patient.id}'
        for obs in inst.observations:
            assert obs.subject.reference == pt_ref

    @pytest.mark.parametrize('inst', Scenarios.wellness_visit,
                             ids=lambda s: s.patient.id)
    def test_us_core_race_extension(self, inst):
        ext_urls = {e.url for e in inst.patient.extension}
        assert US_Core_Race in ext_urls, 'Patient missing us-core-race extension'
        race_ext = next(e for e in inst.patient.extension if e.url == US_Core_Race)
        sub_urls = {se.url for se in race_ext.extension}
        assert 'ombCategory' in sub_urls
        assert 'text' in sub_urls

    @pytest.mark.parametrize('inst', Scenarios.wellness_visit,
                             ids=lambda s: s.patient.id)
    def test_us_core_ethnicity_extension(self, inst):
        ext_urls = {e.url for e in inst.patient.extension}
        assert US_Core_Ethnicity in ext_urls, 'Patient missing us-core-ethnicity extension'
        eth_ext = next(e for e in inst.patient.extension if e.url == US_Core_Ethnicity)
        sub_urls = {se.url for se in eth_ext.extension}
        assert 'ombCategory' in sub_urls
        assert 'text' in sub_urls

    @pytest.mark.parametrize('inst', Scenarios.wellness_visit,
                             ids=lambda s: s.patient.id)
    def test_us_core_birthsex_extension(self, inst):
        ext_urls = {e.url for e in inst.patient.extension}
        assert US_Core_Birthsex in ext_urls, 'Patient missing us-core-birthsex extension'

    @pytest.mark.parametrize('inst', Scenarios.wellness_visit,
                             ids=lambda s: s.patient.id)
    def test_preferred_language(self, inst):
        assert inst.patient.communication, 'Patient has no communication entries'
        comm = inst.patient.communication[0]
        assert comm.language, 'Communication has no language'
        assert comm.preferred is True, 'First communication is not preferred'

    @pytest.mark.parametrize('inst', Scenarios.wellness_visit,
                             ids=lambda s: s.patient.id)
    def test_patient_has_mrn_and_ssn(self, inst):
        systems = {ident.system for ident in inst.patient.identifier}
        assert 'http://example.org/mrn' in systems, 'Patient missing MRN identifier'
        assert 'http://hl7.org/fhir/sid/us-ssn' in systems, 'Patient missing SSN identifier'

    @pytest.mark.parametrize('inst', Scenarios.wellness_visit,
                             ids=lambda s: s.patient.id)
    def test_practitioner_has_npi(self, inst):
        systems = {ident.system for ident in inst.practitioner.identifier}
        assert 'http://hl7.org/fhir/sid/us-npi' in systems, 'Practitioner missing NPI'

# ################################################################################################################################
# ################################################################################################################################
