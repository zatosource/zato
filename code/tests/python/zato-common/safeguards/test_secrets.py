# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.safeguards.api import apply_safeguards
from zato.common.util.safeguards.common import SafeguardConfig, SafeguardResult
from zato.common.util.safeguards.config import build_safeguard_config, is_safeguards_active
from zato.common.util.safeguards.detectors.secrets import Region_Secrets
from zato.common.util.safeguards.names import get_detector_choices, get_land_choices
from zato.common.util.safeguards.secrets_ import remove_secrets

# ################################################################################################################################
# ################################################################################################################################

# One value of each credential shape the detectors recognize, used throughout.
_private_key = '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA7\nMIIEowIBAAKCAQEA8\n-----END RSA PRIVATE KEY-----'
_aws_key     = 'AKIAIOSFODNN7EXAMPLE'
_jwt         = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0In0.abcdefghij123456'
_bearer      = 'Bearer abc123def456ghi789jkl'
_conn_string = 'postgres://crm_user:s3cr3t-pass@db.internal:5432/crm'
_api_token   = 'sk-abcdefghijklmnopqrstuv'

# ################################################################################################################################
# ################################################################################################################################

def _new_result() -> 'SafeguardResult':
    """ Returns a fresh result for direct stage calls.
    """
    out = SafeguardResult()
    out.pii_removed = {}
    out.secrets_removed = {}
    out.signals = {}

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDetectorShapes:

    def test_a_private_key_block_is_replaced_whole(self) -> 'None':

        result = _new_result()
        value = {'note': f'The deploy log pasted this key:\n{_private_key}\nplease rotate it'}

        cleaned = remove_secrets(value, result)

        assert 'PRIVATE KEY' not in cleaned['note']
        assert 'MIIEowIBAAKCAQEA7' not in cleaned['note']
        assert result.secrets_removed == {'secret_private_key': 1}

    def test_an_aws_access_key_is_replaced(self) -> 'None':

        result = _new_result()
        value = {'note': f'The backup job signs with {_aws_key} since March'}

        cleaned = remove_secrets(value, result)

        assert _aws_key not in cleaned['note']
        assert result.secrets_removed == {'secret_aws_access_key': 1}

    def test_a_jwt_is_replaced(self) -> 'None':

        result = _new_result()
        value = {'note': f'The session carries {_jwt} in its cookie'}

        cleaned = remove_secrets(value, result)

        assert _jwt not in cleaned['note']
        assert result.secrets_removed == {'secret_jwt': 1}

    def test_a_bearer_value_is_replaced_with_its_scheme(self) -> 'None':

        result = _new_result()
        value = {'note': f'The header read Authorization: {_bearer} on each call'}

        cleaned = remove_secrets(value, result)

        assert _bearer not in cleaned['note']
        assert result.secrets_removed == {'secret_bearer': 1}

    def test_a_connection_string_with_a_password_is_replaced(self) -> 'None':

        result = _new_result()
        value = {'note': f'The reporting job connects to {_conn_string} nightly'}

        cleaned = remove_secrets(value, result)

        assert 's3cr3t-pass' not in cleaned['note']
        assert result.secrets_removed == {'secret_connection_string': 1}

    def test_a_prefixed_api_token_is_replaced(self) -> 'None':

        result = _new_result()
        value = {'note': f'The integration was set up with {_api_token} last week'}

        cleaned = remove_secrets(value, result)

        assert _api_token not in cleaned['note']
        assert result.secrets_removed == {'secret_api_token': 1}

    def test_ordinary_text_passes_untouched(self) -> 'None':

        result = _new_result()
        value = {'note': 'The quarterly report is ready for review, order ORD-7002 shipped'}

        cleaned = remove_secrets(value, result)

        assert cleaned == value
        assert result.secrets_removed == {}

# ################################################################################################################################
# ################################################################################################################################

class TestStableReplacements:

    def test_the_same_secret_renders_as_the_same_token(self) -> 'None':

        result = _new_result()
        value = {'note': f'Key {_aws_key} rotated, previous value was {_aws_key} too'}

        cleaned = remove_secrets(value, result)

        # Both mentions of the one key collapse into one numbered replacement
        assert cleaned['note'] == 'Key REPLACED_SECRET_AWS_ACCESS_KEY_1 rotated, previous value was REPLACED_SECRET_AWS_ACCESS_KEY_1 too'
        assert result.secrets_removed == {'secret_aws_access_key': 2}

    def test_two_different_secrets_render_as_two_tokens(self) -> 'None':

        result = _new_result()
        other_key = 'AKIAJ73NDNN7EXAMPLE2'
        value = {'note': f'Old key {_aws_key} was replaced by {other_key} in May'}

        cleaned = remove_secrets(value, result)

        assert cleaned['note'] == 'Old key REPLACED_SECRET_AWS_ACCESS_KEY_1 was replaced by REPLACED_SECRET_AWS_ACCESS_KEY_2 in May'
        assert result.secrets_removed == {'secret_aws_access_key': 2}

# ################################################################################################################################
# ################################################################################################################################

class TestPipeline:

    def test_the_enabled_stage_runs_through_apply_safeguards(self) -> 'None':

        config = SafeguardConfig()
        config.secrets_enabled = True

        value = {'note': f'The job signs with {_aws_key} and reads {_conn_string}'}

        result = apply_safeguards(value, config)

        assert _aws_key not in result.value['note']
        assert 's3cr3t-pass' not in result.value['note']
        assert result.was_modified is True
        assert result.secrets_removed == {'secret_aws_access_key': 1, 'secret_connection_string': 1}

        # The caller's own document is never mutated
        assert _aws_key in value['note']

    def test_the_disabled_stage_leaves_secrets_in_place(self) -> 'None':

        config = SafeguardConfig()

        value = {'note': f'The job signs with {_aws_key} since March'}

        result = apply_safeguards(value, config)

        assert result.value == value
        assert result.secrets_removed == {}

# ################################################################################################################################
# ################################################################################################################################

class TestConfig:

    def test_the_flag_is_read_from_the_flat_config(self) -> 'None':

        config = build_safeguard_config({'safeguards_secrets_enabled': True})
        assert config.secrets_enabled is True

    def test_an_absent_key_keeps_the_stage_off(self) -> 'None':

        config = build_safeguard_config({})
        assert config.secrets_enabled is False

    def test_the_stage_alone_makes_safeguards_active(self) -> 'None':

        config = SafeguardConfig()
        assert is_safeguards_active(config) is False

        config.secrets_enabled = True
        assert is_safeguards_active(config) is True

# ################################################################################################################################
# ################################################################################################################################

class TestNameChoices:

    def test_the_secrets_region_is_not_a_land(self) -> 'None':

        land_codes = []

        for code, _land_name in get_land_choices():
            land_codes.append(code)

        assert Region_Secrets not in land_codes

    def test_the_secrets_detectors_are_not_pii_choices(self) -> 'None':

        detector_names = []

        for _group_name, group in get_detector_choices():
            for name, _label in group:
                detector_names.append(name)

        for name in detector_names:
            assert not name.startswith('secret_'), name

# ################################################################################################################################
# ################################################################################################################################
