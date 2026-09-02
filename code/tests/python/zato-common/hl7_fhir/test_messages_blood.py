# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7.mappings import get_conversion_warnings

# Local
from conftest import convert, one_resource, resources_of_type

# ################################################################################################################################
# ################################################################################################################################

MSH_OMB = 'MSH|^~\\&|BLOODBANK|HOSPFAC|LIS|LABFAC|20240517143055||OMB^O27^OMB_O27|MSG00060|P|2.5'
PID = 'PID|1||12345^^^MYHOSP^MR||Smith^John|||M'

# ################################################################################################################################
# ################################################################################################################################

class TestBPOBloodProductOrder:
    """ BPO segments become blood-product ServiceRequests.
    """

    def test_bpo_becomes_a_service_request(self) -> 'None':
        orc = 'ORC|NW|BB-1^BLOODBANK'
        bpo = 'BPO|1|RBC^Red Blood Cells^99BBANK|IRR^Irradiated^99PROC|2|||20240517200000||||||' + \
            'ANEMIA^Symptomatic anemia^L'

        bundle = convert(MSH_OMB, PID, orc, bpo)
        service_request = one_resource(bundle, 'ServiceRequest')

        # A blood product order carries its own category.
        assert service_request['category'] == [{'text': 'Blood product'}]

        # The universal service identifier is the requested product.
        request_code = service_request['code']
        assert request_code['text'] == 'Red Blood Cells'
        assert request_code['coding'][0]['code'] == 'RBC'

        # The processing requirements detail how the product is prepared.
        order_detail = service_request['orderDetail'][0]
        assert order_detail['text'] == 'Irradiated'

        # The quantity says how many units are ordered.
        assert service_request['quantityQuantity'] == {'value': 2}

        # The intended use time is when the product is needed.
        assert service_request['occurrenceDateTime'] == '2024-05-17T20:00:00+00:00'

        # The indication for use is the reason.
        reason = service_request['reasonCode'][0]
        assert reason['text'] == 'Symptomatic anemia'

        # The order number identifies the request.
        identifiers = service_request['identifier']
        assert {'value': 'BB-1', 'system': 'urn:zato:hl7v2:authority:BLOODBANK'} in identifiers

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_every_bpo_makes_its_own_request(self) -> 'None':
        orc_first = 'ORC|NW|BB-2^BLOODBANK'
        bpo_first = 'BPO|1|RBC^Red Blood Cells^99BBANK||3'
        orc_second = 'ORC|NW|BB-3^BLOODBANK'
        bpo_second = 'BPO|2|FFP^Fresh Frozen Plasma^99BBANK||2'

        bundle = convert(MSH_OMB, PID, orc_first, bpo_first, orc_second, bpo_second)

        service_requests = resources_of_type(bundle, 'ServiceRequest')
        assert len(service_requests) == 2

        assert service_requests[0]['code']['text'] == 'Red Blood Cells'
        assert service_requests[0]['quantityQuantity'] == {'value': 3}

        assert service_requests[1]['code']['text'] == 'Fresh Frozen Plasma'
        assert service_requests[1]['quantityQuantity'] == {'value': 2}

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_non_numeric_quantity_is_preserved(self) -> 'None':
        bpo = 'BPO|1|PLT^Platelets^99BBANK||ONE ADULT DOSE'

        bundle = convert(MSH_OMB, PID, bpo)
        service_request = one_resource(bundle, 'ServiceRequest')

        assert 'quantityQuantity' not in service_request

        extensions = service_request['extension']
        assert {'url': 'urn:zato:hl7v2:extension/unmapped/BPO-4', 'valueString': 'ONE ADULT DOSE'} in extensions

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################
