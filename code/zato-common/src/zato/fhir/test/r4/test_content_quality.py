# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

import re

from datetime import datetime, date

import pytest

from zato.fhir.test.r4.v1 import TestData, Scenarios

# ################################################################################################################################
# ################################################################################################################################

# Regex for Latin script (ASCII + Western European accents, covers English and French)
_latin_re = re.compile(r'^[A-Za-z\u00C0-\u024F\u1E00-\u1EFF\s\-\'.]+$')

# Regex for Japanese script (Hiragana, Katakana, CJK Unified, fullwidth, punctuation)
_japanese_re = re.compile(
    r'^[\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF'
    r'\uFF00-\uFF9F\u30FB\u30FC\s\-\'.]+$'
)

_banned_patterns = [
    ('fake-',           re.compile(r'fake-', re.IGNORECASE)),
    ('test- prefix',    re.compile(r'\btest-\w', re.IGNORECASE)),
    ('xxx',             re.compile(r'\bxxx\b', re.IGNORECASE)),
    ('lorem ipsum',     re.compile(r'lorem\s+ipsum', re.IGNORECASE)),
    ('patient-NNN',     re.compile(r'patient-\d{3}')),
    ('uuid fragment',   re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}')),
]

# Clinically plausible ranges per LOINC code (wider than generation ranges)
_loinc_ranges = {
    '8480-6':  (80, 160),     # Systolic BP
    '8462-4':  (40, 110),     # Diastolic BP
    '8867-4':  (35, 120),     # Heart rate
    '8310-5':  (35.0, 38.5),  # Body temperature
    '9279-1':  (8, 30),       # Respiratory rate
    '2708-6':  (85, 100),     # Oxygen saturation
    '29463-7': (30, 200),     # Body weight
    '8302-2':  (100, 220),    # Body height
    '39156-5': (12, 50),      # BMI
    '2093-3':  (80, 350),     # Total cholesterol
    '1989-3':  (5, 120),      # Vitamin D
    '2339-0':  (40, 250),     # Blood glucose
}

_trending_loinc_codes = {'2093-3', '1989-3', '2339-0'}

# ################################################################################################################################
# ################################################################################################################################

