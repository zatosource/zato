# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from conftest import convert, resources_of_type, segment

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# A minimal envelope every PL test builds on.
MSH = 'MSH|^~\\&|EHR|GENHOSP|CARE|GENHOSP|20260315120000||ADT^A01^ADT_A01|MSG00001|P|2.5.1'
PID = 'PID|1||12345^^^GENHOSP^MR||Smith^John|||M'

# ################################################################################################################################
# ################################################################################################################################

def _bed_location(bundle:'any_', name:'str') -> 'anydict':
    """ The one Location of a given name in the bundle.
    """
    matches = []

    for item in resources_of_type(bundle, 'Location'):
        if item['name'] == name:
            matches.append(item)

    assert len(matches) == 1

    out = matches[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPLStatusAndType:
    """ PL-5 is the location status, PL-6 the kind of place the location is.
    """

    def test_pl_6_is_the_location_type(self) -> 'None':
        pv1 = segment('PV1', {1: '1', 2: 'I', 3: 'ICU^101^A^GENHOSP^^N'})

        bundle = convert(MSH, PID, pv1)
        bed = _bed_location(bundle, 'A')

        assert bed['type'] == [{
            'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v2-0305', 'code': 'N'}],
        }]

# ################################################################################################################################

    def test_pl_5_is_the_operational_status(self) -> 'None':
        pv1 = segment('PV1', {1: '1', 2: 'I', 3: 'ICU^101^A^GENHOSP^O'})

        bundle = convert(MSH, PID, pv1)
        bed = _bed_location(bundle, 'A')

        assert bed['operationalStatus'] == {
            'system': 'http://terminology.hl7.org/CodeSystem/v2-0306',
            'code': 'O',
        }

# ################################################################################################################################

    def test_pl_5_defers_to_a_bed_status(self) -> 'None':
        # PV1-40 carries the bed status, which takes the operational status slot first.
        pv1 = segment('PV1', {1: '1', 2: 'I', 3: 'ICU^101^A^GENHOSP^O', 40: 'C'})

        bundle = convert(MSH, PID, pv1)
        bed = _bed_location(bundle, 'A')

        assert bed['operationalStatus']['code'] == 'C'
        assert bed['operationalStatus']['system'] == 'http://terminology.hl7.org/CodeSystem/v2-0116'

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/PL-5',
            'valueString': 'O',
        } in bed['extension']

# ################################################################################################################################
# ################################################################################################################################
