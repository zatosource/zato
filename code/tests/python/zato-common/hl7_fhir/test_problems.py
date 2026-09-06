# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from conftest import convert, full_url_of, one_resource, resources_of_type, segment

# ################################################################################################################################
# ################################################################################################################################

# A minimal envelope every problem list test builds on.
MSH = 'MSH|^~\\&|EHR|GENHOSP|CARE|GENHOSP|20260315120000||PPR^PC1^PPR_PC1|MSG00001|P|2.5.1'
PID = 'PID|1||12345^^^GENHOSP^MR||Smith^John|||M'
PV1 = 'PV1|1|I|WARD1^101^A^GENHOSP'

# ################################################################################################################################
# ################################################################################################################################

class TestPRB:
    """ PRB segments become Condition resources of the problem-list-item category.
    """

    def test_full_problem(self) -> 'None':
        prb = segment('PRB', {
            1: 'AD',
            2: '20260315',
            3: 'I10^Essential hypertension^I10',
            4: 'PRB001^EHR',
            7: '20260310',
            9: '20260601',
            13: 'C^Confirmed^L',
            14: 'A^Active^L',
            16: '20260201',
        })

        bundle = convert(MSH, PID, PV1, prb)
        condition = one_resource(bundle, 'Condition')

        # The patient and the encounter are wired up ..
        patient = one_resource(bundle, 'Patient')
        encounter = one_resource(bundle, 'Encounter')

        patient_url = full_url_of(bundle, patient)
        encounter_url = full_url_of(bundle, encounter)

        assert condition['subject'] == {'reference': patient_url}
        assert condition['encounter'] == {'reference': encounter_url}

        # .. the category says this is a problem list entry ..
        assert condition['category'] == [{
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/condition-category',
                'code': 'problem-list-item',
            }],
        }]

        # .. the problem ID is the code ..
        coding = condition['code']['coding'][0]
        assert coding['code'] == 'I10'
        assert coding['system'] == 'http://hl7.org/fhir/sid/icd-10'

        # .. the instance ID the identifier ..
        assert condition['identifier'] == [{'value': 'PRB001', 'system': 'urn:zato:hl7v2:authority:EHR'}]

        # .. the times land where they belong ..
        assert condition['recordedDate'] == '2026-03-15'
        assert condition['onsetDateTime'] == '2026-02-01'
        assert condition['abatementDateTime'] == '2026-06-01'

        assert {
            'url': 'http://hl7.org/fhir/StructureDefinition/condition-assertedDate',
            'valueDateTime': '2026-03-10',
        } in condition['extension']

        # .. and the statuses map through their vocabularies.
        assert condition['verificationStatus'] == {
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/condition-ver-status',
                'code': 'confirmed',
            }],
        }

        assert condition['clinicalStatus'] == {
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/condition-clinical',
                'code': 'active',
            }],
        }

        # The segment was consumed, so nothing became a Basic resource.
        assert resources_of_type(bundle, 'Basic') == []

# ################################################################################################################################

    def test_onset_text_takes_over_when_there_is_no_onset_date(self) -> 'None':
        prb = segment('PRB', {1: 'AD', 3: 'J45^Asthma^I10', 17: 'Since early childhood'})

        bundle = convert(MSH, PID, prb)
        condition = one_resource(bundle, 'Condition')

        assert condition['onsetString'] == 'Since early childhood'

# ################################################################################################################################

    def test_onset_text_is_preserved_when_the_date_took_the_slot(self) -> 'None':
        prb = segment('PRB', {1: 'AD', 3: 'J45^Asthma^I10', 16: '20260201', 17: 'early February'})

        bundle = convert(MSH, PID, prb)
        condition = one_resource(bundle, 'Condition')

        assert condition['onsetDateTime'] == '2026-02-01'

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/PRB-17',
            'valueString': 'early February',
        } in condition['extension']

# ################################################################################################################################

    def test_deleted_problem_was_entered_in_error(self) -> 'None':
        prb = segment('PRB', {1: 'DE', 3: 'I10^Hypertension^I10', 13: 'C^Confirmed^L'})

        bundle = convert(MSH, PID, prb)
        condition = one_resource(bundle, 'Condition')

        # The deletion wins over the confirmation status.
        assert condition['verificationStatus'] == {
            'coding': [{
                'system': 'http://terminology.hl7.org/CodeSystem/condition-ver-status',
                'code': 'entered-in-error',
            }],
        }

# ################################################################################################################################

    def test_unknown_statuses_are_preserved(self) -> 'None':
        prb = segment('PRB', {1: 'ZZ', 3: 'I10^Hypertension^I10', 13: 'X^Unclear^L', 14: 'Q^Quiescent^L'})

        bundle = convert(MSH, PID, prb)
        condition = one_resource(bundle, 'Condition')

        assert 'verificationStatus' not in condition
        assert 'clinicalStatus' not in condition

        extensions = condition['extension']

        assert {'url': 'urn:zato:hl7v2:extension/unmapped/PRB-1', 'valueString': 'ZZ'} in extensions
        assert {'url': 'urn:zato:hl7v2:extension/unmapped/PRB-13', 'valueString': 'X^Unclear^L'} in extensions
        assert {'url': 'urn:zato:hl7v2:extension/unmapped/PRB-14', 'valueString': 'Q^Quiescent^L'} in extensions

# ################################################################################################################################

    def test_prt_after_prb_asserts_the_condition(self) -> 'None':
        prb = segment('PRB', {1: 'AD', 3: 'I10^Hypertension^I10'})
        prt = segment('PRT', {2: 'AD', 5: '5001^Baker^Sarah'})

        bundle = convert(MSH, PID, prb, prt)
        condition = one_resource(bundle, 'Condition')

        # The participation names the condition's asserter, backed by a Practitioner.
        practitioner = one_resource(bundle, 'Practitioner')
        practitioner_url = full_url_of(bundle, practitioner)

        assert condition['asserter'] == {'reference': practitioner_url}
        assert practitioner['name'] == [{'family': 'Baker', 'given': ['Sarah']}]

        # The PRT was consumed, so nothing became a Basic resource.
        assert resources_of_type(bundle, 'Basic') == []

# ################################################################################################################################
# ################################################################################################################################
