from __future__ import annotations

from zato.fhir.r4_0_1.qicore.v7_0_0.extensions import (
    CODE_OPTIONS_URL,
    KEYELEMENT_URL,
)

from zato.fhir.r4_0_1.qicore.v7_0_0.resources import (
    CodeableConcept,
    ElementDefinition,
)


class TestImports:

    def test_codeableconcept_is_importable(self):
        assert CodeableConcept is not None

    def test_elementdefinition_is_importable(self):
        assert ElementDefinition is not None


class TestURLConstants:

    def test_code_options_url(self):
        assert CODE_OPTIONS_URL == 'http://hl7.org/fhir/StructureDefinition/codeOptions'

    def test_keyelement_url(self):
        assert KEYELEMENT_URL == 'http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-keyelement'


class TestPropertyAccess:

    def test_codeableconcept_code_options_roundtrip(self):
        r = CodeableConcept()
        r.code_options = "test-value"
        result = r.code_options
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_elementdefinition_keyelement_roundtrip(self):
        r = ElementDefinition()
        r.keyelement = "test-value"
        result = r.keyelement
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

