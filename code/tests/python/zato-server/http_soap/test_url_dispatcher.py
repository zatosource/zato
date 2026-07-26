# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.util.url_dispatcher import build_methods_allowed_re, get_match_target, to_internal_accept
from zato.server.connection.http_soap.url_dispatcher import Matcher, PyURLData, target_separator, Url_Path_Cache_Size

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

_any_accept = to_internal_accept(HTTP_SOAP.ACCEPT.ANY)

# The methods a server allows, and the pattern it turns them into for a channel that names none
_methods_allowed = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
_methods_allowed_re = build_methods_allowed_re(_methods_allowed)

# ################################################################################################################################
# ################################################################################################################################

def _make_channel_item(
    url_path:'str',
    name:'str'='test.channel',
    method:'str'='POST',
    http_accept:'str'='',
    ) -> 'anydict':
    """ Builds the parts of a channel item the dispatcher looks at, with its match target built
    the way the server builds one.
    """
    config = {
        'url_path': url_path,
        'method': method,
        'http_accept': http_accept,
    }

    match_target = get_match_target(config, http_methods_allowed_re=_methods_allowed_re)

    out:'anydict' = {
        'name': name,
        'url_path': url_path,
        'method': method,
        'http_accept': http_accept,
        'match_target': match_target,
        'match_target_compiled': Matcher(match_target),
    }

    return out

# ################################################################################################################################

def _make_url_data(channel_data:'anylist') -> 'PyURLData':
    out = PyURLData(channel_data)
    return out

# ################################################################################################################################

def _match(url_data:'PyURLData', url_path:'str') -> 'anydict':
    match, _ = url_data.match(url_path, 'POST', _any_accept)
    return match

# ################################################################################################################################
# ################################################################################################################################

class StaticMatchTestCase(unittest.TestCase):
    """ Tests for matching and caching a static URL path.
    """

