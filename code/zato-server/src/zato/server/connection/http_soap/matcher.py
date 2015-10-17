# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime

# regex
from regex import compile as re_compile, match as re_match

class Matcher(object):
    def __init__(self, pattern):
        self._brace_pattern = re_compile('\{\w+\}')
        self._elem_re_template = r'(?P<{}>\w+)'
        self._group_names = []
        self._matcher = None
        self._set_up_matcher(pattern)
        print(self._matcher)

    def _set_up_matcher(self, pattern):
        orig_groups = self._brace_pattern.findall(pattern)
        groups = [elem.replace('{', '').replace('}', '') for elem in orig_groups]
        groups = [[elem, self._elem_re_template.format(elem)] for elem in groups]

        for idx, (group, re) in enumerate(groups):
            pattern = pattern.replace(orig_groups[idx], re)

        self._group_names.extend([elem[0] for elem in groups])
        self._matcher = re_compile(pattern + '$')

    def match(self, value):
        m = self._matcher.match(value)
        if m:
            return dict(zip(self._group_names, m.groups()))

if __name__ == '__main__':

    patterns = [
        '/customer/{cid}/order/{oid}',
        '/permission/user/{user_id}',
        '/permission/user/{user_id}/update',
        '/permission/user/{user_id}/group/{group_id}',
    ]

    m = Matcher('/permission/user/{user_id}/group/{group_id}')

    n = 100000
    req = range(n)
    start = datetime.utcnow()

    for x in req:
        result = m.match('/permission/user/123/group/456')

    taken = datetime.utcnow() - start
    print(taken)
