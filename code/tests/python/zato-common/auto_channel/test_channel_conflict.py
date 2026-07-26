# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.util.channel import channel_security_key, channel_specificity, find_channel_conflict, url_paths_overlap

# ################################################################################################################################
# ################################################################################################################################

_secured = channel_security_key(101, None)
_secured_elsewhere = channel_security_key(202, None)
_unsecured = channel_security_key(None, None)
_group_secured = channel_security_key(None, [11])

# ################################################################################################################################
# ################################################################################################################################

def make_item(
    name:'str',
    url_path:'str',
    security:'tuple',
    method:'str'='',
    http_accept:'str'='',
    match_slash:'bool'=True,
    item_id:'int'=1,
    ) -> 'dict':

    out = {
        'id': item_id,
        'name': name,
        'url_path': url_path,
        'method': method,
        'http_accept': http_accept,
        'match_slash': match_slash,
        'security': security,
    }

    return out

# ################################################################################################################################

def find(
    url_path:'str',
    security:'tuple',
    existing:'list',
    method:'str'='',
    http_accept:'str'='',
    match_slash:'bool'=True,
    skip_id:'int | None'=None,
    ) -> 'str | None':

    out = find_channel_conflict(url_path, http_accept, method, match_slash, security, existing, skip_id)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestURLPathsOverlap:
    """ Whether some one path a caller may send is matched by both of two channels.
    """

    def test_the_same_path_overlaps_itself(self) -> 'None':
        assert url_paths_overlap('/api/invoice', '/api/invoice', True, True)

    def test_two_literal_paths_do_not_overlap(self) -> 'None':
        assert not url_paths_overlap('/api/invoice', '/api/payment', True, True)

    def test_a_parameter_overlaps_a_literal_segment(self) -> 'None':
        assert url_paths_overlap('/api/{id}', '/api/admin', True, True)

    def test_a_parameter_matching_across_slashes_overlaps_a_deeper_path(self) -> 'None':
        assert url_paths_overlap('/api/{id}', '/api/admin/keys', True, True)

    def test_a_parameter_kept_within_one_segment_does_not_reach_a_deeper_path(self) -> 'None':
        assert not url_paths_overlap('/api/{id}', '/api/admin/keys', False, False)

    def test_two_parameters_of_different_names_overlap(self) -> 'None':
        assert url_paths_overlap('/api/{id}', '/api/{other_id}', True, True)

    def test_paths_that_differ_after_a_parameter_do_not_overlap(self) -> 'None':
        assert not url_paths_overlap('/api/{id}/history', '/api/{id}/status', True, True)

    def test_a_parameter_does_not_overlap_a_path_of_a_different_shape(self) -> 'None':
        assert not url_paths_overlap('/api/{id}', '/other/{id}', True, True)

    def test_a_parameter_takes_in_no_empty_segment(self) -> 'None':
        assert not url_paths_overlap('/api/{id}/history', '/api/history', True, True)

    def test_a_trailing_parameter_overlaps_a_run_of_segments(self) -> 'None':
        assert url_paths_overlap('/api/{path}', '/api/a/b/c', True, True)

# ################################################################################################################################
# ################################################################################################################################

class TestChannelSpecificity:
    """ How far a channel narrows the requests that reach it down, which is what orders two of them.
    """

    def test_a_literal_path_is_narrower_than_a_parameter(self) -> 'None':
        assert channel_specificity('/api/admin', '', '') < channel_specificity('/api/{id}', '', '')

    def test_a_longer_path_is_narrower_after_one_literal_prefix(self) -> 'None':
        assert channel_specificity('/api/{id}/history', '', '') < channel_specificity('/api/{id}', '', '')

    def test_naming_an_accept_value_is_narrower(self) -> 'None':
        assert channel_specificity('/api/{id}', 'application/json', '') < channel_specificity('/api/{id}', '', '')

    def test_naming_a_method_is_narrower(self) -> 'None':
        assert channel_specificity('/api/{id}', '', 'GET') < channel_specificity('/api/{id}', '', '')

    def test_two_paths_of_one_shape_are_of_one_specificity(self) -> 'None':
        assert channel_specificity('/api/{id}', '', '') == channel_specificity('/api/{xx}', '', '')

