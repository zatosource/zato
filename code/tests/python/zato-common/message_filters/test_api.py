# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy

# pytest
import pytest

# Zato
from zato.common.typing_ import stranydict
from zato.common.util.message_filters import cache
from zato.common.util.message_filters.api import apply_filter, validate_expression
from zato.common.util.message_filters.cache import get_compiled
from zato.common.util.message_filters.common import Kind_Evaluation_Error, Kind_Syntax_Error, Kind_Too_Long, \
    Max_Cache_Entries, Max_Expression_Length
from zato.common.util.truncate.measure import get_size

# ################################################################################################################################
# ################################################################################################################################

def _make_document() -> 'stranydict':

    out = {
        'customer': {'name': 'Acme', 'segment': 'enterprise'},
        'invoices': [
            {'id': 'inv-1', 'total': 250, 'status': 'paid'},
            {'id': 'inv-2', 'total': 900, 'status': 'open'},
        ]
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestProjection:

    def test_dict_projection_keeps_only_the_requested_fields(self) -> 'None':

        document = _make_document()
        result = apply_filter('invoices.{"id": id, "total": total}', document)

        assert result.was_applied is True
        assert result.has_match is True
        assert result.error == ''
        assert result.error_kind == ''
        assert result.value == [{'id': 'inv-1', 'total': 250}, {'id': 'inv-2', 'total': 900}]

    def test_list_input_is_filtered_with_a_predicate(self) -> 'None':

        document = [
            {'name': 'orders.create', 'duration_ms': 12},
            {'name': 'orders.get', 'duration_ms': 480},
            {'name': 'orders.list', 'duration_ms': 1250},
        ]
        result = apply_filter('$[duration_ms > 400].name', document)

        assert result.was_applied is True
        assert result.has_match is True
        assert result.value == ['orders.get', 'orders.list']

    def test_scalar_result_is_kept_as_is(self) -> 'None':

        document = _make_document()
        result = apply_filter('$sum(invoices.total)', document)

        assert result.was_applied is True
        assert result.has_match is True
        assert result.value == 1150

    def test_no_match_yields_none_without_a_match(self) -> 'None':

        document = _make_document()
        result = apply_filter('customer.address.city', document)

        assert result.was_applied is True
        assert result.has_match is False
        assert result.value is None

    def test_input_is_never_mutated(self) -> 'None':

        document = _make_document()
        before = deepcopy(document)

        _ = apply_filter('invoices.{"id": id}', document)

        assert document == before

    def test_sizes_are_recorded_before_and_after(self) -> 'None':

        document = _make_document()
        result = apply_filter('invoices.{"id": id}', document)

        assert result.size_before == get_size(document)
        assert result.size_after == get_size(result.value)
        assert result.size_after < result.size_before

# ################################################################################################################################
# ################################################################################################################################

class TestRefusalAndErrors:

    def test_expression_over_the_length_cap_is_refused(self) -> 'None':

        document = _make_document()
        expression = 'customer.' + 'n' * Max_Expression_Length
        result = apply_filter(expression, document)

        assert result.was_applied is False
        assert result.has_match is False
        assert result.error_kind == Kind_Too_Long
        assert str(Max_Expression_Length) in result.error
        assert result.value is document
        assert result.size_before == result.size_after

    def test_syntax_error_is_captured_and_the_input_passes_through(self) -> 'None':

        document = _make_document()
        result = apply_filter('invoices.{id: }', document)

        assert result.was_applied is False
        assert result.has_match is False
        assert result.error_kind == Kind_Syntax_Error
        assert result.error != ''
        assert result.value is document

    def test_evaluation_error_is_captured_and_the_input_passes_through(self) -> 'None':

        document = _make_document()
        result = apply_filter('$error("Test error message")', document)

        assert result.was_applied is False
        assert result.has_match is False
        assert result.error_kind == Kind_Evaluation_Error
        assert result.error == 'Test error message'
        assert result.value is document

# ################################################################################################################################
# ################################################################################################################################

class TestValidation:

    def test_valid_expression_passes(self) -> 'None':
        validate_expression('invoices.{"id": id}')

    def test_invalid_expression_raises(self) -> 'None':
        with pytest.raises(Exception):
            validate_expression('invoices.{id: }')

# ################################################################################################################################
# ################################################################################################################################

class TestCache:

    def test_repeated_expression_reuses_the_compiled_object(self) -> 'None':

        expression = 'customer.name'
        first = get_compiled(expression)
        second = get_compiled(expression)

        assert first is second

    def test_oldest_entry_is_evicted_when_the_cache_is_full(self) -> 'None':

        cache._cache.clear()

        # Fill the cache exactly to its cap ..
        for index in range(Max_Cache_Entries):
            _ = get_compiled(f'field_{index}')

        # .. the oldest entry is still there ..
        assert 'field_0' in cache._cache

        # .. one more expression pushes the cache over the cap ..
        _ = get_compiled('field_newest')

        # .. and the oldest entry made room for it.
        assert 'field_0' not in cache._cache
        assert 'field_newest' in cache._cache

        cache_size = len(cache._cache)
        assert cache_size == Max_Cache_Entries

# ################################################################################################################################
# ################################################################################################################################
