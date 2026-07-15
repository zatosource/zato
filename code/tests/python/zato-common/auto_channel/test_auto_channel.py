# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.auto_channel import collect_family_patterns, Default_Prefix, Family_Exclude, Family_Include, \
    get_auto_channel_config, get_auto_channel_url_path, is_channel_active, matches_any, matches_pattern, should_create_channel

# ################################################################################################################################
# ################################################################################################################################

class TestCollectFamilyPatterns:

    def test_base_variable_alone(self) -> 'None':

        environ = {'Zato_Auto_REST_Channel_Include': 'api.customer.get'}
        patterns = collect_family_patterns(Family_Include, environ)

        assert patterns == ['api.customer.get']

    def test_variables_sort_lexicographically_by_name(self) -> 'None':

        # The dict deliberately lists the names out of order - collection must sort by name.
        environ = {
            'Zato_Auto_REST_Channel_Include_02': 'second',
            'Zato_Auto_REST_Channel_Include': 'first',
            'Zato_Auto_REST_Channel_Include_ABC': 'third',
        }
        patterns = collect_family_patterns(Family_Include, environ)

        assert patterns == ['first', 'second', 'third']

    def test_comma_and_semicolon_separators_with_spaces(self) -> 'None':

        environ = {'Zato_Auto_REST_Channel_Include': ' api.one , api.two ;api.three;  api.four  '}
        patterns = collect_family_patterns(Family_Include, environ)

        assert patterns == ['api.one', 'api.two', 'api.three', 'api.four']

    def test_empty_entries_are_dropped(self) -> 'None':

        environ = {'Zato_Auto_REST_Channel_Include': 'api.one,,;  ;api.two,'}
        patterns = collect_family_patterns(Family_Include, environ)

        assert patterns == ['api.one', 'api.two']

    def test_families_do_not_leak_into_each_other(self) -> 'None':

        environ = {
            'Zato_Auto_REST_Channel_Include': 'included',
            'Zato_Auto_REST_Channel_Exclude': 'excluded',
            'Zato_Auto_REST_Channel_Active': 'active',
            'Some_Other_Variable': 'other',
        }

        assert collect_family_patterns(Family_Include, environ) == ['included']
        assert collect_family_patterns(Family_Exclude, environ) == ['excluded']

    def test_no_variables_means_no_patterns(self) -> 'None':

        assert collect_family_patterns(Family_Include, {}) == []

# ################################################################################################################################
# ################################################################################################################################

class TestMatchesPattern:

    def test_literal_match(self) -> 'None':

        assert matches_pattern('api.customer.get', 'api.customer.get')

    def test_literal_mismatch(self) -> 'None':

        assert not matches_pattern('api.customer.get', 'api.customer.create')

    def test_placeholder_matches_one_segment(self) -> 'None':

        assert matches_pattern('api.billing.customer.get', 'api.{department}.customer.{operation}')

    def test_placeholder_never_matches_two_segments(self) -> 'None':

        # {department} may not swallow 'billing.emea' - a placeholder is exactly one segment.
        assert not matches_pattern('api.billing.emea.customer.get', 'api.{department}.customer.{operation}')

    def test_segment_counts_must_be_equal(self) -> 'None':

        assert not matches_pattern('api.customer', 'api.customer.get')
        assert not matches_pattern('api.customer.get.all', 'api.customer.get')

    def test_all_placeholders(self) -> 'None':

        assert matches_pattern('one.two.three', '{a}.{b}.{c}')

    def test_glob_stars_are_literal(self) -> 'None':

        # A star is not special - it only matches a segment that is literally a star.
        assert not matches_pattern('api.customer.get', 'api.*.get')
        assert matches_pattern('api.*.get', 'api.*.get')

    def test_matches_any(self) -> 'None':

        patterns = ['api.order.{operation}', 'api.customer.{operation}']

        assert matches_any('api.customer.get', patterns)
        assert not matches_any('api.invoice.get', patterns)
        assert not matches_any('api.customer.get', [])

# ################################################################################################################################
# ################################################################################################################################