# ################################################################################################################################

    def test_static_path_matches_and_caches(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice')])

        match, channel_item = url_data.match('/api/invoice', 'POST', _any_accept)

        self.assertEqual(match, {})
        self.assertEqual(channel_item['name'], 'test.channel')
        self.assertEqual(len(url_data.url_path_cache), 1)

# ################################################################################################################################

    def test_cached_hit_returns_the_same_channel(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice')])

        _, first = url_data.match('/api/invoice', 'POST', _any_accept)
        _, second = url_data.match('/api/invoice', 'POST', _any_accept)

        self.assertIs(first, second)

# ################################################################################################################################

    def test_no_match_yields_nothing(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice')])

        match, channel_item = url_data.match('/api/nothing-here', 'POST', _any_accept)

        self.assertIsNone(match)
        self.assertIsNone(channel_item)
        self.assertEqual(len(url_data.url_path_cache), 0)

# ################################################################################################################################
# ################################################################################################################################

class DynamicMatchTestCase(unittest.TestCase):
    """ Tests for matching a path with parameters in it, which used never to be cached at all.
    """

# ################################################################################################################################

    def test_dynamic_path_yields_its_parameters(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice/{invoice_id}')])

        match = _match(url_data, '/api/invoice/INV-0001')

        self.assertEqual(match, {'invoice_id': 'INV-0001'})

# ################################################################################################################################

    def test_dynamic_path_is_cached(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice/{invoice_id}')])

        _ = _match(url_data, '/api/invoice/INV-0001')

        self.assertEqual(len(url_data.url_path_cache), 1)

# ################################################################################################################################

    def test_cached_dynamic_path_yields_the_same_parameters(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice/{invoice_id}')])

        first = _match(url_data, '/api/invoice/INV-0001')
        second = _match(url_data, '/api/invoice/INV-0001')

        self.assertEqual(first, second)

# ################################################################################################################################

    def test_each_dynamic_path_keeps_its_own_parameters(self) -> 'None':

        # Caching a dynamic path is only sound because the parameters are a function of the target,
        # which is the cache key - so two paths through the same channel must not see each other's.
        url_data = _make_url_data([_make_channel_item('/api/invoice/{invoice_id}')])

        first = _match(url_data, '/api/invoice/INV-0001')
        second = _match(url_data, '/api/invoice/INV-0002')

        self.assertEqual(first, {'invoice_id': 'INV-0001'})
        self.assertEqual(second, {'invoice_id': 'INV-0002'})

        # And the first one is still itself after the second went through.
        self.assertEqual(_match(url_data, '/api/invoice/INV-0001'), {'invoice_id': 'INV-0001'})

# ################################################################################################################################

    def test_parameters_handed_out_are_the_callers_own(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice/{invoice_id}')])

        first = _match(url_data, '/api/invoice/INV-0001')
        first['invoice_id'] = 'tampered'

        # A caller that changed its own copy did not change what the next request is told.
        second = _match(url_data, '/api/invoice/INV-0001')
        self.assertEqual(second, {'invoice_id': 'INV-0001'})

# ################################################################################################################################
# ################################################################################################################################

class CacheBoundTestCase(unittest.TestCase):
    """ Tests that the cache cannot grow without limit, which is what makes caching a client-varied
    key safe in the first place.
    """

# ################################################################################################################################

    def test_cache_stays_within_its_limit(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice/{invoice_id}')])

        for counter in range(Url_Path_Cache_Size + 100):
            _ = _match(url_data, f'/api/invoice/INV-{counter}')

        self.assertEqual(len(url_data.url_path_cache), Url_Path_Cache_Size)

# ################################################################################################################################

    def test_least_recently_used_entry_is_the_one_evicted(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice/{invoice_id}')])

        # Fill the cache, then keep the very first entry warm ..
        for counter in range(Url_Path_Cache_Size):
            _ = _match(url_data, f'/api/invoice/INV-{counter}')

        first_target = self._target('/api/invoice/INV-0')
        _ = _match(url_data, '/api/invoice/INV-0')

        # .. and push one more entry in, which has to evict something.
        _ = _match(url_data, '/api/invoice/INV-fresh')

        # The entry that was just used survived, and the one used longest ago did not.
        self.assertIn(first_target, url_data.url_path_cache)
        self.assertNotIn(self._target('/api/invoice/INV-1'), url_data.url_path_cache)

# ################################################################################################################################

    def _target(self, url_path:'str') -> 'str':
        out = f'{target_separator}POST{target_separator}{_any_accept}{target_separator}{url_path}'
        return out

# ################################################################################################################################
# ################################################################################################################################

class ConfiguredPatternTestCase(unittest.TestCase):
    """ Tests that go through the pattern a channel is really configured with, rather than
    through a target assembled by hand.
    """

# ################################################################################################################################

    def _make_url_data(self, url_path:'str', method:'str'='', http_accept:'str'='') -> 'PyURLData':
        channel_item = _make_channel_item(url_path, method=method, http_accept=http_accept)

        out = PyURLData([channel_item])
        return out

# ################################################################################################################################

    def test_the_accept_slot_stays_within_its_own_part_of_the_target(self) -> 'None':
        url_data = self._make_url_data('/api/invoice')

        match, channel_item = url_data.match('/anything:::/api/invoice', 'GET', _any_accept)

        self.assertIsNone(match)
        self.assertIsNone(channel_item)

# ################################################################################################################################

    def test_a_parameter_of_a_method_less_channel_gets_the_value_from_the_path(self) -> 'None':

        # A channel that names no method has every method a server allows standing in that slot,
        # and what goes into the parameter is the path, never the method the request came with.
        url_data = self._make_url_data('/api/{action}')

        match = _match(url_data, '/api/archive')

        self.assertEqual(match, {'action': 'archive'})

# ################################################################################################################################

    def test_a_parameter_value_that_reads_as_a_method_is_kept(self) -> 'None':
        url_data = self._make_url_data('/api/{action}')

        match = _match(url_data, '/api/POST')

        self.assertEqual(match, {'action': 'POST'})

# ################################################################################################################################

    def test_every_parameter_of_a_method_less_channel_gets_its_own_value(self) -> 'None':
        url_data = self._make_url_data('/api/{user_id}/order/{order_id}')

        match = _match(url_data, '/api/123/order/456')

        self.assertEqual(match, {'user_id': '123', 'order_id': '456'})

# ################################################################################################################################

    def test_a_parameter_value_may_carry_the_characters_a_URL_allows(self) -> 'None':
        url_data = self._make_url_data('/api/invoice/{invoice_id}')

        match = _match(url_data, '/api/invoice/a+b,c;d!e(f)@g')

        self.assertEqual(match, {'invoice_id': 'a+b,c;d!e(f)@g'})

# ################################################################################################################################

    def test_a_parameter_value_may_carry_an_encoded_slash(self) -> 'None':
        url_data = self._make_url_data('/api/invoice/{invoice_id}')

        match = _match(url_data, '/api/invoice/INV%2F0001')

        self.assertEqual(match, {'invoice_id': 'INV%2F0001'})

# ################################################################################################################################

    def test_a_path_with_regular_expression_syntax_matches_itself(self) -> 'None':
        url_data = self._make_url_data('/api/invoice.list+all')

        match, channel_item = url_data.match('/api/invoice.list+all', 'GET', _any_accept)

        self.assertEqual(match, {})
        self.assertEqual(channel_item['name'], 'test.channel')

# ################################################################################################################################

    def test_an_accept_header_with_regular_expression_syntax_matches_itself(self) -> 'None':
        url_data = self._make_url_data('/api/invoice', 'GET', 'application/vnd.api+json')

        accept = 'applicationHTTP_SEPvnd.api+json'
        match, channel_item = url_data.match('/api/invoice', 'GET', accept)

        self.assertEqual(match, {})
        self.assertEqual(channel_item['name'], 'test.channel')

# ################################################################################################################################
# ################################################################################################################################

class MissCacheTestCase(unittest.TestCase):
    """ Tests for what a request to a path no channel matched costs the second time around.
    """

# ################################################################################################################################

    def test_a_miss_is_remembered(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice')])

        _ = _match(url_data, '/api/nothing-here')

        self.assertEqual(len(url_data.url_path_miss_cache), 1)

# ################################################################################################################################

    def test_a_remembered_miss_still_matches_nothing(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice')])

        _ = _match(url_data, '/api/nothing-here')
        match, channel_item = url_data.match('/api/nothing-here', 'POST', _any_accept)

        self.assertIsNone(match)
        self.assertIsNone(channel_item)

# ################################################################################################################################

    def test_a_channel_appearing_forgets_the_misses(self) -> 'None':
        invoice = _make_channel_item('/api/invoice')
        channel_data = [invoice]
        url_data = _make_url_data(channel_data)

        _ = _match(url_data, '/api/payment')
        self.assertEqual(len(url_data.url_path_miss_cache), 1)

        # A path that missed can only start matching once a channel appears at it, which is
        # what this invalidation stands for.
        payment = _make_channel_item('/api/payment', 'payment.channel')
        channel_data.append(payment)
        url_data.rebuild_match_target_index()
        url_data._remove_from_cache(payment['match_target'])

        self.assertEqual(len(url_data.url_path_miss_cache), 0)

        _, channel_item = url_data.match('/api/payment', 'POST', _any_accept)
        self.assertEqual(channel_item['name'], 'payment.channel')

# ################################################################################################################################

    def test_miss_cache_stays_within_its_limit(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice')])

        for counter in range(Url_Path_Cache_Size + 100):
            _ = _match(url_data, f'/api/nothing-here/{counter}')

        self.assertEqual(len(url_data.url_path_miss_cache), Url_Path_Cache_Size)

# ################################################################################################################################
# ################################################################################################################################

class AllowMethodsTestCase(unittest.TestCase):
    """ Tests for what a path that channels do sit at reports when the method is not one of theirs.
    """

# ################################################################################################################################

    def test_a_path_with_another_method_reports_it(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice', method='POST')])

        match, _ = url_data.match('/api/invoice', 'DELETE', _any_accept)
        allow_methods = url_data.get_allow_methods('/api/invoice', 'DELETE', _any_accept)

        self.assertIsNone(match)
        self.assertEqual(allow_methods, {'POST'})

# ################################################################################################################################

    def test_every_method_at_that_path_is_reported(self) -> 'None':
        url_data = _make_url_data([
            _make_channel_item('/api/invoice', 'invoice.get', 'GET'),
            _make_channel_item('/api/invoice', 'invoice.post', 'POST'),
        ])

        _, _ = url_data.match('/api/invoice', 'DELETE', _any_accept)
        allow_methods = url_data.get_allow_methods('/api/invoice', 'DELETE', _any_accept)

        self.assertEqual(allow_methods, {'GET', 'POST'})

# ################################################################################################################################

    def test_a_path_no_channel_is_at_reports_no_methods(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice', method='POST')])

        _, _ = url_data.match('/api/nothing-here', 'DELETE', _any_accept)
        allow_methods = url_data.get_allow_methods('/api/nothing-here', 'DELETE', _any_accept)

        self.assertEqual(allow_methods, set())

# ################################################################################################################################

    def test_a_dynamic_path_reports_its_methods(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice/{invoice_id}', method='GET')])

        _, _ = url_data.match('/api/invoice/INV-0001', 'PATCH', _any_accept)
        allow_methods = url_data.get_allow_methods('/api/invoice/INV-0001', 'PATCH', _any_accept)

        self.assertEqual(allow_methods, {'GET'})

# ################################################################################################################################

    def test_a_channel_naming_no_method_reports_none(self) -> 'None':

        # Such a channel accepts whatever method a server allows, so a request that did not match
        # it did not match its path either - which is a 404 rather than anything about methods.
        url_data = _make_url_data([_make_channel_item('/api/invoice', method='')])

        _, _ = url_data.match('/api/nothing-here', 'DELETE', _any_accept)
        allow_methods = url_data.get_allow_methods('/api/nothing-here', 'DELETE', _any_accept)

        self.assertEqual(allow_methods, set())

# ################################################################################################################################

    def test_the_methods_are_worked_out_within_the_scan_that_missed(self) -> 'None':

        # The scan that ends in a miss is what the methods come out of, so they are already
        # remembered by the time the miss is answered - no second walk of every channel.
        url_data = _make_url_data([_make_channel_item('/api/invoice', method='POST')])

        _, _ = url_data.match('/api/invoice', 'DELETE', _any_accept)

        self.assertEqual(list(url_data.url_path_miss_cache.values()), [{'POST'}])

# ################################################################################################################################
# ################################################################################################################################

class AcceptBucketTestCase(unittest.TestCase):
    """ Tests for which Accept headers are told apart when a target is matched and cached, which is
    the ones some channel names - the caches stay keyed by the configuration rather than by the
    header a request happens to carry.
    """

# ################################################################################################################################

    def test_a_header_no_channel_names_still_matches_a_channel_taking_anything(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice')])

        _, channel_item = url_data.match('/api/invoice', 'POST', 'textHTTP_SEPplain')

        self.assertEqual(channel_item['name'], 'test.channel')

# ################################################################################################################################

    def test_headers_no_channel_names_share_one_entry(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice')])

        for counter in range(20):
            _, channel_item = url_data.match('/api/invoice', 'POST', f'textHTTP_SEPmade-up-{counter}')
            self.assertIsNotNone(channel_item)

        self.assertEqual(len(url_data.url_path_cache), 1)

# ################################################################################################################################

    def test_misses_of_headers_no_channel_names_share_one_entry(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice')])

        for counter in range(20):
            _ = url_data.match('/api/nothing-here', 'POST', f'textHTTP_SEPmade-up-{counter}')

        self.assertEqual(len(url_data.url_path_miss_cache), 1)

# ################################################################################################################################

    def test_a_header_a_channel_names_is_kept_apart(self) -> 'None':
        # The channel that names an Accept value of its own comes first, which is the order
        # sort_channel_data puts the two in.
        url_data = _make_url_data([
            _make_channel_item('/api/invoice', 'invoice.json', http_accept='application/json'),
            _make_channel_item('/api/invoice', 'invoice.any'),
        ])

        json_accept = to_internal_accept('application/json')

        _, json_channel = url_data.match('/api/invoice', 'POST', json_accept)
        _, any_channel = url_data.match('/api/invoice', 'POST', 'textHTTP_SEPplain')

        self.assertEqual(json_channel['name'], 'invoice.json')
        self.assertEqual(any_channel['name'], 'invoice.any')

        # One entry for the Accept value a channel names and one for everything else
        self.assertEqual(len(url_data.url_path_cache), 2)

# ################################################################################################################################

    def test_a_header_no_channel_names_does_not_reach_a_channel_that_names_one(self) -> 'None':
        url_data = _make_url_data([_make_channel_item('/api/invoice', http_accept='application/json')])

        _, channel_item = url_data.match('/api/invoice', 'POST', 'applicationHTTP_SEPxml')

        self.assertIsNone(channel_item)

# ################################################################################################################################

    def test_a_channel_appearing_brings_its_own_header_into_the_set(self) -> 'None':
        invoice = _make_channel_item('/api/invoice', 'invoice.any')
        channel_data = [invoice]
        url_data = _make_url_data(channel_data)

        json_accept = to_internal_accept('application/json')

        # Until the channel that names it exists, that header is one of the many that reach
        # only the channels taking anything ..
        _, channel_item = url_data.match('/api/invoice', 'POST', json_accept)
        self.assertEqual(channel_item['name'], 'invoice.any')

        # .. and once it does exist, the header is the one thing that reaches it.
        json_channel = _make_channel_item('/api/invoice', 'invoice.json', http_accept='application/json')
        channel_data.insert(0, json_channel)
        url_data.rebuild_match_target_index()
        url_data._remove_from_cache(json_channel['match_target'])

        _, channel_item = url_data.match('/api/invoice', 'POST', json_accept)
        self.assertEqual(channel_item['name'], 'invoice.json')

# ################################################################################################################################
# ################################################################################################################################

class RemoveFromCacheTestCase(unittest.TestCase):
    """ Tests for the invalidation a channel being created, edited or deleted performs.
    """

# ################################################################################################################################

    def test_entries_of_the_named_channel_are_dropped(self) -> 'None':
        invoice = _make_channel_item('/api/invoice/{invoice_id}', 'invoice.channel')
        payment = _make_channel_item('/api/payment', 'payment.channel')

        url_data = _make_url_data([invoice, payment])

        _ = _match(url_data, '/api/invoice/INV-0001')
        _ = _match(url_data, '/api/payment')

        url_data._remove_from_cache(invoice['match_target'])

        # The invoice channel's entry went and the payment channel's stayed.
        self.assertEqual(len(url_data.url_path_cache), 1)

        _, channel_item = url_data.match('/api/payment', 'POST', _any_accept)
        self.assertEqual(channel_item['name'], 'payment.channel')

# ################################################################################################################################

    def test_entries_of_a_removed_channel_are_dropped(self) -> 'None':

        # A channel being deleted is gone from channel_data by the time the cache is invalidated,
        # so there is no matcher to find and the entries are located by what they cached instead.
        invoice = _make_channel_item('/api/invoice/{invoice_id}', 'invoice.channel')
        payment = _make_channel_item('/api/payment', 'payment.channel')

        channel_data = [invoice, payment]
        url_data = _make_url_data(channel_data)

        _ = _match(url_data, '/api/invoice/INV-0001')
        _ = _match(url_data, '/api/payment')

        channel_data.remove(invoice)
        url_data._remove_from_cache(invoice['match_target'])

        self.assertEqual(len(url_data.url_path_cache), 1)

        # What is left is the payment channel's own entry.
        _, channel_item = url_data.match('/api/payment', 'POST', _any_accept)
        self.assertEqual(channel_item['name'], 'payment.channel')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
