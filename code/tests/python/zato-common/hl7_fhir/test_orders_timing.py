# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings import get_conversion_warnings

# Local
from conftest import convert, one_resource, organization_named, resources_of_type, segment

# ################################################################################################################################
# ################################################################################################################################

MSH_ORU = 'MSH|^~\\&|LAB|LABFAC|EHR|EHRFAC|20240517143055||ORU^R01|MSG00002|P|2.5'
MSH_ORM = 'MSH|^~\\&|EHR|EHRFAC|LAB|LABFAC|20240517143055||ORM^O01|MSG00003|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'

Unmapped = 'urn:zato:hl7v2:extension/unmapped'

# ################################################################################################################################
# ################################################################################################################################

def _unmapped_urls(resource:'dict') -> 'list':
    """ The unmapped-field extension URLs a resource carries.
    """
    out = []

    if 'extension' in resource:
        for extension in resource['extension']:
            url = extension['url']
            if url.startswith(Unmapped):
                out.append(url)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestOBRTimes:
    """ OBR-6 is when the order was authored and OBR-7 when the service occurs.
    """

    def test_obr_6_and_7_fill_the_service_request(self) -> 'None':
        orc = segment('ORC', {1: 'NW', 2: 'ORD-1^EHR'})
        obr = segment('OBR', {1: '1', 2: 'ORD-1^EHR', 4: '24331-1^Lipid panel^LN', 6: '20240517080000', 7: '20240517100000'})

        bundle = convert(MSH_ORM, PID, orc, obr)
        service_request = one_resource(bundle, 'ServiceRequest')

        assert service_request['authoredOn'] == '2024-05-17T08:00:00+00:00'
        assert service_request['occurrenceDateTime'] == '2024-05-17T10:00:00+00:00'

        assert _unmapped_urls(service_request) == []
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_orc_9_wins_over_obr_6(self) -> 'None':
        orc = segment('ORC', {1: 'NW', 2: 'ORD-1^EHR', 9: '20240517090000'})
        obr = segment('OBR', {1: '1', 2: 'ORD-1^EHR', 4: '24331-1^Lipid panel^LN', 6: '20240517080000'})

        bundle = convert(MSH_ORM, PID, orc, obr)
        service_request = one_resource(bundle, 'ServiceRequest')

        # The ORC transaction time is the authored time, the OBR's requested time is preserved next to it.
        assert service_request['authoredOn'] == '2024-05-17T09:00:00+00:00'
        assert {'url': f'{Unmapped}/OBR-6', 'valueString': '20240517080000'} in service_request['extension']

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################

class TestORCRequester:
    """ ORC-12 is the requester, ORC-14 the requester's call back number and ORC-15 when the order takes effect.
    """

    def test_requester_with_call_back_number(self) -> 'None':
        orc = segment('ORC', {1: 'NW', 2: 'ORD-2^EHR', 12: '1234^Welby^Marcus', 14: '^WPN^PH^^1^555^2001234', 15: '20240517093000'})
        obr = segment('OBR', {1: '1', 2: 'ORD-2^EHR', 4: '24331-1^Lipid panel^LN'})

        bundle = convert(MSH_ORM, PID, orc, obr)
        service_request = one_resource(bundle, 'ServiceRequest')

        practitioner = one_resource(bundle, 'Practitioner')
        assert practitioner['name'] == [{'family': 'Welby', 'given': ['Marcus']}]
        assert practitioner['telecom'] == [{'value': '+1 555 2001234', 'use': 'work', 'system': 'phone'}]

        assert service_request['requester']['reference'].startswith('urn:uuid:')
        assert service_request['occurrenceDateTime'] == '2024-05-17T09:30:00+00:00'

        assert _unmapped_urls(service_request) == []
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_call_back_number_without_a_provider_is_preserved(self) -> 'None':
        orc = segment('ORC', {1: 'NW', 2: 'ORD-2^EHR', 14: '^WPN^PH^^1^555^2001234'})
        obr = segment('OBR', {1: '1', 2: 'ORD-2^EHR', 4: '24331-1^Lipid panel^LN'})

        bundle = convert(MSH_ORM, PID, orc, obr)
        service_request = one_resource(bundle, 'ServiceRequest')

        assert 'requester' not in service_request
        assert {'url': f'{Unmapped}/ORC-14', 'valueString': '^WPN^PH^^1^555^2001234'} in service_request['extension']

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################

class TestOBXAttachment:
    """ An encapsulated OBX in a result carries its creation time and who produced it.
    """

    def test_attachment_creation_and_performers(self) -> 'None':
        obr = segment('OBR', {1: '1', 2: 'ORD-1^EHR', 4: '24331-1^Lipid panel^LN', 25: 'F'})
        obx = segment('OBX', {
            1: '1', 2: 'ED', 3: 'PDF^Report^L', 5: '^application^pdf^Base64^JVBERi0=', 11: 'F',
            14: '20240517120000', 15: 'LAB01^Main Lab', 16: '5678^Adams^Robert',
        })

        bundle = convert(MSH_ORU, PID, obr, obx)
        report = one_resource(bundle, 'DiagnosticReport')

        # The OBX-14 time is when the attachment was created ..
        presented = report['presentedForm']
        assert presented == [{
            'contentType': 'application/pdf',
            'data': 'JVBERi0=',
            'title': 'Report',
            'creation': '2024-05-17T12:00:00+00:00',
        }]

        # .. the producer and the responsible observer perform the report.
        producer = organization_named(bundle, 'Main Lab')
        observer = one_resource(bundle, 'Practitioner')

        assert observer['name'] == [{'family': 'Adams', 'given': ['Robert']}]

        performer_urls = []
        for performer in report['performer']:
            performer_urls.append(performer['reference'])

        assert len(performer_urls) == 2

        assert _unmapped_urls(report) == []
        assert resources_of_type(bundle, 'Basic') == []
        assert get_conversion_warnings(bundle) == []

        # The references point at resources that exist in the bundle.
        full_urls = []
        for entry in bundle.to_dict()['entry']:
            full_urls.append(entry['fullUrl'])

        for url in performer_urls:
            assert url in full_urls

        assert producer['name'] == 'Main Lab'

# ################################################################################################################################
# ################################################################################################################################