class TestGetAutoChannelConfig:

    def test_defaults(self) -> 'None':

        config = get_auto_channel_config({})

        assert config.is_enabled is True
        assert config.url_prefix == Default_Prefix
        assert config.include == []
        assert config.exclude == []
        assert config.active == []

    def test_enabled_can_be_turned_off(self) -> 'None':

        config = get_auto_channel_config({'Zato_Auto_REST_Channel_Enabled': 'False'})
        assert config.is_enabled is False

        config = get_auto_channel_config({'Zato_Auto_REST_Channel_Enabled': '0'})
        assert config.is_enabled is False

        config = get_auto_channel_config({'Zato_Auto_REST_Channel_Enabled': 'True'})
        assert config.is_enabled is True

    def test_prefix_is_normalized_to_slashes(self) -> 'None':

        config = get_auto_channel_config({'Zato_Auto_REST_Channel_Prefix': 'rest'})
        assert config.url_prefix == '/rest/'

        config = get_auto_channel_config({'Zato_Auto_REST_Channel_Prefix': '/rest'})
        assert config.url_prefix == '/rest/'

        config = get_auto_channel_config({'Zato_Auto_REST_Channel_Prefix': 'rest/'})
        assert config.url_prefix == '/rest/'

        config = get_auto_channel_config({'Zato_Auto_REST_Channel_Prefix': '/rest/'})
        assert config.url_prefix == '/rest/'

    def test_all_families_are_collected(self) -> 'None':

        environ = {
            'Zato_Auto_REST_Channel_Include': 'api.{name}.get, api.{name}.create',
            'Zato_Auto_REST_Channel_Include_01': 'api.{name}.update',
            'Zato_Auto_REST_Channel_Exclude': 'api.internal.{operation}',
            'Zato_Auto_REST_Channel_Active': 'api.customer.{operation}',
        }
        config = get_auto_channel_config(environ)

        assert config.include == ['api.{name}.get', 'api.{name}.create', 'api.{name}.update']
        assert config.exclude == ['api.internal.{operation}']
        assert config.active == ['api.customer.{operation}']

# ################################################################################################################################
# ################################################################################################################################

class TestShouldCreateChannel:

    def test_include_match_creates(self) -> 'None':

        config = get_auto_channel_config({'Zato_Auto_REST_Channel_Include': 'api.{name}.{operation}'})
        assert should_create_channel('api.customer.get', config)

    def test_no_include_match_means_no_channel(self) -> 'None':

        config = get_auto_channel_config({'Zato_Auto_REST_Channel_Include': 'api.{name}.{operation}'})
        assert not should_create_channel('internal.customer.get', config)

    def test_no_include_patterns_at_all_means_no_channel(self) -> 'None':

        config = get_auto_channel_config({})
        assert not should_create_channel('api.customer.get', config)

    def test_exclude_wins_over_include(self) -> 'None':

        environ = {
            'Zato_Auto_REST_Channel_Include': 'api.{name}.{operation}',
            'Zato_Auto_REST_Channel_Exclude': 'api.internal.{operation}',
        }
        config = get_auto_channel_config(environ)

        assert should_create_channel('api.customer.get', config)
        assert not should_create_channel('api.internal.get', config)

    def test_disabled_feature_creates_nothing(self) -> 'None':

        environ = {
            'Zato_Auto_REST_Channel_Enabled': 'False',
            'Zato_Auto_REST_Channel_Include': 'api.{name}.{operation}',
        }
        config = get_auto_channel_config(environ)

        assert not should_create_channel('api.customer.get', config)

# ################################################################################################################################
# ################################################################################################################################

class TestIsChannelActive:

    def test_active_pattern_match(self) -> 'None':

        config = get_auto_channel_config({'Zato_Auto_REST_Channel_Active': 'api.customer.{operation}'})

        assert is_channel_active('api.customer.get', config)
        assert not is_channel_active('api.order.get', config)

    def test_no_active_patterns_means_inactive(self) -> 'None':

        # A service matching include but no active pattern gets its channel created inactive.
        config = get_auto_channel_config({'Zato_Auto_REST_Channel_Include': 'api.{name}.{operation}'})
        assert not is_channel_active('api.customer.get', config)

# ################################################################################################################################
# ################################################################################################################################

class TestGetAutoChannelUrlPath:

    def test_default_prefix(self) -> 'None':

        config = get_auto_channel_config({})
        assert get_auto_channel_url_path('api.customer.get', config) == '/api/api/customer/get'

    def test_custom_prefix(self) -> 'None':

        config = get_auto_channel_config({'Zato_Auto_REST_Channel_Prefix': '/rest/'})
        assert get_auto_channel_url_path('api.customer.get', config) == '/rest/api/customer/get'

# ################################################################################################################################
# ################################################################################################################################
