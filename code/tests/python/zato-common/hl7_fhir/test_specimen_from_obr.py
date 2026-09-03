# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings import get_conversion_warnings

# Local
from conftest import convert, one_resource, resources_of_type, segment

# ################################################################################################################################
# ################################################################################################################################

MSH_ORU = 'MSH|^~\\&|LAB|LABFAC|EHR|EHRFAC|20240517143055||ORU^R01|MSG00002|P|2.5'
MSH_ORM = 'MSH|^~\\&|EHR|EHRFAC|LAB|LABFAC|20240517143055||ORM^O01|MSG00003|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'

Unmapped = 'urn:zato:hl7v2:extension/unmapped'

Blood = {
    'coding': [{'code': 'BLD', 'display': 'Blood', 'system': 'http://terminology.hl7.org/CodeSystem/v2-0070'}],
    'text': 'Blood',
}

# ################################################################################################################################
# ################################################################################################################################

class TestSpecimenFromOBR:
    """ An OBR that names its specimen source describes a Specimen of its own.
    """

    def test_obr_15_builds_a_specimen(self) -> 'None':
        obr = segment('OBR', {
            1: '1', 2: 'ORD-1^EHR', 4: '24331-1^Lipid panel^LN', 7: '20240517100000', 14: '20240517101500',
            15: 'BLD&Blood&HL70070^EDTA&EDTA&HL70371^^ARM&Left arm&HL70163', 25: 'F',
        })

        bundle = convert(MSH_ORU, PID, obr)
        specimen = one_resource(bundle, 'Specimen')

        # The source name is the type, the body site and the collection time go under collection,
        # the received time is when the lab got it ..
        assert specimen['type'] == Blood
        assert specimen['collection']['bodySite']['coding'][0]['code'] == 'ARM'
        assert specimen['collection']['collectedDateTime'] == '2024-05-17T10:00:00+00:00'
        assert specimen['receivedTime'] == '2024-05-17T10:15:00+00:00'

        # .. and the report points at the specimen.
        report = one_resource(bundle, 'DiagnosticReport')
        service_request = one_resource(bundle, 'ServiceRequest')

        assert report['specimen'][0]['reference'].startswith('urn:uuid:')

        assert 'extension' not in report
        assert 'extension' not in service_request
        assert 'extension' not in specimen

        assert resources_of_type(bundle, 'Basic') == []
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_order_only_message_links_the_service_request(self) -> 'None':
        orc = segment('ORC', {1: 'NW', 2: 'ORD-1^EHR'})
        obr = segment('OBR', {1: '1', 2: 'ORD-1^EHR', 4: '24331-1^Lipid panel^LN', 15: 'BLD&Blood&HL70070'})

        bundle = convert(MSH_ORM, PID, orc, obr)

        specimen = one_resource(bundle, 'Specimen')
        service_request = one_resource(bundle, 'ServiceRequest')

        assert specimen['type'] == Blood
        assert service_request['specimen'][0]['reference'].startswith('urn:uuid:')

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_spm_takes_over_and_keeps_what_obr_added(self) -> 'None':
        obr = segment('OBR', {
            1: '1', 2: 'ORD-1^EHR', 4: '24331-1^Lipid panel^LN', 14: '20240517101500', 15: 'SER&Serum&HL70487', 25: 'F',
        })
        spm = segment('SPM', {1: '1', 2: 'SP-1^LAB', 4: 'SER^Serum^HL70487', 17: '20240517100000'})

        bundle = convert(MSH_ORU, PID, obr, spm)

        # One Specimen, the SPM's, with the received time only the OBR knew.
        specimen = one_resource(bundle, 'Specimen')

        assert specimen['identifier'] == [{'value': 'SP-1'}]
        assert specimen['type']['coding'][0]['code'] == 'SER'
        assert specimen['collection']['collectedDateTime'] == '2024-05-17T10:00:00+00:00'
        assert specimen['receivedTime'] == '2024-05-17T10:15:00+00:00'

        # An OBR source that agrees with the SPM type is not preserved twice.
        assert 'extension' not in specimen

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_spm_disagreeing_with_obr_preserves_the_obr_source(self) -> 'None':
        obr = segment('OBR', {1: '1', 2: 'ORD-1^EHR', 4: '24331-1^Lipid panel^LN', 15: 'BLD&Blood&HL70070', 25: 'F'})
        spm = segment('SPM', {1: '1', 2: 'SP-1^LAB', 4: 'SER^Serum^HL70487'})

        bundle = convert(MSH_ORU, PID, obr, spm)
        specimen = one_resource(bundle, 'Specimen')

        assert specimen['type']['coding'][0]['code'] == 'SER'
        assert {'url': f'{Unmapped}/OBR-15', 'valueString': 'BLD&Blood&HL70070'} in specimen['extension']

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################

class TestSACContainer:
    """ SAC describes the specimen's container.
    """

    def test_container_volumes_and_additive(self) -> 'None':
        obr = segment('OBR', {1: '1', 2: 'ORD-1^EHR', 4: '24331-1^Lipid panel^LN', 15: 'BLD&Blood&HL70070', 25: 'F'})
        sac = segment('SAC', {3: 'CONT-1^LAB', 21: '5', 22: '3', 24: 'mL^^UCUM', 27: 'EDTA^EDTA^HL70371'})

        bundle = convert(MSH_ORU, PID, obr, sac)
        specimen = one_resource(bundle, 'Specimen')

        container = specimen['container'][0]

        assert container['identifier'] == [{'value': 'CONT-1', 'system': 'urn:zato:hl7v2:authority:LAB'}]

        millilitres = {'system': 'http://unitsofmeasure.org', 'code': 'mL', 'unit': 'mL'}

        assert container['capacity'] == dict(millilitres, value=5.0)
        assert container['specimenQuantity'] == dict(millilitres, value=3.0)
        assert container['additiveCodeableConcept']['coding'][0]['code'] == 'EDTA'

        assert 'extension' not in specimen
        assert resources_of_type(bundle, 'Basic') == []
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################
