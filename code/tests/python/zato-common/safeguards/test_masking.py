# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.safeguards.api import apply_safeguards
from zato.common.util.safeguards.config import build_safeguard_config, is_safeguards_active
from zato.common.util.safeguards.masking import get_masking_config, Masked_Value, mask_fields
from zato.common.util.truncate.common import Max_Node_Count, Max_Recursion_Depth

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strset

# ################################################################################################################################
# ################################################################################################################################

def _nested(depth:'int', leaf:'anydict') -> 'anydict':
    """ A chain of dicts, each holding the next one under `child`, with the leaf at the given depth.
    """
    out:'any_' = leaf

    for _ in range(depth):
        out = {'child': out}

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMaskFields:

    def test_a_top_level_field_is_masked(self) -> 'None':
        value, count = mask_fields({'iban': 'DE89370400440532013000', 'name': 'Jane'}, {'iban'})
        assert value == {'iban': Masked_Value, 'name': 'Jane'}
        assert count == 1

    def test_nested_dicts_and_lists_are_walked(self) -> 'None':

        data = {
            'customer': {'iban': 'DE89370400440532013000'},
            'accounts': [{'iban': 'GB82WEST12345698765432'}, {'number': 7}],
            'history': [[{'iban': 'FR1420041010050500013M02606'}]],
        }

        value, count = mask_fields(data, {'iban'})

        assert value['customer']['iban'] == Masked_Value
        assert value['accounts'][0]['iban'] == Masked_Value
        assert value['accounts'][1] == {'number': 7}
        assert value['history'][0][0]['iban'] == Masked_Value
        assert count == 3

    def test_keys_are_compared_without_regard_to_case(self) -> 'None':
        value, count = mask_fields({'IBAN': 'a', 'Iban': 'b', 'iBaN': 'c'}, {'iban'})
        assert value == {'IBAN': Masked_Value, 'Iban': Masked_Value, 'iBaN': Masked_Value}
        assert count == 3

    def test_non_string_values_are_replaced_whole(self) -> 'None':

        data = {
            'number': 12345,
            'flag': True,
            'nothing': None,
            'card': {'pan': '4111111111111111', 'expiry': '12/30'},
            'codes': ['a', 'b'],
        }

        value, count = mask_fields(data, {'number', 'flag', 'nothing', 'card', 'codes'})

        assert value == dict.fromkeys(data, Masked_Value)
        assert count == 5

    def test_a_masked_container_is_not_descended_into(self) -> 'None':
        value, count = mask_fields({'card': {'card': 'x', 'pan': 'y'}}, {'card', 'pan'})
        assert value == {'card': Masked_Value}
        assert count == 1

    def test_values_are_never_matched_only_keys(self) -> 'None':
        value, count = mask_fields({'note': 'iban', 'list': ['iban']}, {'iban'})
        assert value == {'note': 'iban', 'list': ['iban']}
        assert count == 0

    def test_non_string_keys_are_left_alone(self) -> 'None':
        value, count = mask_fields({1: 'one', 'iban': 'x'}, {'iban', '1'})
        assert value == {1: 'one', 'iban': Masked_Value}
        assert count == 1

    def test_scalars_pass_through(self) -> 'None':
        for scalar in ['iban', 7, None, True]:
            value, count = mask_fields(scalar, {'iban'})
            assert value == scalar
            assert count == 0

    def test_no_field_names_masks_nothing(self) -> 'None':
        value, count = mask_fields({'iban': 'x'}, set())
        assert value == {'iban': 'x'}
        assert count == 0

    def test_a_field_within_the_depth_limit_is_masked(self) -> 'None':
        data = _nested(Max_Recursion_Depth, {'iban': 'x'})
        _, count = mask_fields(data, {'iban'})
        assert count == 1

    def test_a_field_beyond_the_depth_limit_is_not_reached(self) -> 'None':
        data = _nested(Max_Recursion_Depth + 1, {'iban': 'x'})
        _, count = mask_fields(data, {'iban'})
        assert count == 0

    def test_the_walk_stops_at_the_node_budget(self) -> 'None':
        data = [{'iban': 'x'} for _ in range(Max_Node_Count + 10)]
        _, count = mask_fields(data, {'iban'})
        assert count == Max_Node_Count - 1

# ################################################################################################################################
# ################################################################################################################################

class TestMaskingConfiguration:

    def test_masking_is_off_by_default(self) -> 'None':
        config = build_safeguard_config({})
        assert config.masking_enabled is False
        assert config.masked_fields == set()
        assert is_safeguards_active(config) is False

    def test_a_set_turns_masking_on(self) -> 'None':
        config = build_safeguard_config({'safeguards_masking_sets': ['banking']})
        assert config.masking_enabled is True
        assert 'iban' in config.masked_fields
        assert is_safeguards_active(config) is True

    def test_custom_fields_alone_turn_masking_on(self) -> 'None':
        config = build_safeguard_config({'safeguards_masking_custom_fields': ['Loyalty_Id']})
        assert config.masking_enabled is True
        assert config.masked_fields == {'loyalty_id'}

    def test_custom_fields_switched_off_alone_leave_masking_off(self) -> 'None':

        config = build_safeguard_config({
            'safeguards_masking_custom_fields': ['loyalty_id'],
            'safeguards_masking_custom_enabled': False,
        })

        assert config.masking_enabled is False
        assert is_safeguards_active(config) is False

    def test_an_exclusion_does_not_reach_custom_fields(self) -> 'None':

        config = build_safeguard_config({
            'safeguards_masking_custom_fields': ['loyalty_id'],
            'safeguards_masking_excluded': ['LOYALTY_ID'],
        })

        assert config.masked_fields == {'loyalty_id'}

    def test_the_pipeline_masks_and_counts(self) -> 'None':

        config = build_safeguard_config({'safeguards_masking_custom_fields': ['secret_code']})
        original = {'secret_code': 'abc', 'items': [{'Secret_Code': 'def'}]}

        result = apply_safeguards(original, config)

        assert result.value == {'secret_code': Masked_Value, 'items': [{'Secret_Code': Masked_Value}]}
        assert result.fields_masked == 2
        assert result.was_modified is True

        # The caller's object is never mutated.
        assert original == {'secret_code': 'abc', 'items': [{'Secret_Code': 'def'}]}

    def test_the_pipeline_masks_before_pii_removal(self) -> 'None':

        config = build_safeguard_config({
            'safeguards_masking_custom_fields': ['contact'],
            'safeguards_pii_enabled': True,
            'safeguards_pii_detectors': ['email'],
        })

        result = apply_safeguards({'contact': 'jane@example.com', 'note': 'mail jane@example.com'}, config)

        assert result.value['contact'] == Masked_Value
        assert 'jane@example.com' not in result.value['note']
        assert result.fields_masked == 1
        assert result.pii_removed == {'email': 1}

    def test_an_exclusion_covers_every_set_listing_the_field(self) -> 'None':

        config = build_safeguard_config({
            'safeguards_masking_sets': ['common', 'banking'],
            'safeguards_masking_excluded': ['email'],
        })

        assert 'email' not in config.masked_fields
        assert 'iban' in config.masked_fields

# ################################################################################################################################
# ################################################################################################################################

class TestMaskingSets:

    def test_no_set_lists_a_field_twice(self) -> 'None':

        for item in get_masking_config():

            seen:'strset' = set()

            for field_name in item['fields']:
                field_name_lower = field_name.lower()
                assert field_name_lower not in seen, (item['name'], field_name)
                seen.add(field_name_lower)

# ################################################################################################################################
# ################################################################################################################################
