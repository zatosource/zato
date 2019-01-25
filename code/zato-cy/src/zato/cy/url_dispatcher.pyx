# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
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
from zato.common import MISC, TRACE1

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

# Redefined from zato.common so that they can be kept on C level
TRACE1 = 6
target_separator = ':::'

# ################################################################################################################################

_internal_url_path_indicator = '{}/zato/'.format(target_separator)

# ################################################################################################################################

cdef class Matcher(object):
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

    def __init__(self, pattern, match_slash=True):

        # If True, we will include slashes in pattern matching,
        # otherwise they will not be taken into account.
        slash_pattern = '\/' if match_slash else ''

        self.group_names = []
        self.pattern = pattern
        self.matcher = None
        self.is_static = True
        self._brace_pattern = re_compile('\{[\w \$.\-|=~^\/]+\}', stdlib_re.UNICODE)
        self._elem_re_template = r'(?P<{}>[\w \$.\-|=~^'+ slash_pattern +']+)'
        self._set_up_matcher(self.pattern)

# ################################################################################################################################

    def __str__(self):
        return '<{} at {} {} {}>'.format(self.__class__.__name__, hex(id(self)), self.pattern, self.matcher)

    __repr__ = __str__

# ################################################################################################################################

    cdef _set_up_matcher(self, unicode pattern):
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

    cdef match(self, unicode value):
        cdef tuple groups
        m = self.match_func(value)
        if m:
            if self.is_static:
                return {}
            else:
                groups = m.groups()
                return dict(zip(self.group_names, groups))

# ################################################################################################################################

cdef class CyURLData(object):

    cdef:
        public list channel_data
        public dict url_path_cache
        dict url_target_cache
        bint has_trace1

    def __init__(self, channel_data=None):
        self.channel_data = channel_data
        self.url_path_cache = {}
        self.url_target_cache = {}
        self.has_trace1 = logger.isEnabledFor(TRACE1)

# ################################################################################################################################

    cpdef tuple match(self, unicode url_path, unicode soap_action, bint has_soap_action,
        unicode _target_separator=target_separator, _bunchify=bunchify, _log_trace1=logger.log, _trace1=TRACE1):
        """ Attemps to match the combination of SOAPt Action and URL path against
        the list of HTTP channel targets.
        """
        cdef bint needs_user, has_target_in_cache=True
        cdef Matcher matcher
        cdef dict item
        cdef object item_bunch
        cdef unicode target
        cdef unicode target_cache_key = (url_path + soap_action) if has_soap_action else url_path

        try:
            target = self.url_target_cache[target_cache_key]
        except KeyError:
            target = '%s%s%s' % (soap_action, _target_separator, url_path)
            has_target_in_cache = False

        # Return from cache if already seen
        try:
            return {}, self.url_path_cache[target]
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

                    # Cache that target but only if it's a static URL without dynamic variables
                    if (not has_target_in_cache) and matcher.is_static:
                        self.url_target_cache[target_cache_key] = target

                    item_bunch = _bunchify(item)

                    # Cache that URL if it's a static one, i.e. does not contain dynamically computed variables
                    if matcher.is_static:
                        self.url_path_cache[target] = item_bunch

                    return match, item_bunch

            return None, None

# ################################################################################################################################

    def get_item(self, url_path, soap_action):
        match_target = '{}{}{}'.format(soap_action, target_separator, url_path)
        item = {}
        item['name'] = url_path[1:].replace('/', '.') + ('soap' if soap_action else '')
        item['match_target'] = match_target
        item['match_target_compiled'] = Matcher(item['match_target'])

        return item

    def set_up_test_data(self):

        channel_data = []

        # We always add /zato/ping
        channel_data.append(self.get_item('/zato/ping', ''))

        prefixes = ('channel', 'definition', 'http-soap', 'kvdb', 'outgoing', 'scheduler', 'security', 'server',
            'service', 'stats')
        soap_actions = ('soap', '')
        for prefix in prefixes:
            for soap_action in soap_actions:
                url_path = '/zato/{}/{}'.format(prefix, str(uuid4()).replace('-', '/'))
                channel_data.append(self.get_item(url_path, soap_action))

        self.channel_data = tuple(sorted(channel_data, key=itemgetter('name')))

# ################################################################################################################################

def run():

    url_data = CyURLData()
    url_data.set_up_test_data()

    #print(url_data.channel_data)

    iters = 100000
    start = datetime.utcnow()

    for x in xrange(iters):
        url_data.match('/zato/ping', '', False)

    print(datetime.utcnow() - start)

if __name__ == '__main__':
    run()
