# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import re as stdlib_re
from datetime import datetime
from logging import getLogger
from operator import itemgetter
from uuid import uuid4

# regex
from regex import compile as re_compile

# Zato
from zato.bunch import bunchify
from zato.common.api import HTTP_SOAP, MISC, TRACE1

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

# ################################################################################################################################
# ################################################################################################################################

cdef class Matcher:
    """ Matches incoming URL paths in requests received against the pattern it's configured to react to.
    For instance, '/permission/user/{user_id}/group/{group_id}' gets translated and compiled to the regex
    of '/permission/user/(?P<user_id>\\w+)/group/(?P<group_id>\\w+)$' which in runtime is used for matching.
    """
    cdef:
        public list group_names
        public unicode pattern
        public object matcher
        object match_func
        public bint is_static, is_internal
        object _brace_pattern
        object _elem_re_template
        set ignore_http_methods

    def __init__(self, pattern, match_slash=True):

        # If True, we will include slashes in pattern matching,
        # otherwise they will not be taken into account.
        slash_pattern = '\/' if match_slash else ''

        # HTTP methods to ignore in case one is set for a particular HTTP channel
        self.ignore_http_methods = set(['CONNECT', 'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT', 'TRACE'])

        self.group_names = []
        self.pattern = pattern
        self.matcher = None
        self.is_static = True
        self._brace_pattern = re_compile('\{[\w \$.\-:|=~^\/]+\}', stdlib_re.UNICODE)
        self._elem_re_template = r'(?P<{}>[\w \$.\-:|=~^'+ slash_pattern +']+)'
        self._set_up_matcher(self.pattern)

# ################################################################################################################################

    def __str__(self):
        return '<{} at {} {} {}>'.format(self.__class__.__name__, hex(id(self)), self.pattern, self.matcher)

    __repr__ = __str__

# ################################################################################################################################

    cdef _set_up_matcher(self, unicode pattern):

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

    cpdef match(self, unicode value):
        cdef tuple groups
        cdef int start_index
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

                return dict(zip(self.group_names, groups[start_index:]))

# ################################################################################################################################
# ################################################################################################################################

cdef class CyURLData:

    cdef:
        public list channel_data
        public dict url_path_cache
        bint has_trace1

    def __init__(self, channel_data=None):
        self.channel_data = channel_data
        self.url_path_cache = {}
        self.url_target_cache = {}
        self.has_trace1 = logger.isEnabledFor(TRACE1)

# ################################################################################################################################

    cpdef _remove_from_cache(self, unicode match_target):

        targets_to_remove = []
        cached_targets = self.url_path_cache.keys()

        for target in cached_targets:
            for item in self.channel_data:
                matcher = item['match_target_compiled']
                if matcher.pattern == match_target:
                    if matcher.match(target) is not None:
                        targets_to_remove.append(target)

        for target in targets_to_remove:
            del self.url_path_cache[target]

# ################################################################################################################################

    cpdef tuple match(self, unicode url_path, unicode http_method, unicode http_accept,
        unicode sep=target_separator, _bunchify=bunchify, _log_trace1=logger.log,
        _trace1=TRACE1):
        """ Attemps to match the combination of SOAPt Action and URL path against
        the list of HTTP channel targets.
        """
        cdef bint needs_user, has_target_in_cache=True
        cdef Matcher matcher
        cdef dict item
        cdef object item_bunch

        cdef unicode target = ''
        target += '' # This used to be a SOAP action, now it is always an empty string
        target += sep
        target += http_method
        target += sep
        target += http_accept
        target += sep
        target += url_path

        try:
            self.url_target_cache[target]
        except KeyError:
            has_target_in_cache = False

        # Return from cache if already seen
        try:
            ctx, channel_item = {}, self.url_path_cache[target]
            return ctx, channel_item
        except KeyError:
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

                    # Cache that target but only if it's a static URL without dynamic variables
                    if (not has_target_in_cache) and matcher.is_static:
                        self.url_path_cache[target] = item_bunch

                    return match, item_bunch

            return None, None

# ################################################################################################################################
# ################################################################################################################################
