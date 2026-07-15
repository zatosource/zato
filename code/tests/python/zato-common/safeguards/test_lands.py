# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# piigex
from piigex import Scrubber

# Zato
from zato.common.typing_ import strlist
from zato.common.util.safeguards import detectors
from zato.common.util.safeguards.common import SafeguardConfig, SafeguardResult
from zato.common.util.safeguards.pii import remove_pii

# The import above registers Zato's own detectors with the library's registry - this line keeps flake8 quiet about it.
detectors = detectors

# ################################################################################################################################
# ################################################################################################################################

# Type aliases
sample_dict = dict[str, strlist]

# ################################################################################################################################
# ################################################################################################################################

# Samples that must match their detector's pattern and pass its validation, keyed by detector name.
Valid_Samples:'sample_dict' = {
    'au_tfn':              ['123456782', '123 456 782'],
    'au_abn':              ['51824753556', '51 824 753 556'],
    'au_medicare':         ['2123456701', '2123 45670 1'],
    'au_passport':         ['N1234567', 'PA1234567'],
    'br_cpf':              ['39053344705', '390.533.447-05'],
    'br_cnpj':             ['16727230000197', '16.727.230/0001-97'],
    'br_passport':         ['CY123456'],
    'ca_sin':              ['130692544', '130-692-544', '130 692 544'],
    'ca_passport':         ['AB123456'],
    'ee_passport':         ['K1234567'],
    'fi_passport':         ['FP1234567'],
    'in_aadhaar':          ['234123412346', '2341 2341 2346'],
    'in_pan':              ['ACUPA7085R'],
    'in_passport':         ['J1234567'],
    'is_kennitala':        ['1201743399', '120174-3399'],
    'jp_my_number':        ['123456789018', '1234 5678 9018'],
    'jp_corporate_number': ['5835678256246'],
    'jp_passport':         ['TK1234567'],
    'kr_rrn':              ['9001011000006', '900101-1000006'],
    'kr_passport':         ['M12345678', 'S12345678'],
    'lu_matricule':        ['1983040575001'],
    'mx_curp':             ['BOXW310820HNERXN09'],
    'mx_rfc':              ['GODE561231GR8'],
    'no_fnr':              ['15108695088'],
    'nz_ird':              ['49091850', '49-091-850'],
    'nz_nhi':              ['ZAC0009', 'ZAC53LA'],
    'ph_psn':              ['1234 5678 9012'],
    'ph_pcn':              ['1234 5678 9012 3456'],
    'sg_nric':             ['S1234567D', 'F2345678T'],
    'za_id':               ['7503305044089'],
    'za_passport':         ['A12345678'],
}

# Samples that match their detector's shape but fail its checksum, keyed by detector name.
# Detectors without a checksum have no entry here - their shape is all there is to check.
Broken_Samples:'sample_dict' = {
    'au_tfn':              ['123456783'],
    'au_abn':              ['51824753557'],
    'au_medicare':         ['2123456711', '2123456700'],
    'br_cpf':              ['39053344706'],
    'br_cnpj':             ['16727230000198'],
    'ca_sin':              ['130692545'],
    'in_aadhaar':          ['234123412347'],
    'is_kennitala':        ['1201743389'],
    'jp_my_number':        ['123456789019'],
    'jp_corporate_number': ['5835678256247'],
    'kr_rrn':              ['9001011000007'],
    'lu_matricule':        ['1983040575002'],
    'mx_curp':             ['BOXW310820HNERXN08'],
    'no_fnr':              ['15108695089'],
    'nz_ird':              ['49091851'],
    'nz_nhi':              ['ZAC0018'],
    'sg_nric':             ['S1234567A'],
    'za_id':               ['7503305044080'],
}

# Ordinary business text that no detector may report as a valid finding -
# order numbers, timestamps, prices and coordinates.
Negative_Text = 'Order ORD-2026-000123 shipped on 2026-07-15 at 11:32 for 1,099.99 EUR to 52.2297, 21.0122'

# ################################################################################################################################
# ################################################################################################################################

def _new_scrubber(name:'str') -> 'Scrubber':
    """ Returns a scrubber running just the one named detector.
    """
    out = Scrubber(detectors=[name])
    return out

# ################################################################################################################################

def _has_valid_match(scrubber:'Scrubber', text:'str', name:'str') -> 'bool':
    """ Tells whether scanning the text yields at least one validated match of the named detector.
    """
    matches = scrubber.scan(text)

    for match in matches:
        if match.name == name:
            if match.valid:
                out = True
                break
    else:
        out = False

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestValidSamples:

    def test_valid_samples_match_and_validate(self) -> 'None':

        for name, sample_list in Valid_Samples.items():
            scrubber = _new_scrubber(name)

            for sample in sample_list:
                text = f'Customer identifier {sample} received in the payload'
                assert _has_valid_match(scrubber, text, name), f'{name} did not accept {sample}'

# ################################################################################################################################
# ################################################################################################################################

class TestBrokenSamples:

    def test_broken_checksums_fail_validation(self) -> 'None':

        for name, sample_list in Broken_Samples.items():
            scrubber = _new_scrubber(name)

            for sample in sample_list:
                text = f'Customer identifier {sample} received in the payload'
                assert not _has_valid_match(scrubber, text, name), f'{name} wrongly accepted {sample}'

# ################################################################################################################################
# ################################################################################################################################

class TestNegativeText:

    def test_ordinary_text_yields_no_valid_findings(self) -> 'None':

        for name in Valid_Samples:
            scrubber = _new_scrubber(name)

            assert not _has_valid_match(scrubber, Negative_Text, name), f'{name} fired on ordinary text'

# ################################################################################################################################
# ################################################################################################################################

class TestLandSelection:

    def test_new_land_detectors_run_via_remove_pii(self) -> 'None':

        # A config selecting Iceland must remove a kennitala while an ordinary order number survives.
        result = SafeguardResult()
        result.pii_removed = {}
        result.signals = {}

        config = SafeguardConfig()
        config.pii_enabled = True
        config.pii_lands = ['is']
        config.pii_detectors = []
        config.pii_exclude = []

        value = {'note': 'Registered 120174-3399 under order ORD-2026-000123'}

        cleaned = remove_pii(value, result, config)

        assert '120174-3399' not in cleaned['note']
        assert 'ORD-2026-000123' in cleaned['note']
        assert result.pii_removed == {'is_kennitala': 1}

# ################################################################################################################################
# ################################################################################################################################
