from __future__ import annotations

from zato.fhir.r4_0_1.dk_core.v3_5_0.extensions import (
    CONDITION_LAST_ASSERTED_DATE_URL,
    NOT_FOLLOWED_ANYMORE_URL,
    DK_CORE_PLANNED_END_DATE_URL,
    DK_CORE_DOCUMENTREFERENCE_VERSION_ID_EXTENSION_URL,
    DK_CORE_PLANNED_START_DATE_URL,
    DK_CORE_MUNICIPALITY_CODES_URL,
    DK_CORE_REGIONAL_SUB_DIVISION_CODES_URL,
    DK_CORE_CARE_PROVIDER_URL,
)

from zato.fhir.r4_0_1.dk_core.v3_5_0.resources import (
    Address,
    Condition,
    Element,
    Encounter,
    Patient,
)


class TestImports:

    def test_address_is_importable(self):
        assert Address is not None

    def test_condition_is_importable(self):
        assert Condition is not None

    def test_element_is_importable(self):
        assert Element is not None

    def test_encounter_is_importable(self):
        assert Encounter is not None

    def test_patient_is_importable(self):
        assert Patient is not None


class TestURLConstants:

    def test_condition_last_asserted_date_url(self):
        assert CONDITION_LAST_ASSERTED_DATE_URL == 'http://hl7.dk/fhir/core/StructureDefinition/ConditionLastAssertedDate'

    def test_not_followed_anymore_url(self):
        assert NOT_FOLLOWED_ANYMORE_URL == 'http://hl7.dk/fhir/core/StructureDefinition/NotFollowedAnymore'

    def test_dk_core_planned_end_date_url(self):
        assert DK_CORE_PLANNED_END_DATE_URL == 'http://hl7.dk/fhir/core/StructureDefinition/dk-core-planned-end-date'

    def test_dk_core_documentreference_version_id_extension_url(self):
        assert DK_CORE_DOCUMENTREFERENCE_VERSION_ID_EXTENSION_URL == 'http://hl7.dk/fhir/core/StructureDefinition/dk-core-documentreference-version-id-extension'

    def test_dk_core_planned_start_date_url(self):
        assert DK_CORE_PLANNED_START_DATE_URL == 'http://hl7.dk/fhir/core/StructureDefinition/dk-core-planned-start-date'

    def test_dk_core_municipality_codes_url(self):
        assert DK_CORE_MUNICIPALITY_CODES_URL == 'http://hl7.dk/fhir/core/StructureDefinition/dk-core-municipalityCodes'

    def test_dk_core_regional_sub_division_codes_url(self):
        assert DK_CORE_REGIONAL_SUB_DIVISION_CODES_URL == 'http://hl7.dk/fhir/core/StructureDefinition/dk-core-RegionalSubDivisionCodes'

    def test_dk_core_care_provider_url(self):
        assert DK_CORE_CARE_PROVIDER_URL == 'http://hl7.dk/fhir/core/StructureDefinition/dk-core-care-provider'


class TestPropertyAccess:

    def test_address_dk_core_municipality_codes_roundtrip(self):
        r = Address()
        r.dk_core_municipality_codes = "test-value"
        result = r.dk_core_municipality_codes
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_address_dk_core_regional_sub_division_codes_roundtrip(self):
        r = Address()
        r.dk_core_regional_sub_division_codes = "test-value"
        result = r.dk_core_regional_sub_division_codes
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_condition_last_asserted_date_roundtrip(self):
        r = Condition()
        r.condition_last_asserted_date = "test-value"
        result = r.condition_last_asserted_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_condition_not_followed_anymore_roundtrip(self):
        r = Condition()
        r.not_followed_anymore = "test-value"
        result = r.not_followed_anymore
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_element_dk_core_documentreference_version_id_extension_roundtrip(self):
        r = Element()
        r.dk_core_documentreference_version_id_extension = "test-value"
        result = r.dk_core_documentreference_version_id_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_dk_core_planned_end_date_roundtrip(self):
        r = Encounter()
        r.dk_core_planned_end_date = "test-value"
        result = r.dk_core_planned_end_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_dk_core_planned_start_date_roundtrip(self):
        r = Encounter()
        r.dk_core_planned_start_date = "test-value"
        result = r.dk_core_planned_start_date
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_encounter_dk_core_care_provider_roundtrip(self):
        r = Encounter()
        r.dk_core_care_provider = "test-value"
        result = r.dk_core_care_provider
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_dk_core_municipality_codes_roundtrip(self):
        r = Patient()
        r.dk_core_municipality_codes = "test-value"
        result = r.dk_core_municipality_codes
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_patient_dk_core_regional_sub_division_codes_roundtrip(self):
        r = Patient()
        r.dk_core_regional_sub_division_codes = "test-value"
        result = r.dk_core_regional_sub_division_codes
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

