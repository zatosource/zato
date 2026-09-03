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

MSH_MFN = 'MSH|^~\\&|HR|HOSPFAC|MF_RECV|HIEFAC|20240517143055||MFN^M02^MFN_M02|MSG00050|P|2.5'

Record_Event = 'http://terminology.hl7.org/CodeSystem/v2-0180'
Unmapped = 'urn:zato:hl7v2:extension/unmapped'

# ################################################################################################################################
# ################################################################################################################################

class TestMFI:
    """ MFI describes the master file the message carries, which belongs on the MessageHeader.
    """

    def test_bare_codes_get_their_tables(self) -> 'None':
        bundle = convert(MSH_MFN, 'MFI|PRA^^HL70175||UPD')
        header = one_resource(bundle, 'MessageHeader')

        assert header['extension'] == [
            {
                'url': 'urn:zato:hl7v2:extension/master-file',
                'valueCodeableConcept': {
                    'coding': [{'code': 'PRA', 'system': 'http://terminology.hl7.org/CodeSystem/v2-0175'}],
                    'text': 'PRA',
                },
            },
            {
                'url': 'urn:zato:hl7v2:extension/master-file-event',
                'valueCodeableConcept': {'coding': [{'code': 'UPD'}], 'text': 'UPD'},
            },
        ]

        assert resources_of_type(bundle, 'Basic') == []
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################

class TestMFE:
    """ MFE frames one entry of the master file and describes the resource its group builds.
    """

    def test_entry_tags_and_identifies_the_practitioner(self) -> 'None':
        mfe = 'MFE|MUP|D300200|20240517000000|D300200'
        stf = 'STF|D300200|D300200^^HOSPFAC|Tanaka^Hiroshi'

        bundle = convert(MSH_MFN, 'MFI|PRA^^HL70175||UPD', mfe, stf)
        practitioner = one_resource(bundle, 'Practitioner')

        # The record event is a tag ..
        assert practitioner['meta']['tag'] == [{'code': 'MUP', 'system': Record_Event}]

        # .. the primary key an identifier ..
        assert {'value': 'D300200'} in practitioner['identifier']

        # .. and the rest of the entry is preserved on the Practitioner rather than as a segment of its own.
        assert {'url': f'{Unmapped}/MFE-2', 'valueString': 'D300200'} in practitioner['extension']
        assert {'url': f'{Unmapped}/MFE-3', 'valueString': '20240517000000'} in practitioner['extension']

        assert resources_of_type(bundle, 'Basic') == []
        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_entry_without_a_group_stays_whole(self) -> 'None':
        orphan = 'MFE|MAD|D300100|20240517000000|D300100'
        mfe = 'MFE|MUP|D300200|20240517000000|D300200'
        stf = 'STF|D300200|D300200^^HOSPFAC|Tanaka^Hiroshi'

        bundle = convert(MSH_MFN, 'MFI|PRA^^HL70175||UPD', orphan, mfe, stf)

        # The first entry built nothing, so it is preserved as a Basic, the second went onto its Practitioner.
        basic = one_resource(bundle, 'Basic')

        assert basic['code']['coding'][0]['code'] == 'MFE'
        assert {'url': 'urn:zato:hl7v2:extension/MFE/1', 'valueString': 'MAD'} in basic['extension']

        practitioner = one_resource(bundle, 'Practitioner')
        assert practitioner['meta']['tag'] == [{'code': 'MUP', 'system': Record_Event}]

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_trailing_entry_without_a_group_stays_whole(self) -> 'None':
        bundle = convert(MSH_MFN, 'MFI|PRA^^HL70175||UPD', 'MFE|MDL|D300300|20240517000000|D300300')

        basic = one_resource(bundle, 'Basic')
        assert basic['code']['coding'][0]['code'] == 'MFE'

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################
