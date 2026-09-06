# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from conftest import convert, one_resource, segment

# ################################################################################################################################
# ################################################################################################################################

# A minimal envelope every PID test builds on.
MSH = 'MSH|^~\\&|EHR|GENHOSP|CARE|GENHOSP|20260315120000||ADT^A01^ADT_A01|MSG00001|P|2.5.1'

# ################################################################################################################################
# ################################################################################################################################

class TestPIDCitizenship:
    """ PID-26 citizenships go to the standard patient-citizenship extension, one per repetition.
    """

    def test_each_citizenship_gets_its_own_extension(self) -> 'None':
        pid = segment('PID', {1: '1', 3: '12345^^^GENHOSP^MR', 5: 'Smith^John', 26: 'USA^United States^ISO3166~POL^Poland^ISO3166'})

        bundle = convert(MSH, pid)
        patient = one_resource(bundle, 'Patient')

        extensions = patient['extension']

        citizenships = []

        for item in extensions:
            if item['url'] == 'http://hl7.org/fhir/StructureDefinition/patient-citizenship':
                citizenships.append(item)

        assert len(citizenships) == 2

        first, second = citizenships

        first_code = first['extension'][0]
        first_concept = first_code['valueCodeableConcept']
        first_coding = first_concept['coding'][0]

        assert first_code['url'] == 'code'
        assert first_coding['code'] == 'USA'
        assert first_coding['system'] == 'urn:iso:std:iso:3166'

        second_code = second['extension'][0]
        second_concept = second_code['valueCodeableConcept']
        second_coding = second_concept['coding'][0]

        assert second_coding['code'] == 'POL'

# ################################################################################################################################
# ################################################################################################################################

class TestPIDCounty:
    """ PID-12 - the county - fills the first address's district when it is free.
    """

    def test_county_fills_the_district(self) -> 'None':
        pid = segment('PID', {1: '1', 3: '12345^^^GENHOSP^MR', 5: 'Smith^John', 11: '10 Main St^^Metropolis^ST^12345', 12: 'Greene'})

        bundle = convert(MSH, pid)
        patient = one_resource(bundle, 'Patient')

        address = patient['address'][0]
        assert address['district'] == 'Greene'

        assert 'extension' not in patient

# ################################################################################################################################

    def test_county_with_no_address_is_preserved(self) -> 'None':
        pid = segment('PID', {1: '1', 3: '12345^^^GENHOSP^MR', 5: 'Smith^John', 12: 'Greene'})

        bundle = convert(MSH, pid)
        patient = one_resource(bundle, 'Patient')

        assert 'address' not in patient

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/PID-12',
            'valueString': 'Greene',
        } in patient['extension']

# ################################################################################################################################

    def test_county_defers_to_a_district_already_there(self) -> 'None':
        # XAD-9 carries its own county, which becomes the district first.
        pid = segment('PID', {1: '1', 3: '12345^^^GENHOSP^MR', 5: 'Smith^John', 11: '10 Main St^^Metropolis^ST^12345^^^^Albany', 12: 'Greene'})

        bundle = convert(MSH, pid)
        patient = one_resource(bundle, 'Patient')

        address = patient['address'][0]
        assert address['district'] == 'Albany'

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/PID-12',
            'valueString': 'Greene',
        } in patient['extension']

# ################################################################################################################################
# ################################################################################################################################
