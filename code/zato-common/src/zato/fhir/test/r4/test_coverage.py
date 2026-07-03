# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

import json

from pathlib import Path

import pytest

from zato.fhir.test.r4._registry import Resource_To_Scenario
from zato.fhir.test.r4._scenarios import Scenario_Names

# ################################################################################################################################
# ################################################################################################################################

_spec_path = Path(__file__).resolve().parent.parent.parent / 'tests' / 'conformance' / 'r4_resource_names.json'
_data_dir = Path(__file__).resolve().parent / 'v1' / 'data'

N = 10

# Scenarios that have been implemented in the generator
_implemented_scenarios = set(Scenario_Names)

# Resource types expected from each implemented scenario
_expected_types_by_scenario = {
    'wellness_visit': {
        'Patient', 'Practitioner', 'PractitionerRole', 'Organization', 'Location',
        'Encounter', 'Observation', 'DiagnosticReport', 'Specimen', 'Procedure',
        'ServiceRequest', 'EpisodeOfCare', 'Composition', 'DocumentReference',
        'List', 'Provenance',
    },
    'immunization_visit': {
        'Patient', 'Practitioner', 'Organization', 'Encounter', 'Immunization',
        'ImmunizationEvaluation', 'ImmunizationRecommendation', 'Medication',
        'MedicationAdministration', 'Provenance',
    },
    'medication_refill': {
        'Patient', 'Practitioner', 'Organization', 'Encounter',
        'MedicationRequest', 'MedicationDispense', 'MedicationStatement',
        'MedicationKnowledge', 'Substance', 'DetectedIssue',
    },
    'insurance_enrollment': {
        'Patient', 'Organization', 'Encounter', 'Coverage', 'InsurancePlan',
        'EnrollmentRequest', 'EnrollmentResponse', 'CoverageEligibilityRequest',
        'CoverageEligibilityResponse', 'Claim', 'ClaimResponse',
        'ExplanationOfBenefit', 'PaymentNotice', 'PaymentReconciliation',
        'Invoice', 'ChargeItem', 'ChargeItemDefinition', 'Account', 'Contract',
    },
    'appointment_booking': {
        'Patient', 'Practitioner', 'Organization', 'Encounter', 'Appointment',
        'AppointmentResponse', 'Schedule', 'Slot', 'HealthcareService', 'Endpoint',
    },
    'referral_letter': {
        'Patient', 'Practitioner', 'Organization', 'Encounter', 'Communication',
        'CommunicationRequest', 'DocumentManifest', 'Task', 'Flag',
    },
    'family_context': {
        'Patient', 'Encounter', 'RelatedPerson', 'FamilyMemberHistory', 'Person', 'Group',
    },
    'care_plan': {
        'Patient', 'Practitioner', 'Organization', 'Encounter', 'CarePlan',
        'CareTeam', 'Goal', 'RequestGroup', 'PlanDefinition', 'ActivityDefinition',
    },
    'allergy_record': {
        'Patient', 'Practitioner', 'Organization', 'Encounter',
        'AllergyIntolerance', 'ClinicalImpression', 'RiskAssessment', 'Condition', 'Consent',
    },
    'lab_panel': {
        'Patient', 'Practitioner', 'Organization', 'Encounter', 'Observation',
        'ObservationDefinition', 'Media', 'Specimen', 'SpecimenDefinition', 'NutritionOrder',
    },
    'vision_checkup': {
        'Patient', 'Practitioner', 'Organization', 'Encounter', 'VisionPrescription',
        'Device', 'DeviceDefinition', 'DeviceMetric', 'DeviceRequest', 'DeviceUseStatement',
    },
    'physical_therapy': {
        'Patient', 'Practitioner', 'Organization', 'Encounter', 'Procedure',
        'CarePlan', 'Goal', 'Questionnaire', 'QuestionnaireResponse',
    },
    'supply_order': {
        'Patient', 'Organization', 'Encounter', 'SupplyRequest', 'SupplyDelivery',
        'OrganizationAffiliation',
    },
    'research_study': {
        'Patient', 'Organization', 'Encounter', 'ResearchStudy', 'ResearchSubject',
        'ResearchDefinition', 'ResearchElementDefinition', 'Evidence', 'EvidenceVariable',
    },
    'audit_trail': {
        'Patient', 'AuditEvent', 'Provenance', 'Linkage', 'Basic', 'Binary',
        'Parameters', 'OperationOutcome',
    },
    'terminology_setup': {
        'CodeSystem', 'ValueSet', 'ConceptMap', 'NamingSystem', 'TerminologyCapabilities',
    },
    'messaging': {
        'Patient', 'MessageDefinition', 'MessageHeader', 'Bundle', 'Subscription',
    },
    'conformance': {
        'CapabilityStatement', 'OperationDefinition', 'SearchParameter',
        'CompartmentDefinition', 'StructureDefinition', 'StructureMap',
        'ImplementationGuide', 'GraphDefinition', 'ExampleScenario',
    },
    'quality_measure': {'Measure', 'MeasureReport', 'Library'},
    'test_execution': {'TestReport', 'TestScript', 'VerificationResult'},
    'vitals_profiles': {'Patient', 'Practitioner', 'Encounter', 'Observation'},
    'lipid_profiles': {'Patient', 'Practitioner', 'Encounter', 'Observation'},
    'shareable_definitions': {
        'ActivityDefinition', 'CodeSystem', 'Library', 'Measure', 'PlanDefinition', 'ValueSet',
    },
    'clinical_document': {'Patient', 'Encounter', 'Composition', 'CatalogEntry'},
    'cds_hooks': {'Patient', 'GuidanceResponse', 'RequestGroup', 'PlanDefinition'},
    'device_observation': {'Patient', 'Device', 'Observation', 'Group'},
    'genomics': {
        'Patient', 'MolecularSequence', 'BiologicallyDerivedProduct', 'BodyStructure',
        'SubstanceNucleicAcid', 'SubstancePolymer', 'SubstanceProtein',
        'SubstanceReferenceInformation', 'SubstanceSourceMaterial', 'SubstanceSpecification',
    },
    'product_registration': {
        'MedicinalProduct', 'MedicinalProductAuthorization', 'MedicinalProductIngredient',
        'MedicinalProductManufactured', 'MedicinalProductPackaged',
        'MedicinalProductPharmaceutical', 'MedicinalProductContraindication',
        'MedicinalProductIndication', 'MedicinalProductInteraction',
        'MedicinalProductUndesirableEffect',
    },
    'effect_evidence': {'EffectEvidenceSynthesis', 'RiskEvidenceSynthesis'},
    'payment': {'Patient', 'Organization', 'PaymentNotice', 'PaymentReconciliation', 'Invoice', 'Account'},
}

