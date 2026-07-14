# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# piigex
from piigex import scan

# Zato
from zato.common.util.safeguards.api import apply_safeguards
from zato.common.util.safeguards.common import Kind_Unicode, Max_Signal_Paths, Mode_Reject, SafeguardConfig, SafeguardResult
from zato.common.util.safeguards.unicode_ import Bidi_Control_Characters, normalize_unicode, Zero_Width_Characters

# ################################################################################################################################
# ################################################################################################################################

def _new_result() -> 'SafeguardResult':
    """ Returns a fresh result for direct stage calls.
    """
    out = SafeguardResult()
    out.pii_removed = {}
    out.signals = {}

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestNormalizeUnicode:

    def test_every_zero_width_character_is_removed(self) -> 'None':

        for character in Zero_Width_Characters:

            result = _new_result()
            value = {'note': f'before{character}after'}

            cleaned = normalize_unicode(value, result)

            assert cleaned == {'note': 'beforeafter'}
            assert result.unicode_chars_removed == 1

    def test_every_bidi_control_character_is_removed(self) -> 'None':

        for character in Bidi_Control_Characters:

            result = _new_result()
            value = {'note': f'before{character}after'}

            cleaned = normalize_unicode(value, result)

            assert cleaned == {'note': 'beforeafter'}
            assert result.unicode_chars_removed == 1

    def test_nfc_is_applied(self) -> 'None':

        # A decomposed letter is recomposed, silently - composition differences are benign.
        result = _new_result()
        value = {'name': 'Cafe\u0301 de Paris'}

        cleaned = normalize_unicode(value, result)

        assert cleaned == {'name': 'Caf\u00e9 de Paris'}
        assert result.unicode_chars_removed == 0
        assert result.signals == {}

    def test_plain_ascii_passes_unchanged(self) -> 'None':

        result = _new_result()
        value = {'note': 'Nothing to normalize here'}

        cleaned = normalize_unicode(value, result)

        assert cleaned == {'note': 'Nothing to normalize here'}
        assert result.unicode_chars_removed == 0
        assert result.signals == {}

    def test_iban_matches_again_after_normalization(self) -> 'None':

        # A zero-width space inside an IBAN prevents the detector from firing - normalization repairs that.
        result = _new_result()
        smuggled = 'Pay to DE89\u200b370400440532013000 today'
        value = {'payment': smuggled}

        before = scan(smuggled)

        found_before = []

        for match in before:
            if match.name == 'intl_iban':
                found_before.append(match)

        assert len(found_before) == 0

        cleaned = normalize_unicode(value, result)
        after = scan(cleaned['payment'])

        found_after = []

        for match in after:
            if match.name == 'intl_iban':
                found_after.append(match)

        assert len(found_after) == 1
        assert found_after[0].valid is True

    def test_findings_are_signalled_with_paths(self) -> 'None':

        result = _new_result()
        value = {'first': 'a\u200bb', 'second': 'c\u202ed\u202ee'}

        _ = normalize_unicode(value, result)

        assert result.unicode_chars_removed == 3

        signal = result.signals[Kind_Unicode]

        assert signal.count == 3
        assert signal.paths == ['$.first', '$.second']

    def test_path_sample_is_capped(self) -> 'None':

        # More findings than the cap - the count keeps growing, the path sample does not.
        result = _new_result()
        value = {}

        for index in range(Max_Signal_Paths + 2):
            value[f'field_{index}'] = f'a\u200bb{index}'

        _ = normalize_unicode(value, result)

        signal = result.signals[Kind_Unicode]

        assert signal.count == Max_Signal_Paths + 2
        assert len(signal.paths) == Max_Signal_Paths

    def test_reject_mode_stops_the_pipeline(self) -> 'None':

        # In reject mode the whole document is refused and the stages after unicode never run.
        config = SafeguardConfig()
        config.normalize_unicode = True
        config.unicode_mode = Mode_Reject
        config.pii_enabled = True
        config.pii_lands = ['intl']
        config.pii_detectors = []
        config.pii_exclude = []

        value = {'note': 'a\u200bb', 'payment': 'IBAN DE89370400440532013000'}

        result = apply_safeguards(value, config)

        assert result.was_rejected is True
        assert result.reject_kind == Kind_Unicode

        # PII removal never ran - the IBAN is still in the value.
        assert result.pii_removed == {}
        assert result.value['payment'] == 'IBAN DE89370400440532013000'

# ################################################################################################################################
# ################################################################################################################################
