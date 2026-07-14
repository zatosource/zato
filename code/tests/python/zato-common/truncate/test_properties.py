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
from zato.common.util.truncate.api import truncate_json
from zato.common.util.truncate.common import Min_Usable_Cap, Report_Budget, Report_Key
from zato.common.util.truncate.measure import get_size, serialize

# ################################################################################################################################
# ################################################################################################################################

def _extend_with_containers(children:'any_') -> 'any_':
    """ Wraps child strategies in lists and dicts, so documents of arbitrary nesting are generated.
    """
    lists = st.lists(children, max_size=15)
    dicts = st.dictionaries(st.text(max_size=15), children, max_size=15)

    out = st.one_of(lists, dicts)

    return out

# ################################################################################################################################

_scalars = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(min_value=-1000000, max_value=1000000),
    st.floats(allow_nan=False, allow_infinity=False),
    st.text(max_size=800),
)

_documents = st.recursive(_scalars, _extend_with_containers, max_leaves=60)

_fractions = st.floats(min_value=0.2, max_value=1.5)

# ################################################################################################################################
# ################################################################################################################################

def _assert_keys_preserved(original:'any_', degraded:'any_', is_root:'bool') -> 'None':
    """ Asserts that the degraded document kept every object key of the original, recursively -
    arrays may be shorter and strings may be cut, but keys never vanish.
    """
    if isinstance(original, dict):

        degraded_keys = set(degraded.keys())

        # The report key is the one addition allowed, and only at the root.
        if is_root:
            degraded_keys.discard(Report_Key)

        assert degraded_keys == set(original.keys())

        for key in original:
            _assert_keys_preserved(original[key], degraded[key], False)

    elif isinstance(original, list):

        # Arrays only ever lose elements from the tail, so the survivors match the original head.
        assert len(degraded) <= len(original)

        for index, degraded_item in enumerate(degraded):
            _assert_keys_preserved(original[index], degraded_item, False)

# ################################################################################################################################
# ################################################################################################################################

class TestProperties:

    @given(document=_documents, fraction=_fractions)
    @settings(max_examples=30, deadline=None)
    def test_invariants_hold_for_every_document(self, document:'any_', fraction:'float') -> 'None':

        size_before = get_size(document)

        cap = int(size_before * fraction)
        if cap < Min_Usable_Cap:
            cap = Min_Usable_Cap

        snapshot = deepcopy(document)
        result = truncate_json(document, cap)

        # The input is never mutated.
        assert document == snapshot

        # The output is always valid JSON.
        serialized = serialize(result.value)
        _ = loads(serialized)

        # The reported sizes are real.
        assert result.size_before == size_before
        assert result.size_after == get_size(result.value)

        # Whenever the result claims to fit, it fits.
        if result.did_fit:
            assert result.size_after <= cap

        # Object keys survive every truncation.
        if result.was_truncated:
            _assert_keys_preserved(snapshot, result.value, True)

        # Truncation is deterministic - the same document and cap always degrade identically.
        rerun = truncate_json(deepcopy(snapshot), cap)

        assert serialize(rerun.value) == serialized

        # When the report is embedded, it always fits its budget and always costs less
        # than the bytes it accounts for.
        if isinstance(result.value, dict):
            if Report_Key in result.value:

                report = result.value[Report_Key]

                assert get_size(report) <= Report_Budget

                body = {}
                for key, value in result.value.items():
                    if key != Report_Key:
                        body[key] = value

                body_size = get_size(body)
                bytes_removed = size_before - body_size
                report_cost = result.size_after - body_size

                assert report_cost < bytes_removed

# ################################################################################################################################
# ################################################################################################################################