def _load_spec_types():
    with open(_spec_path, 'r') as f:
        return set(json.load(f))

def _collect_resource_types_from_files(scenario_dir):
    types = set() # type: set[str]
    for fp in scenario_dir.glob('*.json'):
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for key, value in data.items():
            if key.startswith('_'):
                continue
            items = value if isinstance(value, list) else [value]
            for item in items:
                if isinstance(item, dict) and 'resourceType' in item:
                    types.add(item['resourceType'])
    return types

# ################################################################################################################################
# ################################################################################################################################

class TestRegistryCoverage:

    def test_all_181_spec_types_mapped_to_scenarios(self):
        spec_types = _load_spec_types()
        registry_types = set(Resource_To_Scenario.keys())
        missing = spec_types - registry_types
        assert not missing, f'{len(missing)} resource types not in registry: {sorted(missing)}'

    def test_registry_covers_exactly_181_types(self):
        spec_types = _load_spec_types()
        assert len(spec_types) == len(Resource_To_Scenario), \
            f'Spec has {len(spec_types)} types, registry has {len(Resource_To_Scenario)}'

    def test_every_scenario_in_registry_is_defined(self):
        all_scenarios_in_registry = set() # type: set[str]
        for scenario_list in Resource_To_Scenario.values():
            all_scenarios_in_registry.update(scenario_list)
        defined = set(Scenario_Names)
        unknown = all_scenarios_in_registry - defined
        assert not unknown, f'Registry references undefined scenarios: {sorted(unknown)}'

# ################################################################################################################################
# ################################################################################################################################

class TestDataFileCoverage:

    @pytest.mark.parametrize('scenario_name', sorted(_implemented_scenarios))
    def test_scenario_has_n_files(self, scenario_name):
        scenario_dir = _data_dir / scenario_name
        assert scenario_dir.exists(), f'Missing directory: {scenario_dir}'
        files = sorted(scenario_dir.glob('*.json'))
        assert len(files) == N, f'{scenario_name}: expected {N} files, found {len(files)}'

    @pytest.mark.parametrize('scenario_name', sorted(_implemented_scenarios))
    def test_scenario_files_named_correctly(self, scenario_name):
        scenario_dir = _data_dir / scenario_name
        expected = {f'{i:03d}.json' for i in range(1, N + 1)}
        actual = {f.name for f in scenario_dir.glob('*.json')}
        assert actual == expected, f'{scenario_name}: expected files {sorted(expected)}, got {sorted(actual)}'

    @pytest.mark.parametrize('scenario_name', sorted(_expected_types_by_scenario.keys()))
    def test_scenario_resource_types_present(self, scenario_name):
        scenario_dir = _data_dir / scenario_name
        if not scenario_dir.exists():
            pytest.skip(f'{scenario_name} not generated yet')
        found = _collect_resource_types_from_files(scenario_dir)
        expected = _expected_types_by_scenario[scenario_name]
        missing = expected - found
        assert not missing, f'{scenario_name}: missing resource types: {sorted(missing)}'

    def test_every_resource_passes_from_dict_round_trip(self):
        from zato.fhir.r4_0_1 import resources as r4_mod

        failed = [] # type: list[str]
        for scenario_name in _implemented_scenarios:
            scenario_dir = _data_dir / scenario_name
            if not scenario_dir.exists():
                continue
            for fp in sorted(scenario_dir.glob('*.json')):
                with open(fp, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for key, value in data.items():
                    if key.startswith('_'):
                        continue
                    items = value if isinstance(value, list) else [value]
                    for item in items:
                        if not isinstance(item, dict) or 'resourceType' not in item:
                            continue
                        rt = item['resourceType']
                        cls = getattr(r4_mod, rt, None)
                        if cls is None:
                            failed.append(f'{fp.name}/{rt}: unknown resourceType')
                            continue
                        try:
                            obj = cls.from_dict(item)
                            d1 = obj.to_dict()
                            obj2 = cls.from_dict(d1)
                            d2 = obj2.to_dict()
                            assert d1 == d2, f'{fp.name}/{rt}/{item.get("id")}: round-trip mismatch'
                        except Exception as e:
                            failed.append(f'{fp.name}/{rt}/{item.get("id")}: {e}')

        assert not failed, f'{len(failed)} resources failed validation:\n' + '\n'.join(failed[:20])

# ################################################################################################################################
# ################################################################################################################################
