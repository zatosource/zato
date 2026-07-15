# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.safeguards.api import apply_safeguards
from zato.common.util.safeguards.common import Mode_Clean, Mode_Reject, Url_Mode_Neutralize, Url_Mode_Remove
from zato.common.util.safeguards.config import build_safeguard_config, is_safeguards_active

# ################################################################################################################################
# ################################################################################################################################

class TestBuildSafeguardConfig:

    def test_empty_config_keeps_every_stage_off(self) -> 'None':

        config = build_safeguard_config({})

        assert config.strip_nulls is False
        assert config.collapse_whitespace is False
        assert config.strip_base64 is False

        assert config.pii_enabled is False
        assert config.pii_lands == []
        assert config.pii_detectors == []
        assert config.pii_exclude == []
        assert config.pii_validate is True
        assert config.pii_stable_tokens is False

        assert config.normalize_unicode is False
        assert config.unicode_mode == Mode_Clean

        assert config.sanitize_markup is False
        assert config.markup_mode == Mode_Clean

        assert config.url_policy_enabled is False
        assert config.url_allow_list == []
        assert config.url_mode == Url_Mode_Remove

    def test_full_config_maps_every_field(self) -> 'None':

        gateway_config = {
            'safeguards_strip_nulls': True,
            'safeguards_collapse_whitespace': True,
            'safeguards_strip_base64': True,
            'safeguards_pii_enabled': True,
            'safeguards_pii_lands': ['es', 'de'],
            'safeguards_pii_detectors': ['intl_iban'],
            'safeguards_pii_exclude': ['es_phone'],
            'safeguards_pii_validate': False,
            'safeguards_pii_stable_tokens': True,
            'safeguards_normalize_unicode': True,
            'safeguards_unicode_mode': Mode_Reject,
            'safeguards_sanitize_markup': True,
            'safeguards_markup_mode': Mode_Reject,
            'safeguards_url_policy_enabled': True,
            'safeguards_url_allow_list': ['example.com', 'api.invoicing.example'],
            'safeguards_url_mode': Url_Mode_Neutralize,
        }

        config = build_safeguard_config(gateway_config)

        assert config.strip_nulls is True
        assert config.collapse_whitespace is True
        assert config.strip_base64 is True

        assert config.pii_enabled is True
        assert config.pii_lands == ['es', 'de']
        assert config.pii_detectors == ['intl_iban']
        assert config.pii_exclude == ['es_phone']
        assert config.pii_validate is False
        assert config.pii_stable_tokens is True

        assert config.normalize_unicode is True
        assert config.unicode_mode == Mode_Reject

        assert config.sanitize_markup is True
        assert config.markup_mode == Mode_Reject

        assert config.url_policy_enabled is True
        assert config.url_allow_list == ['example.com', 'api.invoicing.example']
        assert config.url_mode == Url_Mode_Neutralize

    def test_stored_false_is_kept_and_not_replaced_by_a_default(self) -> 'None':

        gateway_config = {
            'safeguards_pii_validate': False,
        }

        config = build_safeguard_config(gateway_config)

        assert config.pii_validate is False

    def test_built_config_drives_the_safeguards(self) -> 'None':

        gateway_config = {
            'safeguards_strip_nulls': True,
        }

        config = build_safeguard_config(gateway_config)
        document = {'customer': 'Customer name here', 'middle_name': None}

        result = apply_safeguards(document, config)

        assert result.value == {'customer': 'Customer name here'}
        assert result.nulls_removed == 1

# ################################################################################################################################
# ################################################################################################################################

class TestIsSafeguardsActive:

    def test_a_config_with_every_stage_off_is_inactive(self) -> 'None':

        config = build_safeguard_config({})

        assert is_safeguards_active(config) is False

    def test_any_single_enabled_stage_makes_the_config_active(self) -> 'None':

        stage_keys = (
            'safeguards_strip_nulls',
            'safeguards_collapse_whitespace',
            'safeguards_strip_base64',
            'safeguards_pii_enabled',
            'safeguards_normalize_unicode',
            'safeguards_sanitize_markup',
            'safeguards_url_policy_enabled',
        )

        for key in stage_keys:
            config = build_safeguard_config({key: True})
            assert is_safeguards_active(config) is True, key

    def test_non_stage_fields_alone_do_not_make_the_config_active(self) -> 'None':

        gateway_config = {
            'safeguards_pii_validate': True,
            'safeguards_pii_stable_tokens': True,
            'safeguards_unicode_mode': Mode_Reject,
            'safeguards_url_allow_list': ['example.com'],
        }

        config = build_safeguard_config(gateway_config)

        assert is_safeguards_active(config) is False

# ################################################################################################################################
# ################################################################################################################################