# ################################################################################################################################
# ################################################################################################################################

class TestFindChannelConflict:
    """ A candidate that one request could reach in place of a channel already there.
    """

    def test_one_path_shape_with_different_security_is_refused(self) -> 'None':

        # Nothing but their names tells these two apart, and a name is no way to settle which
        # of them secures a request.
        existing = [make_item('channel.1', '/api/{id}', _secured)]
        assert find('/api/{other_id}', _unsecured, existing) == 'channel.1'

    def test_one_path_shape_with_the_same_security_is_allowed(self) -> 'None':

        existing = [make_item('channel.1', '/api/{id}', _secured)]
        assert find('/api/{other_id}', _secured, existing) is None

    def test_another_security_definition_is_different_security(self) -> 'None':

        existing = [make_item('channel.1', '/api/{id}', _secured)]
        assert find('/api/{other_id}', _secured_elsewhere, existing) == 'channel.1'

    def test_a_group_is_security_of_its_own(self) -> 'None':

        # A channel protected by a group alone carries no definition id, and neither does an
        # unprotected one - what tells them apart is the group.
        existing = [make_item('channel.1', '/api/{id}', _group_secured)]
        assert find('/api/{other_id}', _unsecured, existing) == 'channel.1'

    def test_the_same_group_is_the_same_security(self) -> 'None':

        existing = [make_item('channel.1', '/api/{id}', _group_secured)]
        assert find('/api/{other_id}', channel_security_key(None, [11]), existing) is None

    def test_a_narrower_channel_is_allowed(self) -> 'None':

        # The narrower one answers the requests it matches, so the order of the two is settled
        existing = [make_item('channel.1', '/api/{id}', _unsecured)]
        assert find('/api/admin/keys', _secured, existing) is None

    def test_a_broader_channel_is_allowed(self) -> 'None':

        existing = [make_item('channel.1', '/api/admin/keys', _secured)]
        assert find('/api/{id}', _unsecured, existing) is None

    def test_paths_that_no_request_reaches_both_of_are_allowed(self) -> 'None':

        existing = [make_item('channel.1', '/api/{id}/history', _secured)]
        assert find('/api/{id}/status', _unsecured, existing) is None

    def test_another_method_at_one_path_is_allowed(self) -> 'None':

        # A method of its own is what keeps each of these two to its own requests
        existing = [make_item('channel.1', '/api/{id}', _secured, method='GET')]
        assert find('/api/{other_id}', _unsecured, existing, method='POST') is None

    def test_the_same_method_at_one_path_shape_is_refused(self) -> 'None':

        existing = [make_item('channel.1', '/api/{id}', _secured, method='GET')]
        assert find('/api/{other_id}', _unsecured, existing, method='GET') == 'channel.1'

    def test_another_accept_value_at_one_path_is_allowed(self) -> 'None':

        existing = [make_item('channel.1', '/api/{id}', _secured, http_accept='application/json')]
        assert find('/api/{other_id}', _unsecured, existing, http_accept='application/xml') is None

    def test_a_channel_taking_any_method_is_allowed_next_to_one_that_names_one(self) -> 'None':

        # The channel naming a method is the narrower of the two, so it answers its own requests
        existing = [make_item('channel.1', '/api/{id}', _secured, method='GET')]
        assert find('/api/{other_id}', _unsecured, existing) is None

    def test_an_edit_does_not_conflict_with_the_channel_it_edits(self) -> 'None':

        existing = [make_item('channel.1', '/api/{id}', _secured, item_id=7)]
        assert find('/api/{id}', _unsecured, existing, skip_id=7) is None

    def test_the_channel_a_request_reaches_is_the_one_reported(self) -> 'None':

        existing = [
            make_item('channel.1', '/api/payment', _secured, item_id=1),
            make_item('channel.2', '/api/{id}', _secured, item_id=2),
        ]

        assert find('/api/{other_id}', _unsecured, existing) == 'channel.2'

    def test_a_path_kept_within_one_segment_is_allowed_next_to_a_deeper_one(self) -> 'None':

        existing = [make_item('channel.1', '/api/admin/keys', _secured, match_slash=False)]
        assert find('/api/{id}', _unsecured, existing, match_slash=False) is None

# ################################################################################################################################
# ################################################################################################################################
