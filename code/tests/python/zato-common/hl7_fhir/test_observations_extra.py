# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from conftest import convert, full_url_of, one_resource, organization_named, segment

# ################################################################################################################################
# ################################################################################################################################

# A minimal envelope every OBX test builds on.
MSH = 'MSH|^~\\&|LAB|GENHOSP|EHR|GENHOSP|20260315120000||ORU^R01^ORU_R01|MSG00001|P|2.5.1'
PID = 'PID|1||12345^^^GENHOSP^MR||Smith^John|||M'
OBR = 'OBR|1|PL1|FIL1|57021-8^CBC^LN'

# ################################################################################################################################
# ################################################################################################################################

class TestOBXExtraFields:
    """ The OBX fields beyond the value itself - analysis time, body site,
    instance identifier and the performing organization.
    """

    def test_analysis_time_keeps_its_own_extension(self) -> 'None':
        obx = segment('OBX', {1: '1', 2: 'NM', 3: '718-7^Hemoglobin^LN', 5: '13.2', 11: 'F', 19: '20260315113000'})

        bundle = convert(MSH, PID, OBR, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['extension'] == [{
            'url': 'urn:zato:hl7v2:extension/observation/analysis-time',
            'valueDateTime': '2026-03-15T11:30:00+00:00',
        }]

# ################################################################################################################################

    def test_analysis_time_that_is_no_time_is_preserved(self) -> 'None':
        obx = segment('OBX', {1: '1', 2: 'NM', 3: '718-7^Hemoglobin^LN', 5: '13.2', 11: 'F', 19: 'BENCH-2'})

        bundle = convert(MSH, PID, OBR, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['extension'] == [{
            'url': 'urn:zato:hl7v2:extension/unmapped/OBX-19',
            'valueString': 'BENCH-2',
        }]

# ################################################################################################################################

    def test_body_site_keeps_its_coding(self) -> 'None':
        obx = segment('OBX', {1: '1', 2: 'ST', 3: '6462-6^Wound Culture^LN', 5: 'Moderate growth', 11: 'F', 20: 'LA^Left arm^L'})

        bundle = convert(MSH, PID, OBR, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['bodySite'] == {
            'coding': [{'code': 'LA', 'display': 'Left arm'}],
            'text': 'Left arm',
        }

# ################################################################################################################################

    def test_instance_identifier_is_a_filler_one(self) -> 'None':
        obx = segment('OBX', {1: '1', 2: 'NM', 3: '718-7^Hemoglobin^LN', 5: '13.2', 11: 'F', 21: 'OBS001^LAB'})

        bundle = convert(MSH, PID, OBR, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['identifier'] == [{
            'value': 'OBS001',
            'system': 'urn:zato:hl7v2:authority:LAB',
            'type': {
                'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v2-0203', 'code': 'FILL'}],
            },
        }]

# ################################################################################################################################

    def test_performing_organization_with_its_address(self) -> 'None':
        obx = segment('OBX', {
            1: '1',
            2: 'NM',
            3: '718-7^Hemoglobin^LN',
            5: '13.2',
            11: 'F',
            23: 'Acme Lab^^^^^^^^^ACME01',
            24: '123 Lab St^^Metropolis^ST^12345',
        })

        bundle = convert(MSH, PID, OBR, obx)
        observation = one_resource(bundle, 'Observation')

        organization = organization_named(bundle, 'Acme Lab')
        organization_url = full_url_of(bundle, organization)

        # The organization is a performer and carries the address along.
        assert {'reference': organization_url} in observation['performer']

        assert organization['identifier'] == [{'value': 'ACME01'}]
        assert organization['address'] == [{
            'line': ['123 Lab St'],
            'city': 'Metropolis',
            'state': 'ST',
            'postalCode': '12345',
        }]

# ################################################################################################################################

    def test_address_with_no_organization_is_preserved(self) -> 'None':
        obx = segment('OBX', {1: '1', 2: 'NM', 3: '718-7^Hemoglobin^LN', 5: '13.2', 11: 'F', 24: '123 Lab St^^Metropolis'})

        bundle = convert(MSH, PID, OBR, obx)
        observation = one_resource(bundle, 'Observation')

        assert observation['extension'] == [{
            'url': 'urn:zato:hl7v2:extension/unmapped/OBX-24',
            'valueString': '123 Lab St^^Metropolis',
        }]

# ################################################################################################################################
# ################################################################################################################################
