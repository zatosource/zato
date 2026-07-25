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
from zato.common.ext.bunch import bunchify
from zato.common.api import HTTP_SOAP

http_any_internal = HTTP_SOAP.ACCEPT.ANY_INTERNAL

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

# Redefined from zato.common so that they can be kept on C level
TRACE1 = 6
target_separator = ':::'
unused_marker = 'unused'

# ################################################################################################################################

_internal_url_path_indicator = '{}/zato/'.format(target_separator)

# How many resolved match targets are kept. The cache key includes the client's own Accept header
# and, now that dynamic paths are cached too, its own path parameters - both of which a client is
# free to vary. Unbounded, that is a way to exhaust a worker's memory with nothing but valid
# requests, so the cache evicts its least recently used entry instead of growing.
Url_Path_Cache_Size = 10_000

# ################################################################################################################################
# ################################################################################################################################

class Matcher:
    """ Matches incoming URL paths in requests received against the pattern it's configured to react to.
    For instance, '/permission/user/{user_id}/group/{group_id}' gets translated and compiled to the regex
    of '/permission/user/(?P<user_id>\\w+)/group/(?P<group_id>\\w+)$' which in runtime is used for matching.
    """

    def __init__(self, pattern, match_slash=True):

        # If True, we will include slashes in pattern matching,
        # otherwise they will not be taken into account.
        slash_pattern = r'\/' if match_slash else ''

        # HTTP methods to ignore in case one is set for a particular HTTP channel
        self.ignore_http_methods = set(['CONNECT', 'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT', 'TRACE'])

        self.group_names = []
        self.pattern = pattern
        self.matcher = None
        self.is_static = True
        self._brace_pattern = re_compile(r'\{[\w \$.\-:|=~^\/]+\}', stdlib_re.UNICODE)
        self._elem_re_template = r'(?P<{}>[\w \$.\-:|=~^'+ slash_pattern +']+)'
        self._set_up_matcher(self.pattern)

# ################################################################################################################################

    def __str__(self):
        return '<{} at {} {} {}>'.format(self.__class__.__name__, hex(id(self)), self.pattern, self.matcher)

    __repr__ = __str__

# ################################################################################################################################

    def _set_up_matcher(self, pattern):

        # HTTP Accept headers may in runtime come in a variety of forms
        # including multiple key/values or their weights. In order to support it
        # we treat */* as a pattern to catch any string possible in regexps.
        pattern = pattern.replace('{}HTTP_SEP{}'.format(http_any_internal, http_any_internal), '.*')

        orig_groups = self._brace_pattern.findall(pattern)
        groups = (elem.replace('{', '').replace('}', '') for elem in orig_groups)
        groups = [[elem, self._elem_re_template.format(elem)] for elem in groups]

        for idx, (group, re) in enumerate(groups):
            pattern = pattern.replace(orig_groups[idx], re)

        self.group_names.extend([elem[0] for elem in groups])
        self.matcher = re_compile(pattern + '$', stdlib_re.UNICODE)
        self.match_func = self.matcher.match

        # No groups = URL is static and has no dynamic variables in the pattern
        self.is_static = not bool(self.group_names)

        # URL path contains /zato = this is a path to an internal service
        self.is_internal = _internal_url_path_indicator in self.pattern

    def match(self, value):
        m = self.match_func(value)
        if m:
            if self.is_static:
                return {}
            else:
                groups = m.groups()

                # Note that below we may want to skip the first group and provide only the remaining ones
                # to the dict constructor. This is because the first element may be the HTTP method matched
                # and we do not require it on output from this function,
                # e.g. it is POST in the example below:
                # :::POST:::haanyHTTP_SEPhaany:::/zato/api/invoke/zato.server.get-list
                if groups[0] in self.ignore_http_methods:
                    start_index = 1
                else:
                    start_index = 0

                out = dict(zip(self.group_names, groups[start_index:]))
                return out

# ################################################################################################################################
# ################################################################################################################################

class PyURLData:

    def __init__(self, channel_data=None):
        self.channel_data = channel_data

        # Maps a match target to the channel item it resolved to and the path parameters it yielded.
        # An OrderedDict rather than a plain dict because the cache is bounded and evicts the
        # least recently used entry - see Url_Path_Cache_Size on why it has to be bounded at all.
        self.url_path_cache = OrderedDict()

        self.has_trace1 = logger.isEnabledFor(TRACE1)

# ################################################################################################################################

    def _remove_from_cache(self, match_target):
        """ Drops every cached entry that resolved to the given channel, which is what a channel
        being created, edited or deleted invalidates.
        """
        matcher = None

        # Only the one channel whose pattern this is decides which cached targets go, so it is found
        # once rather than looked for again inside the scan over cached targets.
        for item in self.channel_data:
            if item['match_target_compiled'].pattern == match_target:
                matcher = item['match_target_compiled']
                break

        # A target being deleted no longer has a channel, so there is nothing to match against and
        # the entries that pointed at it are found by the value they cached instead.
        if matcher is None:
            self._remove_by_match_target(match_target)
            return

        targets_to_remove = []

        for target in self.url_path_cache:
            if matcher.match(target) is not None:
                targets_to_remove.append(target)

        for target in targets_to_remove:
            del self.url_path_cache[target]

# ################################################################################################################################

    def _remove_by_match_target(self, match_target):
        """ Drops the cached entries whose channel item carries the given match target.
        """
        targets_to_remove = []

        for target, entry in self.url_path_cache.items():
            if entry[1]['match_target'] == match_target:
                targets_to_remove.append(target)

        for target in targets_to_remove:
            del self.url_path_cache[target]

# ################################################################################################################################

    def _cache(self, target, match, item_bunch):
        """ Stores one resolved target, evicting the least recently used entry when the cache is full.

        The path parameters are copied on the way in, since the dict handed back to the caller of
        this very request is the one that was matched - keeping that same dict would let that caller
        reach into the cache.
        """
        self.url_path_cache[target] = (dict(match), item_bunch)

        while len(self.url_path_cache) > Url_Path_Cache_Size:
            _ = self.url_path_cache.popitem(last=False)

# ################################################################################################################################

    def match(self, url_path, http_method, http_accept, sep=target_separator, _bunchify=bunchify, _log_trace1=logger.log,
        _trace1=TRACE1):
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

        needs_user = not url_path.startswith('/zato')

        for item in self.channel_data:

            matcher = item['match_target_compiled']
            if needs_user and matcher.is_internal:
                continue

            match = matcher.match(target)

            if match is not None:
                if self.has_trace1:
                    _log_trace1(_trace1, 'Matched target:`%s` with:`%r`', target, item)

                item_bunch = _bunchify(item)

                # A dynamic path is cached along with the parameters it yielded. Those parameters
                # are a function of the target alone, and the target is the cache key, so caching
                # them is sound - and it is what stops a dynamic-path channel from paying a full
                # regex scan of every channel on every single request. What used to make this
                # unsafe was the cache being unbounded, which is no longer the case.
                self._cache(target, match, item_bunch)

                return match, item_bunch

        return None, None

# ################################################################################################################################
# ################################################################################################################################
