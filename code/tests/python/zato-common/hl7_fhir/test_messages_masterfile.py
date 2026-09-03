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

# ################################################################################################################################
# ################################################################################################################################

class TestMFNStaffMasterFile:
    """ MFN^M02 staff master files - the MFI and MFE frames are preserved
    and each MFE group's STF and PRA build a Practitioner.
    """

    def test_staff_update_builds_a_practitioner(self) -> 'None':
        mfi = 'MFI|PRA^Practitioner master file^HL70175||UPD^Update^HL70180|||NE'
        mfe = 'MFE|MAD^Add record to master file^HL70180|20240517155500||8903456789^Beaumont^Patricia'
        stf = 'STF|8903456789|U8903456789^^HOSPFAC|Beaumont^Patricia^Ann||F|19750830|A|||' + \
            '|^WPN^PH^^1^214^5559102'
        pra = 'PRA|8903456789||I||207RC0000X^Internal Medicine Cardiovascular Disease^NUCC'

        bundle = convert(MSH_MFN, mfi, mfe, stf, pra)

        practitioner = one_resource(bundle, 'Practitioner')

        # The STF identifiers and name carried over ..
        identifiers = practitioner['identifier']
        assert {'value': '8903456789'} in identifiers

        assert practitioner['name'] == [{'family': 'Beaumont', 'given': ['Patricia', 'Ann']}]

        # .. A means the staff member is active ..
        assert practitioner['active'] is True

        # .. and the PRA specialty became a qualification.
        qualification = practitioner['qualification'][0]
        assert qualification['code']['text'] == 'Internal Medicine Cardiovascular Disease'

        # The MFI frame describes the message itself ..
        assert resources_of_type(bundle, 'Basic') == []

        header = one_resource(bundle, 'MessageHeader')
        header_extensions = header['extension']

        master_file = {
            'url': 'urn:zato:hl7v2:extension/master-file',
            'valueCodeableConcept': {
                'coding': [{
                    'code': 'PRA',
                    'display': 'Practitioner master file',
                    'system': 'http://terminology.hl7.org/CodeSystem/v2-0175',
                }],
                'text': 'Practitioner master file',
            },
        }
        assert master_file in header_extensions

        master_file_event = {
            'url': 'urn:zato:hl7v2:extension/master-file-event',
            'valueCodeableConcept': {
                'coding': [{
                    'code': 'UPD',
                    'display': 'Update',
                    'system': 'http://terminology.hl7.org/CodeSystem/v2-0180',
                }],
                'text': 'Update',
            },
        }
        assert master_file_event in header_extensions

        # .. the response level is preserved on it ..
        assert {'url': 'urn:zato:hl7v2:extension/unmapped/MFI-6', 'valueString': 'NE'} in header_extensions

        # .. and the MFE record event tags the Practitioner its group built, with the primary key as an identifier.
        tag = {
            'code': 'MAD',
            'display': 'Add record to master file',
            'system': 'http://terminology.hl7.org/CodeSystem/v2-0180',
        }
        assert practitioner['meta']['tag'] == [tag]
        assert {'value': '8903456789'} in identifiers

        practitioner_extensions = practitioner['extension']
        assert {'url': 'urn:zato:hl7v2:extension/unmapped/MFE-2', 'valueString': '20240517155500'} \
            in practitioner_extensions
        assert {'url': 'urn:zato:hl7v2:extension/unmapped/MFE-4', 'valueString': '8903456789^Beaumont^Patricia'} \
            in practitioner_extensions

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################

    def test_every_mfe_group_makes_its_own_practitioner(self) -> 'None':
        mfi = 'MFI|PRA^^HL70175||UPD|||NE'
        mfe_first = 'MFE|MAD|D300100|20240517000000|D300100'
        stf_first = 'STF|D300100|D300100^^HOSPFAC|Matsumoto^Yukie||F'
        mfe_second = 'MFE|MAD|D300200|20240517000000|D300200'
        stf_second = 'STF|D300200|D300200^^HOSPFAC|Tanaka^Hiroshi||M'

        bundle = convert(MSH_MFN, mfi, mfe_first, stf_first, mfe_second, stf_second)

        practitioners = resources_of_type(bundle, 'Practitioner')
        assert len(practitioners) == 2

        assert practitioners[0]['name'] == [{'family': 'Matsumoto', 'given': ['Yukie']}]
        assert practitioners[1]['name'] == [{'family': 'Tanaka', 'given': ['Hiroshi']}]

        assert get_conversion_warnings(bundle) == []

# ################################################################################################################################
# ################################################################################################################################
