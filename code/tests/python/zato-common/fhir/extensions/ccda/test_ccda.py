from __future__ import annotations

from zato.fhir.r4_0_1.ccda.v1_2_0.extensions import (
    DATA_ENTERER_EXTENSION_URL,
    ORDER_EXTENSION_URL,
    INFORMATION_RECIPIENT_EXTENSION_URL,
    VERSION_NUMBER_URL,
    PERFORMER_EXTENSION_URL,
    PARTICIPANT_EXTENSION_URL,
    INFORMANT_EXTENSION_URL,
    AUTHORIZATION_EXTENSION_URL,
)

from zato.fhir.r4_0_1.ccda.v1_2_0.resources import (
    Composition,
)


class TestImports:

    def test_composition_is_importable(self):
        assert Composition is not None


class TestURLConstants:

    def test_data_enterer_extension_url(self):
        assert DATA_ENTERER_EXTENSION_URL == 'http://hl7.org/fhir/us/ccda/StructureDefinition/DataEntererExtension'

    def test_order_extension_url(self):
        assert ORDER_EXTENSION_URL == 'http://hl7.org/fhir/us/ccda/StructureDefinition/OrderExtension'

    def test_information_recipient_extension_url(self):
        assert INFORMATION_RECIPIENT_EXTENSION_URL == 'http://hl7.org/fhir/us/ccda/StructureDefinition/InformationRecipientExtension'

    def test_version_number_url(self):
        assert VERSION_NUMBER_URL == 'http://hl7.org/fhir/us/ccda/StructureDefinition/VersionNumber'

    def test_performer_extension_url(self):
        assert PERFORMER_EXTENSION_URL == 'http://hl7.org/fhir/us/ccda/StructureDefinition/PerformerExtension'

    def test_participant_extension_url(self):
        assert PARTICIPANT_EXTENSION_URL == 'http://hl7.org/fhir/us/ccda/StructureDefinition/ParticipantExtension'

    def test_informant_extension_url(self):
        assert INFORMANT_EXTENSION_URL == 'http://hl7.org/fhir/us/ccda/StructureDefinition/InformantExtension'

    def test_authorization_extension_url(self):
        assert AUTHORIZATION_EXTENSION_URL == 'http://hl7.org/fhir/us/ccda/StructureDefinition/AuthorizationExtension'


class TestPropertyAccess:

    def test_composition_data_enterer_extension_roundtrip(self):
        r = Composition()
        r.data_enterer_extension = "test-value"
        result = r.data_enterer_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_order_extension_roundtrip(self):
        r = Composition()
        r.order_extension = "test-value"
        result = r.order_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_information_recipient_extension_roundtrip(self):
        r = Composition()
        r.information_recipient_extension = "test-value"
        result = r.information_recipient_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_version_number_roundtrip(self):
        r = Composition()
        r.version_number = "test-value"
        result = r.version_number
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_performer_extension_roundtrip(self):
        r = Composition()
        r.performer_extension = "test-value"
        result = r.performer_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_participant_extension_roundtrip(self):
        r = Composition()
        r.participant_extension = "test-value"
        result = r.participant_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_informant_extension_roundtrip(self):
        r = Composition()
        r.informant_extension = "test-value"
        result = r.informant_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_composition_authorization_extension_roundtrip(self):
        r = Composition()
        r.authorization_extension = "test-value"
        result = r.authorization_extension
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

