# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy

# Zato
from zato.common.util.safeguards.api import apply_safeguards
from zato.common.util.safeguards.common import Mode_Reject, SafeguardConfig, Url_Marker
from zato.common.util.truncate.measure import get_size

# ################################################################################################################################
# ################################################################################################################################

def _new_full_config() -> 'SafeguardConfig':
    """ Returns a config with every stage enabled in clean mode.
    """
    out = SafeguardConfig()
    out.strip_nulls = True
    out.collapse_whitespace = True
    out.strip_base64 = True
    out.normalize_unicode = True
    out.sanitize_markup = True
    out.url_policy_enabled = True
    out.url_allow_list = ['zato.io']
    out.pii_enabled = True
    out.pii_lands = ['intl']
    out.pii_detectors = []
    out.pii_exclude = []

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPassthrough:

    def test_all_off_config_is_a_passthrough(self) -> 'None':

        config = SafeguardConfig()
        value = {'note': 'Pay to DE89370400440532013000  now', 'empty': None, 'link': 'https://example.com/x'}

        result = apply_safeguards(value, config)

        assert result.value == value
        assert result.was_modified is False
        assert result.was_rejected is False
        assert result.size_before == result.size_after
        assert result.pii_removed == {}
        assert result.signals == {}

    def test_enabled_stages_with_nothing_to_do_leave_the_value_alone(self) -> 'None':

        config = _new_full_config()
        value = {'note': 'A perfectly clean sentence', 'link': 'See https://zato.io/docs today'}

        result = apply_safeguards(value, config)

        assert result.value == value
        assert result.was_modified is False
        assert result.was_rejected is False

# ################################################################################################################################
# ################################################################################################################################

class TestSingleToggles:

    def test_strip_nulls_alone(self) -> 'None':

        config = SafeguardConfig()
        config.strip_nulls = True

        value = {'name': 'First invoice', 'reference': None}

        result = apply_safeguards(value, config)

        assert result.value == {'name': 'First invoice'}
        assert result.nulls_removed == 1
        assert result.was_modified is True

    def test_collapse_whitespace_alone(self) -> 'None':

        config = SafeguardConfig()
        config.collapse_whitespace = True

        value = {'note': 'Two  spaces'}

        result = apply_safeguards(value, config)

        assert result.value == {'note': 'Two spaces'}
        assert result.whitespace_chars_removed == 1

    def test_strip_base64_alone(self) -> 'None':

        config = SafeguardConfig()
        config.strip_base64 = True

        blob = 'QUJD' * 100
        value = {'attachment': blob}

        result = apply_safeguards(value, config)

        assert result.base64_blobs_removed == 1
        assert blob not in result.value['attachment']

    def test_normalize_unicode_alone(self) -> 'None':

        config = SafeguardConfig()
        config.normalize_unicode = True

        value = {'note': 'a\u200bb'}

        result = apply_safeguards(value, config)

        assert result.value == {'note': 'ab'}
        assert result.unicode_chars_removed == 1
        assert result.was_rejected is False

    def test_sanitize_markup_alone(self) -> 'None':

        config = SafeguardConfig()
        config.sanitize_markup = True

        value = {'body': 'Before <script>a()</script> after'}

        result = apply_safeguards(value, config)

        assert result.value == {'body': 'Before  after'}
        assert result.markup_items_removed == 1
        assert result.was_rejected is False

    def test_url_policy_alone(self) -> 'None':

        config = SafeguardConfig()
        config.url_policy_enabled = True
        config.url_allow_list = ['zato.io']

        value = {'link': 'Get it from https://example.com/payload now'}

        result = apply_safeguards(value, config)

        assert result.value == {'link': f'Get it from {Url_Marker} now'}
        assert result.urls_flagged == 1
        assert result.was_rejected is False

    def test_pii_alone(self) -> 'None':

        config = SafeguardConfig()
        config.pii_enabled = True
        config.pii_lands = ['intl']
        config.pii_detectors = []
        config.pii_exclude = []

        value = {'note': 'Pay to DE89370400440532013000 today'}

        result = apply_safeguards(value, config)

        assert result.value == {'note': 'Pay to {{IBAN}} today'}
        assert result.pii_removed == {'intl_iban': 1}

# ################################################################################################################################
# ################################################################################################################################

class TestStageOrder:

    def test_unicode_runs_before_pii(self) -> 'None':

        # A zero-width space inside the IBAN would hide it from the detector -
        # normalization runs first, so the detector still fires.
        config = _new_full_config()
        value = {'payment': 'Pay to DE89\u200b370400440532013000 today'}

        result = apply_safeguards(value, config)

        assert result.value == {'payment': 'Pay to {{IBAN}} today'}
        assert result.unicode_chars_removed == 1
        assert result.pii_removed == {'intl_iban': 1}

    def test_all_stages_together(self) -> 'None':

        config = _new_full_config()
        blob = 'QUJD' * 100

        value = {
            'empty': None,
            'attachment': blob,
            'note': 'Contact  alice@example.com <script>x()</script> via https://example.com/x',
        }

        result = apply_safeguards(value, config)

        assert result.nulls_removed == 1
        assert result.base64_blobs_removed == 1
        assert result.whitespace_chars_removed >= 1
        assert result.markup_items_removed == 1
        assert result.urls_flagged == 1
        assert result.pii_removed == {'intl_email': 1}
        assert result.was_modified is True
        assert result.was_rejected is False

# ################################################################################################################################
# ################################################################################################################################

class TestRejectModes:

    def test_reject_mode_with_a_clean_document_completes(self) -> 'None':

        config = _new_full_config()
        config.unicode_mode = Mode_Reject
        config.markup_mode = Mode_Reject

        value = {'note': 'A perfectly clean sentence'}

        result = apply_safeguards(value, config)

        assert result.was_rejected is False
        assert result.reject_kind == ''

# ################################################################################################################################
# ################################################################################################################################

class TestRoots:

    def test_string_root_is_replaced_through_the_return_value(self) -> 'None':

        config = _new_full_config()
        value = 'Wire the amount to DE89370400440532013000 by Friday'

        result = apply_safeguards(value, config)

        assert result.value == 'Wire the amount to {{IBAN}} by Friday'
        assert result.pii_removed == {'intl_iban': 1}

    def test_list_root_is_walked(self) -> 'None':

        config = _new_full_config()
        value = ['Reach alice@example.com for help', {'reference': None}]

        result = apply_safeguards(value, config)

        assert result.value == ['Reach {{EMAIL}} for help', {}]
        assert result.nulls_removed == 1

    def test_scalar_root_passes_unchanged(self) -> 'None':

        config = _new_full_config()
        value = 12345

        result = apply_safeguards(value, config)

        assert result.value == 12345
        assert result.was_modified is False

# ################################################################################################################################
# ################################################################################################################################

class TestAccounting:

    def test_input_is_never_mutated(self) -> 'None':

        config = _new_full_config()
        value = {'empty': None, 'note': 'Pay  to DE89370400440532013000 <script>x()</script>'}
        snapshot = deepcopy(value)

        _ = apply_safeguards(value, config)

        assert value == snapshot

    def test_sizes_are_real(self) -> 'None':

        config = _new_full_config()
        value = {'empty': None, 'note': 'Pay  to DE89370400440532013000 via https://example.com/x'}

        result = apply_safeguards(value, config)

        assert result.size_before == get_size(value)
        assert result.size_after == get_size(result.value)

# ################################################################################################################################
# ################################################################################################################################
