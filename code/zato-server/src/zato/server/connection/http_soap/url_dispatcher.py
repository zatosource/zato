# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import re as stdlib_re
from collections import OrderedDict
from logging import getLogger

# regex
from regex import compile as re_compile

# Zato
from zato.common.api import HTTP_SOAP

http_any_internal = HTTP_SOAP.ACCEPT.ANY_INTERNAL

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, callable_, strlist, strset, tuple_
    any_ = any_
    anydict = anydict
    anylist = anylist
    callable_ = callable_
    strlist = strlist
    strset = strset
    tuple_ = tuple_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

# Redefined from zato.common so that they can be kept on C level
TRACE1 = 6
target_separator = ':::'

# ################################################################################################################################

_internal_url_path_indicator = '{}/zato/'.format(target_separator)

# How many resolved match targets are kept. The cache key includes the client's own Accept header
# and, now that dynamic paths are cached too, its own path parameters - both of which a client is
# free to vary. Unbounded, that is a way to exhaust a worker's memory with nothing but valid
# requests, so the cache evicts its least recently used entry instead of growing.
Url_Path_Cache_Size = 10_000

# What a path parameter's value is built of, apart from the slash, which match_slash decides on.
_path_param_chars = r'\w \$.\-:|=~^%@+,;!()'

# Whether a path parameter matches a value spanning several path segments, for a channel
# whose configuration does not say either way.
Match_Slash_Default = True

# The Accept slot of a match target, for a channel that accepts anything. Anchored to
# everything but the separator, so the slot stays within its own part of the target.
_accept_any_pattern = '[^:]*'

# ################################################################################################################################

def resolve_match_slash(value:'any_') -> 'bool':
    """ Returns whether path parameters match across slashes for a channel whose configuration
    carries the given value, which a channel configured before the option existed does not carry.
    """
    if value is None:
        return Match_Slash_Default

    if value == '':
        return Match_Slash_Default

    out = bool(value)
    return out

# ################################################################################################################################
# ################################################################################################################################

class Matcher:
    """ Matches incoming URL paths in requests received against the pattern it's configured to react to.
    For instance, '/permission/user/{user_id}/group/{group_id}' gets translated and compiled to the regex
    of '/permission/user/(?P<user_id>\\w+)/group/(?P<group_id>\\w+)$' which in runtime is used for matching.
    """

    def __init__(self, pattern:'str', match_slash:'bool'=Match_Slash_Default) -> 'None':

        # If True, we will include slashes in pattern matching,
        # otherwise they will not be taken into account.
        slash_pattern = r'\/' if match_slash else ''

        self.group_names:'strlist' = []
        self.pattern = pattern
        self.matcher = None
        self.is_static = True
        self._brace_pattern = re_compile(r'\{[\w \$.\-:|=~^\/]+\}', stdlib_re.UNICODE)
        self._elem_re_template = r'(?P<{}>[' + _path_param_chars + slash_pattern + ']+)'
        self._set_up_matcher(self.pattern)

# ################################################################################################################################

    def __str__(self) -> 'str':
        return '<{} at {} {} {}>'.format(self.__class__.__name__, hex(id(self)), self.pattern, self.matcher)

    __repr__ = __str__

