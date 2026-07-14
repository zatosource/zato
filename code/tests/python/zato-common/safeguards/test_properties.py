# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from json import loads

# hypothesis
from hypothesis import given, settings, strategies as st

# Zato
from zato.common.typing_ import any_
from zato.common.util.safeguards.api import apply_safeguards
from zato.common.util.safeguards.common import SafeguardConfig
from zato.common.util.truncate.measure import get_size, serialize

# ################################################################################################################################
# ################################################################################################################################

def _extend_with_containers(children:'any_') -> 'any_':
    """ Wraps child strategies in lists and dicts, so documents of arbitrary nesting are generated.
    """
    lists = st.lists(children, max_size=10)
    dicts = st.dictionaries(st.text(max_size=10), children, max_size=10)

    out = st.one_of(lists, dicts)

    return out

# ################################################################################################################################

_scalars = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(min_value=-1000000, max_value=1000000),
    st.floats(allow_nan=False, allow_infinity=False),
    st.text(max_size=200),
)

_documents = st.recursive(_scalars, _extend_with_containers, max_leaves=40)

_toggles = st.booleans()

# ################################################################################################################################
# ################################################################################################################################

def _new_config(
    strip_nulls:'bool',
    collapse_whitespace:'bool',
    strip_base64:'bool',
    normalize_unicode:'bool',
    sanitize_markup:'bool',
    url_policy_enabled:'bool',
    pii_enabled:'bool',
    ) -> 'SafeguardConfig':
    """ Returns a config with the given stages enabled, all in clean mode.
    """
    out = SafeguardConfig()
    out.strip_nulls = strip_nulls
    out.collapse_whitespace = collapse_whitespace
    out.strip_base64 = strip_base64
    out.normalize_unicode = normalize_unicode
    out.sanitize_markup = sanitize_markup
    out.url_policy_enabled = url_policy_enabled
    out.url_allow_list = ['zato.io']
    out.pii_enabled = pii_enabled
    out.pii_lands = ['intl']
    out.pii_detectors = []
    out.pii_exclude = []

    return out

# ################################################################################################################################
# ################################################################################################################################

def _assert_structure(original:'any_', cleaned:'any_', nulls_stripped:'bool') -> 'None':
    """ Asserts that the cleaned document kept the structure of the original - array lengths never change
    and the only keys allowed to vanish are null-valued ones when null stripping is active.
    """
    if isinstance(original, dict):

        for key, child in original.items():

            if child is None:
                if nulls_stripped:
                    assert key not in cleaned
                else:
                    assert cleaned[key] is None
            else:
                _assert_structure(child, cleaned[key], nulls_stripped)

    elif isinstance(original, list):

        assert len(cleaned) == len(original)

        for index, child in enumerate(original):
            _assert_structure(child, cleaned[index], nulls_stripped)

# ################################################################################################################################
# ################################################################################################################################

class TestProperties:

    @given(
        document=_documents,
        strip_nulls=_toggles,
        collapse_whitespace=_toggles,
        strip_base64=_toggles,
        normalize_unicode=_toggles,
        sanitize_markup=_toggles,
        url_policy_enabled=_toggles,
        pii_enabled=_toggles,
    )
    @settings(max_examples=30, deadline=None)
    def test_invariants_hold_for_every_document(
        self,
        document:'any_',
        strip_nulls:'bool',
        collapse_whitespace:'bool',
        strip_base64:'bool',
        normalize_unicode:'bool',
        sanitize_markup:'bool',
        url_policy_enabled:'bool',
        pii_enabled:'bool',
        ) -> 'None':

        config = _new_config(
            strip_nulls, collapse_whitespace, strip_base64, normalize_unicode,
            sanitize_markup, url_policy_enabled, pii_enabled)

        snapshot = deepcopy(document)
        result = apply_safeguards(document, config)

        # The input is never mutated.
        assert document == snapshot

        # Clean modes never reject.
        assert result.was_rejected is False

        # The output is always valid JSON.
        serialized = serialize(result.value)
        _ = loads(serialized)

        # The reported sizes are real.
        assert result.size_before == get_size(snapshot)
        assert result.size_after == get_size(result.value)

        # Structure survives - array lengths never change, only null-valued keys may vanish.
        _assert_structure(snapshot, result.value, strip_nulls)

        # The safeguards are deterministic - the same document and config always clean identically.
        rerun = apply_safeguards(deepcopy(snapshot), config)

        assert serialize(rerun.value) == serialized

        # A second pass over an already safeguarded document changes nothing.
        second = apply_safeguards(deepcopy(result.value), config)

        assert serialize(second.value) == serialized

# ################################################################################################################################
# ################################################################################################################################
