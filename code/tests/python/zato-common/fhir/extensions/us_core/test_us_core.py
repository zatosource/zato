from __future__ import annotations

from zato.fhir.r4_0_1.us_core.v8_0_0.extensions import (
    ETHNICITY_URL,
    QUESTIONNAIRE_URI_URL,
    MEDICATION_ADHERENCE_URL,
    USCDI_REQUIREMENT_URL,
    SEX_URL,
    DIRECT_URL,
    RACE_URL,
    BIRTHSEX_URL,
    GENDER_IDENTITY_URL,
    JURISDICTION_URL,
    AUTHENTICATION_TIME_URL,
    TRIBAL_AFFILIATION_URL,
    INTERPRETER_NEEDED_URL,
)

from zato.fhir.r4_0_1.us_core.v8_0_0.resources import (
    BiologicallyDerivedProduct,
    BodyStructure,
    Claim,
    Consent,
    ContactPoint,
    Contract,
    Coverage,
    Device,
    DeviceMetric,
    DocumentReference,
    ElementDefinition,
    Encounter,
    Endpoint,
    ExplanationOfBenefit,
    FamilyMemberHistory,
    Group,
    HealthcareService,
    InsurancePlan,
    Invoice,
    Location,
    MedicationRequest,
    Organization,
    OrganizationAffiliation,
    Patient,
    Person,
    Practitioner,
    PractitionerRole,
    QuestionnaireResponse,
    RelatedPerson,
    Specimen,
    Substance,
)


class TestImports:

    def test_biologicallyderivedproduct_is_importable(self):
        assert BiologicallyDerivedProduct is not None

    def test_bodystructure_is_importable(self):
        assert BodyStructure is not None

    def test_claim_is_importable(self):
        assert Claim is not None

    def test_consent_is_importable(self):
        assert Consent is not None

    def test_contactpoint_is_importable(self):
        assert ContactPoint is not None

    def test_contract_is_importable(self):
        assert Contract is not None

    def test_coverage_is_importable(self):
        assert Coverage is not None

    def test_device_is_importable(self):
        assert Device is not None

    def test_devicemetric_is_importable(self):
        assert DeviceMetric is not None

    def test_documentreference_is_importable(self):
        assert DocumentReference is not None

    def test_elementdefinition_is_importable(self):
        assert ElementDefinition is not None

    def test_encounter_is_importable(self):
        assert Encounter is not None

    def test_endpoint_is_importable(self):
        assert Endpoint is not None

    def test_explanationofbenefit_is_importable(self):
        assert ExplanationOfBenefit is not None

    def test_familymemberhistory_is_importable(self):
        assert FamilyMemberHistory is not None

    def test_group_is_importable(self):
        assert Group is not None

    def test_healthcareservice_is_importable(self):
        assert HealthcareService is not None

    def test_insuranceplan_is_importable(self):
        assert InsurancePlan is not None

    def test_invoice_is_importable(self):
        assert Invoice is not None

    def test_location_is_importable(self):
        assert Location is not None

    def test_medicationrequest_is_importable(self):
        assert MedicationRequest is not None

    def test_organization_is_importable(self):
        assert Organization is not None

    def test_organizationaffiliation_is_importable(self):
        assert OrganizationAffiliation is not None

    def test_patient_is_importable(self):
        assert Patient is not None

    def test_person_is_importable(self):
        assert Person is not None

    def test_practitioner_is_importable(self):
        assert Practitioner is not None

    def test_practitionerrole_is_importable(self):
        assert PractitionerRole is not None

    def test_questionnaireresponse_is_importable(self):
        assert QuestionnaireResponse is not None

    def test_relatedperson_is_importable(self):
        assert RelatedPerson is not None

    def test_specimen_is_importable(self):
        assert Specimen is not None

    def test_substance_is_importable(self):
        assert Substance is not None


class TestURLConstants:

    def test_ethnicity_url(self):
        assert ETHNICITY_URL == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity'

    def test_questionnaire_uri_url(self):
        assert QUESTIONNAIRE_URI_URL == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-extension-questionnaire-uri'

    def test_medication_adherence_url(self):
        assert MEDICATION_ADHERENCE_URL == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-medication-adherence'

    def test_uscdi_requirement_url(self):
        assert USCDI_REQUIREMENT_URL == 'http://hl7.org/fhir/us/core/StructureDefinition/uscdi-requirement'

    def test_sex_url(self):
        assert SEX_URL == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-sex'

    def test_direct_url(self):
        assert DIRECT_URL == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-direct'

    def test_race_url(self):
        assert RACE_URL == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race'

    def test_birthsex_url(self):
        assert BIRTHSEX_URL == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex'

    def test_gender_identity_url(self):
        assert GENDER_IDENTITY_URL == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-genderIdentity'

    def test_jurisdiction_url(self):
        assert JURISDICTION_URL == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-jurisdiction'

    def test_authentication_time_url(self):
        assert AUTHENTICATION_TIME_URL == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-authentication-time'

    def test_tribal_affiliation_url(self):
        assert TRIBAL_AFFILIATION_URL == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-tribal-affiliation'

    def test_interpreter_needed_url(self):
        assert INTERPRETER_NEEDED_URL == 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-interpreter-needed'