# ################################################################################################################################

    def _set_up_matcher(self, pattern:'str') -> 'None':

        # HTTP Accept headers may in runtime come in a variety of forms
        # including multiple key/values or their weights. In order to support it
        # we treat */* as a pattern to catch any string possible in this one slot.
        pattern = pattern.replace('{}HTTP_SEP{}'.format(http_any_internal, http_any_internal), _accept_any_pattern)

        orig_groups = self._brace_pattern.findall(pattern)
        groups = (elem.replace('{', '').replace('}', '') for elem in orig_groups)
        groups = [[elem, self._elem_re_template.format(elem)] for elem in groups]

        for idx, (_, re) in enumerate(groups):
            pattern = pattern.replace(orig_groups[idx], re)

        self.group_names.extend([elem[0] for elem in groups])
        self.matcher = re_compile(pattern + '$', stdlib_re.UNICODE)
        self.match_func = self.matcher.match

        # No groups = URL is static and has no dynamic variables in the pattern
        self.is_static = not bool(self.group_names)

        # URL path contains /zato = this is a path to an internal service
        self.is_internal = _internal_url_path_indicator in self.pattern

    def match(self, value:'str') -> 'anydict | None':
        m = self.match_func(value)
        if m:
            if self.is_static:
                return {}
            else:

                # The method slot is a non-capturing group and so is the Accept one, which leaves
                # the path parameters as the only groups there are, in the order they were declared.
                groups = m.groups()

                out = dict(zip(self.group_names, groups))
                return out

# ################################################################################################################################
# ################################################################################################################################

class PyURLData:

    def __init__(self, channel_data:'anylist') -> 'None':
        self.channel_data = channel_data

        # Maps a match target to the channel item it resolved to and the path parameters it yielded.
        # An OrderedDict rather than a plain dict because the cache is bounded and evicts the
        # least recently used entry - see Url_Path_Cache_Size on why it has to be bounded at all.
        self.url_path_cache = OrderedDict()

        # Maps a match target that resolved to no channel at all to the methods its path does accept.
        # Bounded and evicted the same way the cache above is, and for the same reason.
        self.url_path_miss_cache = OrderedDict()

        # Maps a channel's match target to its channel item, so that a channel being created,
        # edited or deleted is found in one lookup rather than in a scan of every channel there is.
        self.match_target_index = {}
        self.rebuild_match_target_index()

        self.has_trace1 = logger.isEnabledFor(TRACE1)

# ################################################################################################################################

    def rebuild_match_target_index(self) -> 'None':
        """ Rebuilds the match-target index from the channel data it indexes.
        """
        index = {}

        for item in self.channel_data:
            index[item['match_target']] = item

        self.match_target_index = index

# ################################################################################################################################

    def _remove_from_cache(self, match_target:'str') -> 'None':
        """ Drops every cached entry that resolved to the given channel, which is what a channel
        being created, edited or deleted invalidates.
        """

        # A channel appearing, changing its path or going away changes which paths match nothing
        # and which methods the remaining ones accept, and a miss belongs to no channel that its
        # entry could be correlated with, so all of them go at once.
        self.url_path_miss_cache.clear()

        # Only the one channel whose pattern this is decides which cached targets go.
        item = self.match_target_index.get(match_target)

        # A target being deleted no longer has a channel, so there is nothing to match against and
        # the entries that pointed at it are found by the value they cached instead.
        if item is None:
            self._remove_by_match_target(match_target)
            return

        matcher = item['match_target_compiled']
        targets_to_remove = []

        for target in self.url_path_cache:
            if matcher.match(target) is not None:
                targets_to_remove.append(target)

        for target in targets_to_remove:
            del self.url_path_cache[target]

# ################################################################################################################################

    def _remove_by_match_target(self, match_target:'str') -> 'None':
        """ Drops the cached entries whose channel item carries the given match target.
        """
        targets_to_remove = []

        for target, entry in self.url_path_cache.items():
            if entry[1]['match_target'] == match_target:
                targets_to_remove.append(target)

        for target in targets_to_remove:
            del self.url_path_cache[target]

# ################################################################################################################################

    def _cache(self, target:'str', match:'anydict', channel_item:'anydict') -> 'None':
        """ Stores one resolved target, evicting the least recently used entry when the cache is full.

        The path parameters are copied on the way in, since the dict handed back to the caller of
        this very request is the one that was matched - keeping that same dict would let that caller
        reach into the cache.
        """
        self.url_path_cache[target] = (dict(match), channel_item)

        while len(self.url_path_cache) > Url_Path_Cache_Size:
            _ = self.url_path_cache.popitem(last=False)

