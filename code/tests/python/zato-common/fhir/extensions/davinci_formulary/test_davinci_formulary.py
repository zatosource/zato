from __future__ import annotations

from zato.fhir.r4_0_1.davinci_formulary.v2_1_0.extensions import (
    AVAILABILITY_STATUS_EXTENSION_URL,
    QUANTITY_LIMIT_EXTENSION_URL,
    PHARMACY_BENEFIT_TYPE_EXTENSION_URL,
    PRIOR_AUTHORIZATION_EXTENSION_URL,
    QUANTITY_LIMIT_DETAIL_EXTENSION_URL,
    PRIOR_AUTHORIZATION_NEW_STARTS_ONLY_EXTENSION_URL,
    FORMULARY_REFERENCE_EXTENSION_URL,
    DRUG_TIER_ID_EXTENSION_URL,
    ADDITIONAL_COVERAGE_INFORMATION_EXTENSION_URL,
    STEP_THERAPY_LIMIT_NEW_STARTS_ONLY_EXTENSION_URL,
    STEP_THERAPY_LIMIT_EXTENSION_URL,
    AVAILABILITY_PERIOD_EXTENSION_URL,
)

from zato.fhir.r4_0_1.davinci_formulary.v2_1_0.resources import (
    Basic,
    InsurancePlan,
)


class TestImports:

    def test_basic_is_importable(self):
        assert Basic is not None

    def test_insuranceplan_is_importable(self):
        assert InsurancePlan is not None


class TestURLConstants:

    def test_availability_status_extension_url(self):
        assert AVAILABILITY_STATUS_EXTENSION_URL == 'http://hl7.org/fhir/us/davinci-drug-formulary/StructureDefinition/usdf-AvailabilityStatus-extension'

    def test_quantity_limit_extension_url(self):
        assert QUANTITY_LIMIT_EXTENSION_URL == 'http://hl7.org/fhir/us/davinci-drug-formulary/StructureDefinition/usdf-QuantityLimit-extension'

    def test_pharmacy_benefit_type_extension_url(self):
        assert PHARMACY_BENEFIT_TYPE_EXTENSION_URL == 'http://hl7.org/fhir/us/davinci-drug-formulary/StructureDefinition/usdf-PharmacyBenefitType-extension'

    def test_prior_authorization_extension_url(self):
        assert PRIOR_AUTHORIZATION_EXTENSION_URL == 'http://hl7.org/fhir/us/davinci-drug-formulary/StructureDefinition/usdf-PriorAuthorization-extension'

    def test_quantity_limit_detail_extension_url(self):
        assert QUANTITY_LIMIT_DETAIL_EXTENSION_URL == 'http://hl7.org/fhir/us/davinci-drug-formulary/StructureDefinition/usdf-QuantityLimitDetail-extension'

    def test_prior_authorization_new_starts_only_extension_url(self):
        assert PRIOR_AUTHORIZATION_NEW_STARTS_ONLY_EXTENSION_URL == 'http://hl7.org/fhir/us/davinci-drug-formulary/StructureDefinition/usdf-PriorAuthorizationNewStartsOnly-extension'

    def test_formulary_reference_extension_url(self):
        assert FORMULARY_REFERENCE_EXTENSION_URL == 'http://hl7.org/fhir/us/davinci-drug-formulary/StructureDefinition/usdf-FormularyReference-extension'

    def test_drug_tier_id_extension_url(self):
        assert DRUG_TIER_ID_EXTENSION_URL == 'http://hl7.org/fhir/us/davinci-drug-formulary/StructureDefinition/usdf-DrugTierID-extension'

    def test_additional_coverage_information_extension_url(self):
        assert ADDITIONAL_COVERAGE_INFORMATION_EXTENSION_URL == 'http://hl7.org/fhir/us/davinci-drug-formulary/StructureDefinition/usdf-AdditionalCoverageInformation-extension'

    def test_step_therapy_limit_new_starts_only_extension_url(self):
        assert STEP_THERAPY_LIMIT_NEW_STARTS_ONLY_EXTENSION_URL == 'http://hl7.org/fhir/us/davinci-drug-formulary/StructureDefinition/usdf-StepTherapyLimitNewStartsOnly-extension'

    def test_step_therapy_limit_extension_url(self):
        assert STEP_THERAPY_LIMIT_EXTENSION_URL == 'http://hl7.org/fhir/us/davinci-drug-formulary/StructureDefinition/usdf-StepTherapyLimit-extension'

    def test_availability_period_extension_url(self):
        assert AVAILABILITY_PERIOD_EXTENSION_URL == 'http://hl7.org/fhir/us/davinci-drug-formulary/StructureDefinition/usdf-AvailabilityPeriod-extension'


class TestPropertyAccess:

    def test_basic_availability_status_extension_roundtrip(self):
        r = Basic()
        r.availability_status_extension = "test-value"
        result = r.availability_status_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_quantity_limit_extension_roundtrip(self):
        r = Basic()
        r.quantity_limit_extension = "test-value"
        result = r.quantity_limit_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_pharmacy_benefit_type_extension_roundtrip(self):
        r = Basic()
        r.pharmacy_benefit_type_extension = "test-value"
        result = r.pharmacy_benefit_type_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_prior_authorization_extension_roundtrip(self):
        r = Basic()
        r.prior_authorization_extension = "test-value"
        result = r.prior_authorization_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_quantity_limit_detail_extension_roundtrip(self):
        r = Basic()
        r.quantity_limit_detail_extension = "test-value"
        result = r.quantity_limit_detail_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_prior_authorization_new_starts_only_extension_roundtrip(self):
        r = Basic()
        r.prior_authorization_new_starts_only_extension = "test-value"
        result = r.prior_authorization_new_starts_only_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_formulary_reference_extension_roundtrip(self):
        r = Basic()
        r.formulary_reference_extension = "test-value"
        result = r.formulary_reference_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_drug_tier_id_extension_roundtrip(self):
        r = Basic()
        r.drug_tier_id_extension = "test-value"
        result = r.drug_tier_id_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_additional_coverage_information_extension_roundtrip(self):
        r = Basic()
        r.additional_coverage_information_extension = "test-value"
        result = r.additional_coverage_information_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_step_therapy_limit_new_starts_only_extension_roundtrip(self):
        r = Basic()
        r.step_therapy_limit_new_starts_only_extension = "test-value"
        result = r.step_therapy_limit_new_starts_only_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_step_therapy_limit_extension_roundtrip(self):
        r = Basic()
        r.step_therapy_limit_extension = "test-value"
        result = r.step_therapy_limit_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_basic_availability_period_extension_roundtrip(self):
        r = Basic()
        r.availability_period_extension = "test-value"
        result = r.availability_period_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_insuranceplan_formulary_reference_extension_roundtrip(self):
        r = InsurancePlan()
        r.formulary_reference_extension = "test-value"
        result = r.formulary_reference_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