class TestPropertyAccess:

    def test_biologicallyderivedproduct_jurisdiction_roundtrip(self):
        r = BiologicallyDerivedProduct()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_bodystructure_jurisdiction_roundtrip(self):
        r = BodyStructure()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_claim_jurisdiction_roundtrip(self):
        r = Claim()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_consent_jurisdiction_roundtrip(self):
        r = Consent()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactpoint_direct_roundtrip(self):
        r = ContactPoint()
        r.direct = "test-value"
        result = r.direct
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contract_jurisdiction_roundtrip(self):
        r = Contract()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_coverage_jurisdiction_roundtrip(self):
        r = Coverage()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_device_jurisdiction_roundtrip(self):
        r = Device()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_devicemetric_jurisdiction_roundtrip(self):
        r = DeviceMetric()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_documentreference_authentication_time_roundtrip(self):
        r = DocumentReference()
        r.authentication_time = "test-value"
        result = r.authentication_time
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_uscdi_requirement_roundtrip(self):
        r = ElementDefinition()
        r.uscdi_requirement = "test-value"
        result = r.uscdi_requirement
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_interpreter_needed_roundtrip(self):
        r = Encounter()
        r.interpreter_needed = "test-value"
        result = r.interpreter_needed
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_endpoint_jurisdiction_roundtrip(self):
        r = Endpoint()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_explanationofbenefit_jurisdiction_roundtrip(self):
        r = ExplanationOfBenefit()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_ethnicity_roundtrip(self):
        r = FamilyMemberHistory()
        r.ethnicity = "test-value"
        result = r.ethnicity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_race_roundtrip(self):
        r = FamilyMemberHistory()
        r.race = "test-value"
        result = r.race
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_familymemberhistory_tribal_affiliation_roundtrip(self):
        r = FamilyMemberHistory()
        r.tribal_affiliation = "test-value"
        result = r.tribal_affiliation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_group_jurisdiction_roundtrip(self):
        r = Group()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_healthcareservice_jurisdiction_roundtrip(self):
        r = HealthcareService()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_insuranceplan_jurisdiction_roundtrip(self):
        r = InsurancePlan()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_invoice_jurisdiction_roundtrip(self):
        r = Invoice()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_location_jurisdiction_roundtrip(self):
        r = Location()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_medicationrequest_medication_adherence_roundtrip(self):
        r = MedicationRequest()
        r.medication_adherence = "test-value"
        result = r.medication_adherence
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_jurisdiction_roundtrip(self):
        r = Organization()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organizationaffiliation_jurisdiction_roundtrip(self):
        r = OrganizationAffiliation()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_ethnicity_roundtrip(self):
        r = Patient()
        r.ethnicity = "test-value"
        result = r.ethnicity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_sex_roundtrip(self):
        r = Patient()
        r.sex = "test-value"
        result = r.sex
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_race_roundtrip(self):
        r = Patient()
        r.race = "test-value"
        result = r.race
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_birthsex_roundtrip(self):
        r = Patient()
        r.birthsex = "test-value"
        result = r.birthsex
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_gender_identity_roundtrip(self):
        r = Patient()
        r.gender_identity = "test-value"
        result = r.gender_identity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_jurisdiction_roundtrip(self):
        r = Patient()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_tribal_affiliation_roundtrip(self):
        r = Patient()
        r.tribal_affiliation = "test-value"
        result = r.tribal_affiliation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_interpreter_needed_roundtrip(self):
        r = Patient()
        r.interpreter_needed = "test-value"
        result = r.interpreter_needed
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_person_ethnicity_roundtrip(self):
        r = Person()
        r.ethnicity = "test-value"
        result = r.ethnicity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_person_race_roundtrip(self):
        r = Person()
        r.race = "test-value"
        result = r.race
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_person_gender_identity_roundtrip(self):
        r = Person()
        r.gender_identity = "test-value"
        result = r.gender_identity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_person_jurisdiction_roundtrip(self):
        r = Person()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_person_tribal_affiliation_roundtrip(self):
        r = Person()
        r.tribal_affiliation = "test-value"
        result = r.tribal_affiliation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_ethnicity_roundtrip(self):
        r = Practitioner()
        r.ethnicity = "test-value"
        result = r.ethnicity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_race_roundtrip(self):
        r = Practitioner()
        r.race = "test-value"
        result = r.race
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_gender_identity_roundtrip(self):
        r = Practitioner()
        r.gender_identity = "test-value"
        result = r.gender_identity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_jurisdiction_roundtrip(self):
        r = Practitioner()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_tribal_affiliation_roundtrip(self):
        r = Practitioner()
        r.tribal_affiliation = "test-value"
        result = r.tribal_affiliation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_interpreter_needed_roundtrip(self):
        r = Practitioner()
        r.interpreter_needed = "test-value"
        result = r.interpreter_needed
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitionerrole_jurisdiction_roundtrip(self):
        r = PractitionerRole()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_questionnaireresponse_questionnaire_uri_roundtrip(self):
        r = QuestionnaireResponse()
        r.questionnaire_uri = "test-value"
        result = r.questionnaire_uri
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedperson_ethnicity_roundtrip(self):
        r = RelatedPerson()
        r.ethnicity = "test-value"
        result = r.ethnicity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedperson_race_roundtrip(self):
        r = RelatedPerson()
        r.race = "test-value"
        result = r.race
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedperson_gender_identity_roundtrip(self):
        r = RelatedPerson()
        r.gender_identity = "test-value"
        result = r.gender_identity
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedperson_jurisdiction_roundtrip(self):
        r = RelatedPerson()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedperson_tribal_affiliation_roundtrip(self):
        r = RelatedPerson()
        r.tribal_affiliation = "test-value"
        result = r.tribal_affiliation
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_relatedperson_interpreter_needed_roundtrip(self):
        r = RelatedPerson()
        r.interpreter_needed = "test-value"
        result = r.interpreter_needed
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_specimen_jurisdiction_roundtrip(self):
        r = Specimen()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_substance_jurisdiction_roundtrip(self):
        r = Substance()
        r.jurisdiction = "test-value"
        result = r.jurisdiction
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

