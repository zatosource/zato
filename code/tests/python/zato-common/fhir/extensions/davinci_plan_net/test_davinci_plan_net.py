from __future__ import annotations

from zato.fhir.r4_0_1.davinci_plan_net.v1_2_0.extensions import (
    COMMUNICATION_PROFICIENCY_URL,
    ORG_DESCRIPTION_URL,
    PRACTITIONER_PERIOD_URL,
    NETWORK_REFERENCE_URL,
    VIA_INTERMEDIARY_URL,
    ENDPOINT_USECASE_URL,
    QUALIFICATION_URL,
    LOCATION_REFERENCE_URL,
    DELIVERY_METHOD_URL,
    ACCESSIBILITY_URL,
    CONTACTPOINT_AVAILABLETIME_URL,
    NEWPATIENTS_URL,
    PRACTITIONER_QUALIFICATION_URL,
)

from zato.fhir.r4_0_1.davinci_plan_net.v1_2_0.resources import (
    ContactPoint,
    Endpoint,
    HealthcareService,
    Location,
    Organization,
    OrganizationAffiliation,
    Practitioner,
    PractitionerRole,
)


class TestImports:

    def test_contactpoint_is_importable(self):
        assert ContactPoint is not None

    def test_endpoint_is_importable(self):
        assert Endpoint is not None

    def test_healthcareservice_is_importable(self):
        assert HealthcareService is not None

    def test_location_is_importable(self):
        assert Location is not None

    def test_organization_is_importable(self):
        assert Organization is not None

    def test_organizationaffiliation_is_importable(self):
        assert OrganizationAffiliation is not None

    def test_practitioner_is_importable(self):
        assert Practitioner is not None

    def test_practitionerrole_is_importable(self):
        assert PractitionerRole is not None


class TestURLConstants:

    def test_communication_proficiency_url(self):
        assert COMMUNICATION_PROFICIENCY_URL == 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/communication-proficiency'

    def test_org_description_url(self):
        assert ORG_DESCRIPTION_URL == 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/org-description'

    def test_practitioner_period_url(self):
        assert PRACTITIONER_PERIOD_URL == 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/practitioner-period'

    def test_network_reference_url(self):
        assert NETWORK_REFERENCE_URL == 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/network-reference'

    def test_via_intermediary_url(self):
        assert VIA_INTERMEDIARY_URL == 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/via-intermediary'

    def test_endpoint_usecase_url(self):
        assert ENDPOINT_USECASE_URL == 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/endpoint-usecase'

    def test_qualification_url(self):
        assert QUALIFICATION_URL == 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/qualification'

    def test_location_reference_url(self):
        assert LOCATION_REFERENCE_URL == 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/location-reference'

    def test_delivery_method_url(self):
        assert DELIVERY_METHOD_URL == 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/delivery-method'

    def test_accessibility_url(self):
        assert ACCESSIBILITY_URL == 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/accessibility'

    def test_contactpoint_availabletime_url(self):
        assert CONTACTPOINT_AVAILABLETIME_URL == 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/contactpoint-availabletime'

    def test_newpatients_url(self):
        assert NEWPATIENTS_URL == 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/newpatients'

    def test_practitioner_qualification_url(self):
        assert PRACTITIONER_QUALIFICATION_URL == 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/practitioner-qualification'


class TestPropertyAccess:

    def test_contactpoint_via_intermediary_roundtrip(self):
        r = ContactPoint()
        r.via_intermediary = "test-value"
        result = r.via_intermediary
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_contactpoint_contactpoint_availabletime_roundtrip(self):
        r = ContactPoint()
        r.contactpoint_availabletime = "test-value"
        result = r.contactpoint_availabletime
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_endpoint_endpoint_usecase_roundtrip(self):
        r = Endpoint()
        r.endpoint_usecase = "test-value"
        result = r.endpoint_usecase
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_healthcareservice_delivery_method_roundtrip(self):
        r = HealthcareService()
        r.delivery_method = "test-value"
        result = r.delivery_method
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_healthcareservice_newpatients_roundtrip(self):
        r = HealthcareService()
        r.newpatients = "test-value"
        result = r.newpatients
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_location_accessibility_roundtrip(self):
        r = Location()
        r.accessibility = "test-value"
        result = r.accessibility
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_location_newpatients_roundtrip(self):
        r = Location()
        r.newpatients = "test-value"
        result = r.newpatients
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_org_description_roundtrip(self):
        r = Organization()
        r.org_description = "test-value"
        result = r.org_description
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_qualification_roundtrip(self):
        r = Organization()
        r.qualification = "test-value"
        result = r.qualification
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organization_location_reference_roundtrip(self):
        r = Organization()
        r.location_reference = "test-value"
        result = r.location_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_organizationaffiliation_qualification_roundtrip(self):
        r = OrganizationAffiliation()
        r.qualification = "test-value"
        result = r.qualification
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_communication_proficiency_roundtrip(self):
        r = Practitioner()
        r.communication_proficiency = "test-value"
        result = r.communication_proficiency
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_practitioner_period_roundtrip(self):
        r = Practitioner()
        r.practitioner_period = "test-value"
        result = r.practitioner_period
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitioner_practitioner_qualification_roundtrip(self):
        r = Practitioner()
        r.practitioner_qualification = "test-value"
        result = r.practitioner_qualification
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitionerrole_network_reference_roundtrip(self):
        r = PractitionerRole()
        r.network_reference = "test-value"
        result = r.network_reference
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitionerrole_qualification_roundtrip(self):
        r = PractitionerRole()
        r.qualification = "test-value"
        result = r.qualification
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

    def test_practitionerrole_newpatients_roundtrip(self):
        r = PractitionerRole()
        r.newpatients = "test-value"
        result = r.newpatients
        if isinstance(result, list):
            assert result == ["test-value"]
        else:
            assert result == "test-value"

