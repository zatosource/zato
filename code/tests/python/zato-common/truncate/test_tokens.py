# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import dictlist
from zato.common.util.truncate.measure import serialize
from zato.common.util.truncate.tokens import apply_token_cap, build_token_cap_config, Default_Characters_Per_Token, \
    estimate_tokens, Size_Cap_Mode_Block, Size_Cap_Mode_Truncate, TokenCapConfig

# ################################################################################################################################
# ################################################################################################################################

def _new_config(
    max_response_tokens:'int',
    min_threshold_tokens:'int',
    size_cap_mode:'str'=Size_Cap_Mode_Truncate,
    characters_per_token:'float'=Default_Characters_Per_Token,
) -> 'TokenCapConfig':

    out = TokenCapConfig()
    out.max_response_tokens = max_response_tokens
    out.min_threshold_tokens = min_threshold_tokens
    out.size_cap_mode = size_cap_mode
    out.characters_per_token = characters_per_token

    return out

# ################################################################################################################################

def _make_rows(count:'int') -> 'dictlist':
    out = []
    for index in range(count):
        row = {'id': f'inv-{index:05}', 'amount': index * 1.5, 'customer': 'Customer name here'}
        out.append(row)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestEstimator:

    def test_estimate_divides_characters_by_the_ratio_and_rounds_up(self) -> 'None':

        # The canonical form is {"a":1} - seven characters, which at four characters per token rounds up to two.
        document = {'a': 1}

        assert len(serialize(document)) == 7
        assert estimate_tokens(document, 4.0) == 2

    def test_estimate_accepts_a_fractional_ratio(self) -> 'None':

        # The canonical form is seven characters again - at 3.5 characters per token that is exactly two tokens.
        document = {'a': 1}

        assert estimate_tokens(document, 3.5) == 2

    def test_estimate_of_an_exact_multiple_does_not_round_up(self) -> 'None':

        # The canonical form is "abcdefgh" - ten characters with the quotes, five tokens at two characters each.
        document = 'abcdefgh'

        assert estimate_tokens(document, 2.0) == 5

# ################################################################################################################################
# ################################################################################################################################

class TestPassthrough:

    def test_value_below_the_threshold_is_skipped(self) -> 'None':

        document = {'status': 'ok'}
        config = _new_config(1, 1000)

        result = apply_token_cap(document, config)

        assert result.value is document
        assert result.was_skipped is True
        assert result.was_blocked is False
        assert result.was_truncated is False
        assert result.tokens_before == result.tokens_after
        assert result.report == []

    def test_value_within_the_cap_passes_through_untouched(self) -> 'None':

        document = {'status': 'ok', 'total': 3}
        config = _new_config(1000, 0)

        result = apply_token_cap(document, config)

        assert result.value is document
        assert result.did_fit is True
        assert result.was_skipped is False
        assert result.was_truncated is False
        assert result.tokens_before == result.tokens_after

    def test_cap_of_zero_means_no_cap(self) -> 'None':

        document = {'rows': _make_rows(500)}
        config = _new_config(0, 0)

        result = apply_token_cap(document, config)

        assert result.value is document
        assert result.did_fit is True
        assert result.was_truncated is False

# ################################################################################################################################
# ################################################################################################################################

class TestEnforcement:

    def test_block_mode_flags_the_result_and_leaves_the_value_untouched(self) -> 'None':

        document = {'rows': _make_rows(500)}
        config = _new_config(10, 0, Size_Cap_Mode_Block)

        result = apply_token_cap(document, config)

        assert result.value is document
        assert result.was_blocked is True
        assert result.was_truncated is False
        assert result.did_fit is False
        assert result.tokens_before == result.tokens_after
        assert result.report == []

    def test_truncate_mode_trims_the_value_to_fit_the_token_budget(self) -> 'None':

        # 2048 tokens at four characters each is an 8192-byte budget for graceful trimming.
        document = {'status': 'ok', 'rows': _make_rows(2000)}
        config = _new_config(2048, 0)

        result = apply_token_cap(document, config)

        assert result.was_truncated is True
        assert result.did_fit is True
        assert result.tokens_before > config.max_response_tokens
        assert result.tokens_after <= config.max_response_tokens
        assert len(result.report) > 0

        # The scalar fields survive the trimming and the input itself is never mutated.
        assert result.value['status'] == 'ok'
        assert len(document['rows']) == 2000

    def test_truncate_mode_respects_a_fractional_ratio(self) -> 'None':

        # 4000 tokens at 3.5 characters each is a 14000-byte budget.
        document = {'rows': _make_rows(3000)}
        config = _new_config(4000, 0, Size_Cap_Mode_Truncate, 3.5)

        result = apply_token_cap(document, config)

        assert result.was_truncated is True
        assert result.did_fit is True
        assert result.tokens_after <= config.max_response_tokens

# ################################################################################################################################
# ################################################################################################################################

class TestBuildConfig:

    def test_empty_config_keeps_the_cap_off(self) -> 'None':

        config = build_token_cap_config({})

        assert config.max_response_tokens == 0
        assert config.min_threshold_tokens == 0
        assert config.size_cap_mode == Size_Cap_Mode_Truncate
        assert config.characters_per_token == Default_Characters_Per_Token

    def test_full_config_maps_every_field(self) -> 'None':

        gateway_config = {
            'max_response_size': 25000,
            'min_size_threshold': 500,
            'size_cap_mode': Size_Cap_Mode_Block,
            'characters_per_token': 3.5,
        }

        config = build_token_cap_config(gateway_config)

        assert config.max_response_tokens == 25000
        assert config.min_threshold_tokens == 500
        assert config.size_cap_mode == Size_Cap_Mode_Block
        assert config.characters_per_token == 3.5

    def test_stored_zero_is_kept_and_not_replaced_by_a_default(self) -> 'None':

        gateway_config = {
            'max_response_size': 0,
            'min_size_threshold': 0,
        }

        config = build_token_cap_config(gateway_config)

        assert config.max_response_tokens == 0
        assert config.min_threshold_tokens == 0

    def test_built_config_drives_the_cap(self) -> 'None':

        gateway_config = {
            'max_response_size': 10,
            'size_cap_mode': Size_Cap_Mode_Block,
        }

        config = build_token_cap_config(gateway_config)
        document = {'rows': _make_rows(500)}

        result = apply_token_cap(document, config)

        assert result.was_blocked is True

# ################################################################################################################################
# ################################################################################################################################