def _all_strings(obj, path=''):
    """ Recursively yield (path, value) for every string in a nested dict/list. """
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _all_strings(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _all_strings(v, f'{path}[{i}]')
    elif isinstance(obj, str):
        yield path, obj

def _is_valid_name_script(text):
    return bool(_latin_re.match(text)) or bool(_japanese_re.match(text))

def _is_monotonic(values):
    if len(values) < 2:
        return True
    increasing = all(a <= b for a, b in zip(values, values[1:]))
    decreasing = all(a >= b for a, b in zip(values, values[1:]))
    return increasing or decreasing

def _parse_fhir_dt(s):
    s = str(s)
    for fmt in ('%Y-%m-%dT%H:%M:%S+00:00', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None

# ################################################################################################################################
# ################################################################################################################################

class TestNoPlaceholders:

    def test_no_banned_patterns_in_resources(self):
        issues = [] # type: list[str]
        for inst in Scenarios.wellness_visit:
            all_resources = [inst.patient, inst.practitioner, inst.organization,
                             inst.location, inst.practitioner_role, inst.diagnostic_report,
                             inst.specimen, inst.procedure, inst.service_request,
                             inst.episode_of_care, inst.composition, inst.document_ref,
                             inst.list_resource, inst.provenance]
            all_resources.extend(inst.encounters)
            all_resources.extend(inst.observations)

            for resource in all_resources:
                rd = resource.to_dict()
                rt = rd.get('resourceType', '?')
                rid = rd.get('id', '?')
                for path, value in _all_strings(rd):
                    if '.div' in path or path.endswith('.data'):
                        continue
                    if value.startswith(('http://', 'https://', 'urn:')):
                        continue
                    for pattern_name, pattern_re in _banned_patterns:
                        if pattern_re.search(value):
                            issues.append(f'{rt}/{rid}{path}: {pattern_name!r} in {value!r}')

        assert not issues, f'{len(issues)} placeholder violations:\n' + '\n'.join(issues[:20])

# ################################################################################################################################
# ################################################################################################################################

class TestPatientQuality:

    @pytest.mark.parametrize('patient', TestData.Patient, ids=lambda p: p.id)
    def test_plausible_birth_date(self, patient):
        bd = str(patient.birthDate)
        dt = datetime.strptime(bd, '%Y-%m-%d').date()
        today = date(2025, 6, 15)
        age = (today - dt).days / 365.25
        assert 1 <= age <= 100, f'Patient {patient.id} age is {age:.0f}'

    @pytest.mark.parametrize('patient', TestData.Patient, ids=lambda p: p.id)
    def test_name_has_family_and_given(self, patient):
        assert patient.name, 'Patient has no name'
        name = patient.name[0]
        assert name.family, 'Name missing family'
        family_str = str(name.family)
        assert len(family_str) >= 1, f'Family name empty: {name.family!r}'
        assert name.given, 'Name missing given'
        given_str = str(name.given[0])
        assert len(given_str) >= 1, f'Given name empty: {name.given[0]!r}'
        if _latin_re.match(family_str):
            assert len(family_str) >= 2, f'Latin family name too short: {family_str!r}'
        if _latin_re.match(given_str):
            assert len(given_str) >= 2, f'Latin given name too short: {given_str!r}'

    @pytest.mark.parametrize('patient', TestData.Patient, ids=lambda p: p.id)
    def test_gender_populated(self, patient):
        assert patient.gender in ('male', 'female'), f'Invalid gender: {patient.gender}'

    @pytest.mark.parametrize('patient', TestData.Patient, ids=lambda p: p.id)
    def test_has_address(self, patient):
        assert patient.address, 'Patient has no address'
        addr = patient.address[0]
        assert addr.line, 'Address missing street line'
        assert addr.city, 'Address missing city'
        assert addr.state, 'Address missing state'
        assert addr.postalCode, 'Address missing postal code'

    @pytest.mark.parametrize('patient', TestData.Patient, ids=lambda p: p.id)
    def test_has_telecom(self, patient):
        assert patient.telecom, 'Patient has no telecom'
        systems = {str(t.system) for t in patient.telecom}
        assert 'phone' in systems, 'Patient missing phone'
        assert 'email' in systems, 'Patient missing email'

# ################################################################################################################################
# ################################################################################################################################

class TestObservationQuality:

    @pytest.mark.parametrize('obs', TestData.Observation, ids=lambda o: o.id)
    def test_has_value_with_unit(self, obs):
        if obs.valueQuantity:
            assert obs.valueQuantity.value is not None, f'Observation {obs.id} has no value'
            assert obs.valueQuantity.unit, f'Observation {obs.id} has no unit'

    def test_values_in_clinically_plausible_range(self):
        issues = [] # type: list[str]
        for obs in TestData.Observation:
            if not obs.valueQuantity or obs.valueQuantity.value is None:
                continue
            code = str(obs.code.coding[0].code)
            value = float(obs.valueQuantity.value)
            if code in _loinc_ranges:
                lo, hi = _loinc_ranges[code]
                if not (lo <= value <= hi):
                    issues.append(
                        f'{obs.id} ({code}): value {value} outside [{lo}, {hi}]')

        assert not issues, f'{len(issues)} out-of-range observations:\n' + '\n'.join(issues[:20])

# ################################################################################################################################
# ################################################################################################################################

class TestEncounterQuality:

    @pytest.mark.parametrize('enc', TestData.Encounter, ids=lambda e: e.id)
    def test_period_start_before_end(self, enc):
        start = _parse_fhir_dt(enc.period.start)
        end = _parse_fhir_dt(enc.period.end)
        assert start is not None, f'Cannot parse start: {enc.period.start}'
        assert end is not None, f'Cannot parse end: {enc.period.end}'
        assert start < end, f'Start {start} not before end {end}'

    @pytest.mark.parametrize('enc', TestData.Encounter, ids=lambda e: e.id)
    def test_outpatient_duration_under_24h(self, enc):
        start = _parse_fhir_dt(enc.period.start)
        end = _parse_fhir_dt(enc.period.end)
        if start and end:
            duration_hours = (end - start).total_seconds() / 3600
            assert duration_hours < 24, f'Outpatient encounter {enc.id} is {duration_hours:.1f}h'

    @pytest.mark.parametrize('enc', TestData.Encounter, ids=lambda e: e.id)
    def test_has_status_and_class(self, enc):
        assert str(enc.status) == 'finished'
        assert enc.class_, 'Encounter missing class'

# ################################################################################################################################
# ################################################################################################################################

class TestNameScripts:

    def test_patient_names_use_allowed_scripts(self):
        issues = [] # type: list[str]
        for patient in TestData.Patient:
            for hn in patient.name:
                family = str(hn.family) if hn.family else ''
                if family and not _is_valid_name_script(family):
                    issues.append(f'{patient.id}: family name {family!r} uses disallowed script')
                if hn.given:
                    for g in hn.given:
                        g_str = str(g)
                        if g_str and not _is_valid_name_script(g_str):
                            issues.append(f'{patient.id}: given name {g_str!r} uses disallowed script')

        assert not issues, f'{len(issues)} name script violations:\n' + '\n'.join(issues[:20])

    def test_practitioner_names_use_allowed_scripts(self):
        issues = [] # type: list[str]
        for pract in TestData.Practitioner:
            for hn in pract.name:
                family = str(hn.family) if hn.family else ''
                if family and not _is_valid_name_script(family):
                    issues.append(f'{pract.id}: family {family!r} uses disallowed script')
                if hn.given:
                    for g in hn.given:
                        g_str = str(g)
                        if g_str and not _is_valid_name_script(g_str):
                            issues.append(f'{pract.id}: given {g_str!r} uses disallowed script')

        assert not issues, f'{len(issues)} name script violations:\n' + '\n'.join(issues[:20])

# ################################################################################################################################
# ################################################################################################################################

class TestDistinctInstances:

    def test_unique_patient_names(self):
        names = [] # type: list[str]
        for inst in Scenarios.wellness_visit:
            name_text = str(inst.patient.name[0].text)
            names.append(name_text)
        assert len(set(names)) == len(names), \
            f'Duplicate patient names found: {[n for n in names if names.count(n) > 1]}'

    def test_unique_patient_mrns(self):
        mrns = [] # type: list[str]
        for inst in Scenarios.wellness_visit:
            for ident in inst.patient.identifier:
                if str(ident.system) == 'http://example.org/mrn':
                    mrns.append(str(ident.value))
        assert len(set(mrns)) == len(mrns), \
            f'Duplicate MRNs found: {[m for m in mrns if mrns.count(m) > 1]}'

    def test_unique_patient_ids(self):
        ids = [inst.patient.id for inst in Scenarios.wellness_visit]
        assert len(set(ids)) == len(ids), 'Duplicate patient IDs found'

# ################################################################################################################################
# ################################################################################################################################

class TestTrendingLabValues:

    def test_trending_values_are_monotonic(self):
        issues = [] # type: list[str]
        for inst in Scenarios.wellness_visit:
            for code in _trending_loinc_codes:
                obs_for_code = [
                    o for o in inst.observations
                    if str(o.code.coding[0].code) == code
                ]
                obs_for_code.sort(key=lambda o: str(o.effectiveDateTime))
                values = [float(o.valueQuantity.value) for o in obs_for_code]
                if len(values) >= 2 and not _is_monotonic(values):
                    display = str(obs_for_code[0].code.text)
                    issues.append(
                        f'{inst.patient.id}/{display} ({code}): values {values} not monotonic')

        assert not issues, f'{len(issues)} non-monotonic trends:\n' + '\n'.join(issues[:20])

    def test_trending_values_have_3_data_points(self):
        for inst in Scenarios.wellness_visit:
            for code in _trending_loinc_codes:
                obs_for_code = [
                    o for o in inst.observations
                    if str(o.code.coding[0].code) == code
                ]
                assert len(obs_for_code) == 3, \
                    f'{inst.patient.id}/{code}: expected 3 trending values, got {len(obs_for_code)}'

# ################################################################################################################################
# ################################################################################################################################

class TestOrganizationQuality:

    @pytest.mark.parametrize('org', TestData.Organization, ids=lambda o: o.id)
    def test_name_has_multiple_words(self, org):
        name = str(org.name)
        words = name.split()
        assert len(words) >= 2, f'Organization name too short: {name!r}'

    @pytest.mark.parametrize('org', TestData.Organization, ids=lambda o: o.id)
    def test_name_not_hex_or_numbers_only(self, org):
        name = str(org.name)
        assert not re.match(r'^[0-9a-fA-F\s\-]+$', name), \
            f'Organization name looks like hex/numbers: {name!r}'

# ################################################################################################################################
# ################################################################################################################################

class TestDocumentReferenceQuality:

    def test_clinical_content_not_empty(self):
        for inst in Scenarios.wellness_visit:
            dr = inst.document_ref
            assert dr.content, f'DocumentReference {dr.id} has no content'
            attachment = dr.content[0].attachment
            assert attachment.data, f'DocumentReference {dr.id} has empty attachment data'
            assert len(str(attachment.data)) > 10, \
                f'DocumentReference {dr.id} attachment data too short'

# ################################################################################################################################
# ################################################################################################################################