# ################################################################################################################################

    def _cache_miss(self, target:'str', allow_methods:'strset') -> 'None':
        """ Stores one target that resolved to no channel, evicting the least recently used entry
        when the set is full.
        """
        self.url_path_miss_cache[target] = allow_methods

        while len(self.url_path_miss_cache) > Url_Path_Cache_Size:
            _ = self.url_path_miss_cache.popitem(last=False)

# ################################################################################################################################

    def _get_allow_methods(self, url_path:'str', http_accept:'str', sep:'str'=target_separator) -> 'strset':
        """ Returns the methods accepted at the given path by the channels that declare one,
        which is what tells a path no channel is at from one reached with another method.
        """
        out:'strset' = set()

        needs_user = not url_path.startswith('/zato')

        for item in self.channel_data:

            matcher = item['match_target_compiled']
            if needs_user and matcher.is_internal:
                continue

            # A channel that accepts every method has nothing to say here - the request would
            # have matched the channel itself had its path matched at all.
            method = item['method']
            if not method:
                continue

            target = f'{sep}{method}{sep}{http_accept}{sep}{url_path}'

            if matcher.match_func(target) is not None:
                out.add(method)

        return out

# ################################################################################################################################

    def get_allow_methods(self, url_path:'str', http_method:'str', http_accept:'str', sep:'str'=target_separator) -> 'strset':
        """ Returns the methods accepted at the given path, for a request that matched no channel.
        """
        target = f'{sep}{http_method}{sep}{http_accept}{sep}{url_path}'

        out = self.url_path_miss_cache.get(target)

        # The entry is there because the match ran first, unless a configuration change
        # cleared the whole set in between the two.
        if out is None:
            out = self._get_allow_methods(url_path, http_accept)

        return out

# ################################################################################################################################

    def match(
        self,
        url_path:'str',
        http_method:'str',
        http_accept:'str',
        sep:'str' = target_separator,
        _log_trace1:'callable_' = logger.log,
        _trace1:'int' = TRACE1,
        ) -> 'tuple_[anydict | None, anydict | None]':
        """ Attemps to match the combination of HTTP method, Accept header and URL path
        against the list of HTTP channel targets. The leading separator is where a SOAP action
        used to go - channels no longer match on one, so the field stays empty.
        """
        target = f'{sep}{http_method}{sep}{http_accept}{sep}{url_path}'

        # Return from cache if already seen
        entry = self.url_path_cache.get(target)

        if entry is not None:

            # The entry just used is the one to keep longest.
            self.url_path_cache.move_to_end(target)

            match, channel_item = entry

            # The path parameters are handed out as a copy - the caller receives them as its own
            # dict and a caller that changed one would otherwise change what every later request
            # for the same path is told.
            return dict(match), channel_item

        # A target already known to match nothing does not go through the scan again either.
        if target in self.url_path_miss_cache:
            self.url_path_miss_cache.move_to_end(target)
            return None, None

        needs_user = not url_path.startswith('/zato')

        for item in self.channel_data:

            matcher = item['match_target_compiled']
            if needs_user and matcher.is_internal:
                continue

            match = matcher.match(target)

            if match is not None:
                if self.has_trace1:
                    _log_trace1(_trace1, 'Matched target:`%s` with:`%r`', target, item)

                # A dynamic path is cached along with the parameters it yielded. Those parameters
                # are a function of the target alone, and the target is the cache key, so caching
                # them is sound - and it is what stops a dynamic-path channel from paying a full
                # regex scan of every channel on every single request. What used to make this
                # unsafe was the cache being unbounded, which is no longer the case.
                self._cache(target, match, item)

                return match, item

        # Nothing matched, so the methods this path does accept are worked out once and kept
        # along with the miss, which is what the next request for the same target is answered from.
        allow_methods = self._get_allow_methods(url_path, http_accept)
        self._cache_miss(target, allow_methods)

        return None, None

# ################################################################################################################################
# ################################################################################################################################
