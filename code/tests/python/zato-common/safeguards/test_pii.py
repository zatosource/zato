# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import strlist
from zato.common.util.safeguards.common import Max_Cleaner_Cache_Entries, SafeguardConfig, SafeguardResult
from zato.common.util.safeguards.pii import _cache, get_cleaner, remove_pii

# ################################################################################################################################
# ################################################################################################################################

# A valid IBAN, a valid email and an IBAN with a broken checksum, used throughout.
_valid_iban  = 'DE89370400440532013000'
_broken_iban = 'DE89370400440532013001'
_email       = 'alice@example.com'

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

def _new_config(lands:'strlist', detectors:'strlist', exclude:'strlist') -> 'SafeguardConfig':
    """ Returns a config with PII removal enabled and the given selection.
    """
    out = SafeguardConfig()
    out.pii_enabled = True
    out.pii_lands = lands
    out.pii_detectors = detectors
    out.pii_exclude = exclude

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestLandSelection:

    def test_only_detectors_of_the_configured_lands_fire(self) -> 'None':

        # An SSN is a us detector and an IBAN is an intl one - with only us configured, the IBAN survives.
        result = _new_result()
        config = _new_config(['us'], [], [])
        value = {'note': f'SSN 536-90-4399 and IBAN {_valid_iban} in one note'}

        cleaned = remove_pii(value, result, config)

        assert '536-90-4399' not in cleaned['note']
        assert _valid_iban in cleaned['note']
        assert result.pii_removed == {'us_ssn': 1}

    def test_explicit_detectors_win_over_lands(self) -> 'None':

        # The detector list names only emails, so the us land selection has no say and the SSN survives.
        result = _new_result()
        config = _new_config(['us'], ['intl_email'], [])
        value = {'note': f'SSN 536-90-4399 wrote from {_email} yesterday'}

        cleaned = remove_pii(value, result, config)

        assert '536-90-4399' in cleaned['note']
        assert _email not in cleaned['note']
        assert result.pii_removed == {'intl_email': 1}

    def test_exclusions_are_honored(self) -> 'None':

        result = _new_result()
        config = _new_config(['intl'], [], ['intl_email'])
        value = {'note': f'Pay to {_valid_iban}, questions go to {_email}'}

        cleaned = remove_pii(value, result, config)

        assert _valid_iban not in cleaned['note']
        assert _email in cleaned['note']
        assert result.pii_removed == {'intl_iban': 1}

    def test_empty_selection_means_all_default_detectors(self) -> 'None':

        result = _new_result()
        config = _new_config([], [], [])
        value = {'note': f'SSN 536-90-4399 pays to {_valid_iban} from {_email}'}

        cleaned = remove_pii(value, result, config)

        assert '536-90-4399' not in cleaned['note']
        assert _valid_iban not in cleaned['note']
        assert _email not in cleaned['note']

# ################################################################################################################################
# ################################################################################################################################

class TestValidation:

    def test_broken_checksum_survives_with_validation_on(self) -> 'None':

        result = _new_result()
        config = _new_config(['intl'], [], [])
        value = {'note': f'A broken account number {_broken_iban} appears here'}

        cleaned = remove_pii(value, result, config)

        assert _broken_iban in cleaned['note']
        assert result.pii_removed == {}

    def test_broken_checksum_is_removed_with_validation_off(self) -> 'None':

        result = _new_result()
        config = _new_config(['intl'], [], [])
        config.pii_validate = False
        value = {'note': f'A broken account number {_broken_iban} appears here'}

        cleaned = remove_pii(value, result, config)

        assert _broken_iban not in cleaned['note']
        assert result.pii_removed == {'intl_iban': 1}

# ################################################################################################################################
# ################################################################################################################################

class TestStableTokens:

    def test_stable_tokens_number_repeated_values(self) -> 'None':

        result = _new_result()
        config = _new_config([], ['intl_iban'], [])
        config.pii_stable_tokens = True
        value = {'note': f'First {_valid_iban} and again {_valid_iban}'}

        cleaned = remove_pii(value, result, config)

        assert cleaned == {'note': 'First {{IBAN_1}} and again {{IBAN_1}}'}
        assert result.pii_removed == {'intl_iban': 2}

    def test_plain_tokens_carry_no_numbers(self) -> 'None':

        result = _new_result()
        config = _new_config([], ['intl_iban'], [])
        value = {'note': f'First {_valid_iban} and again {_valid_iban}'}

        cleaned = remove_pii(value, result, config)

        assert cleaned == {'note': 'First {{IBAN}} and again {{IBAN}}'}
        assert result.pii_removed == {'intl_iban': 2}

# ################################################################################################################################
# ################################################################################################################################

class TestCleanerCache:

    def test_same_config_reuses_the_cleaner(self) -> 'None':

        config = _new_config(['intl'], [], [])

        first = get_cleaner(config)
        second = get_cleaner(config)

        assert first is second

    def test_full_cache_evicts_the_oldest_entry(self) -> 'None':

        # The cache is filled to the brim with entries sharing one cleaner -
        # building one more evicts the oldest of them.
        config = _new_config([], ['intl_email'], [])
        filler = get_cleaner(config)

        _cache.clear()

        for index in range(Max_Cleaner_Cache_Entries):
            _cache[('filler', index)] = filler

        oldest = ('filler', 0)

        assert oldest in _cache

        _ = get_cleaner(config)

        assert oldest not in _cache
        assert len(_cache) == Max_Cleaner_Cache_Entries

        _cache.clear()

# ################################################################################################################################
# ################################################################################################################################

class TestRemovePii:

    def test_strings_without_pii_are_untouched(self) -> 'None':

        result = _new_result()
        config = _new_config(['intl'], [], [])
        value = {'note': 'Nothing sensitive in this sentence at all'}

        cleaned = remove_pii(value, result, config)

        assert cleaned == {'note': 'Nothing sensitive in this sentence at all'}
        assert result.pii_removed == {}

    def test_nested_documents_are_cleaned(self) -> 'None':

        result = _new_result()
        config = _new_config(['intl'], [], [])
        value = {'rows': [{'contact': f'Reach {_email} for help'}, {'payment': f'Wire to {_valid_iban} today'}]}

        cleaned = remove_pii(value, result, config)

        assert cleaned == {'rows': [{'contact': 'Reach {{EMAIL}} for help'}, {'payment': 'Wire to {{IBAN}} today'}]}
        assert result.pii_removed == {'intl_email': 1, 'intl_iban': 1}

    def test_counts_accumulate_per_detector(self) -> 'None':

        result = _new_result()
        config = _new_config(['intl'], [], [])
        value = {
            'first':  f'One {_valid_iban} here',
            'second': f'Another ES9121000418450200051332 there, sent from {_email}',
        }

        _ = remove_pii(value, result, config)

        assert result.pii_removed == {'intl_iban': 2, 'intl_email': 1}

# ################################################################################################################################
# ################################################################################################################################
