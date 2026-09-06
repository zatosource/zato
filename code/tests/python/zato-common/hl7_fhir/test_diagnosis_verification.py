# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from conftest import convert, one_resource

# ################################################################################################################################
# ################################################################################################################################

# A minimal envelope every DG1 test builds on.
MSH = 'MSH|^~\\&|EHR|GENHOSP|CARE|GENHOSP|20260315120000||ADT^A01^ADT_A01|MSG00001|P|2.5.1'
PID = 'PID|1||12345^^^GENHOSP^MR||Smith^John|||M'

# ################################################################################################################################
# ################################################################################################################################

class TestDG1Verification:
    """ DG1-6 working and final diagnoses map to the Condition's verification status.
    """

    def test_working_diagnosis_is_provisional(self) -> 'None':
        dg1 = 'DG1|1||I10^Hypertension^I10|||W'

        bundle = convert(MSH, PID, dg1)
        condition = one_resource(bundle, 'Condition')

        assert condition['verificationStatus'] == {
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/condition-ver-status',
                'code': 'provisional',
            }],
        }

        assert 'extension' not in condition

# ################################################################################################################################

    def test_final_diagnosis_is_confirmed(self) -> 'None':
        dg1 = 'DG1|1||I10^Hypertension^I10|||F'

        bundle = convert(MSH, PID, dg1)
        condition = one_resource(bundle, 'Condition')

        assert condition['verificationStatus'] == {
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/condition-ver-status',
                'code': 'confirmed',
            }],
        }

# ################################################################################################################################

    def test_admitting_diagnosis_still_names_the_encounter_role(self) -> 'None':
        pv1 = 'PV1|1|I|ICU^101^A'
        dg1 = 'DG1|1||I10^Hypertension^I10|||A'

        bundle = convert(MSH, PID, pv1, dg1)

        condition = one_resource(bundle, 'Condition')
        encounter = one_resource(bundle, 'Encounter')

        # An admitting diagnosis is an encounter role, not a verification status.
        assert 'verificationStatus' not in condition

        diagnosis = encounter['diagnosis'][0]

        assert diagnosis['use'] == {
            'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/diagnosis-role', 'code': 'AD'}],
        }

# ################################################################################################################################

    def test_unknown_diagnosis_type_is_preserved(self) -> 'None':
        dg1 = 'DG1|1||I10^Hypertension^I10|||X'

        bundle = convert(MSH, PID, dg1)
        condition = one_resource(bundle, 'Condition')

        assert 'verificationStatus' not in condition

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/DG1-6',
            'valueString': 'X',
        } in condition['extension']

# ################################################################################################################################
# ################################################################################################################################
