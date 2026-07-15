# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import any_, stranydict
from zato.common.util.safeguards.common import SafeguardConfig

# ################################################################################################################################
# ################################################################################################################################

def _get(config:'stranydict', key:'str', default:'any_') -> 'any_':
    """ Returns a config value, using the default when the key predates the config, e.g. for gateways
    created before a given field existed. Stored values are never None, so None always means an absent key.
    """
    out = config.get(key)

    if out is None:
        out = default

    return out

# ################################################################################################################################
# ################################################################################################################################

def build_safeguard_config(config:'stranydict') -> 'SafeguardConfig':
    """ Builds a safeguard config out of a flat config dict, e.g. an MCP gateway's opaque configuration,
    whose keys carry the safeguards_ prefix. Absent keys fall back to the dataclass defaults,
    which keep every stage off.
    """

    # Our response to produce
    out = SafeguardConfig()

    # Noise stripping
    out.strip_nulls         = _get(config, 'safeguards_strip_nulls', SafeguardConfig.strip_nulls)
    out.collapse_whitespace = _get(config, 'safeguards_collapse_whitespace', SafeguardConfig.collapse_whitespace)
    out.strip_base64        = _get(config, 'safeguards_strip_base64', SafeguardConfig.strip_base64)

    # PII removal - the list fields carry no dataclass defaults, so they are always assigned here.
    out.pii_enabled       = _get(config, 'safeguards_pii_enabled', SafeguardConfig.pii_enabled)
    out.pii_lands         = _get(config, 'safeguards_pii_lands', [])
    out.pii_detectors     = _get(config, 'safeguards_pii_detectors', [])
    out.pii_exclude       = _get(config, 'safeguards_pii_exclude', [])
    out.pii_validate      = _get(config, 'safeguards_pii_validate', SafeguardConfig.pii_validate)
    out.pii_stable_tokens = _get(config, 'safeguards_pii_stable_tokens', SafeguardConfig.pii_stable_tokens)

    # Unicode normalization
    out.normalize_unicode = _get(config, 'safeguards_normalize_unicode', SafeguardConfig.normalize_unicode)
    out.unicode_mode      = _get(config, 'safeguards_unicode_mode', SafeguardConfig.unicode_mode)

    # Markup sanitization
    out.sanitize_markup = _get(config, 'safeguards_sanitize_markup', SafeguardConfig.sanitize_markup)
    out.markup_mode     = _get(config, 'safeguards_markup_mode', SafeguardConfig.markup_mode)

    # URL policy - the allow list is another list field assigned unconditionally.
    out.url_policy_enabled = _get(config, 'safeguards_url_policy_enabled', SafeguardConfig.url_policy_enabled)
    out.url_allow_list     = _get(config, 'safeguards_url_allow_list', [])
    out.url_mode           = _get(config, 'safeguards_url_mode', SafeguardConfig.url_mode)

    return out

# ################################################################################################################################
# ################################################################################################################################

def is_safeguards_active(config:'SafeguardConfig') -> 'bool':
    """ Whether any safeguard stage is enabled at all - callers use it to skip the deep copy
    and the full walk that apply_safeguards performs even when every stage is off.
    """
    stage_flags = (
        config.strip_nulls,
        config.collapse_whitespace,
        config.strip_base64,
        config.pii_enabled,
        config.normalize_unicode,
        config.sanitize_markup,
        config.url_policy_enabled,
    )

    out = any(stage_flags)
    return out

# ################################################################################################################################
# ################################################################################################################################
