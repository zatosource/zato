# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from traceback import format_exc
from typing import NamedTuple

# pytest
import pytest

# Live containers
from live_containers.docker import has_docker

# Live environment
from live_environment.haproxy import is_haproxy_available

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_, strlist, strtuple

# ################################################################################################################################
# ################################################################################################################################

class Part(NamedTuple):
    """ One thing a suite started and what ends it.
    """
    what: 'str'
    stop: 'callable_'

# ################################################################################################################################

part_list = list[Part]

# ################################################################################################################################
# ################################################################################################################################

class Parts:
    """ Everything a suite has started so far, in the order it started, so that a failure half-way through
    a setup leaves nothing behind and a teardown ends things in the reverse of the order they came up in.
    """

    def __init__(self) -> 'None':
        self.started:'part_list' = []

# ################################################################################################################################

    def add(self, what:'str', stop:'callable_') -> 'None':
        """ Registers one started thing along with the call that ends it.
        """
        part = Part(what, stop)
        self.started.append(part)

# ################################################################################################################################
# ################################################################################################################################

def tear_down(parts:'Parts') -> 'None':
    """ Ends everything that started, last one first. One part that will not stop does not keep the
    others running - what it printed is in the output and the rest are ended all the same.
    """
    for part in reversed(parts.started):

        try:
            part.stop()
        except Exception:
            print(f'[TEARDOWN] Could not stop {part.what}; e:`{format_exc()}`')

    parts.started.clear()

# ################################################################################################################################
# ################################################################################################################################

def missing_requirements(*, wants_docker:'bool', wants_haproxy:'bool', variables:'strtuple'=()) -> 'strlist':
    """ What this machine lacks for a live suite to come up - empty when nothing is missing. The variables
    are the names of the ones that have to be set, each reported by name when it is not.
    """
    out:'strlist' = []

    if wants_docker:
        if not has_docker():
            out.append('Docker compose is not available, so no live system can be started')

    if wants_haproxy:
        if not is_haproxy_available():
            out.append('HAProxy is not installed, so nothing can front the MLLP listener')

    for variable in variables:
        if not os.environ.get(variable):
            out.append(f'{variable} is not set')

    return out

# ################################################################################################################################

def skip_or_fail(missing:'strlist', required_variable:'str') -> 'None':
    """ A machine without what the suite needs skips, unless the run was asked for outright by setting
    the suite's own variable to 1, in which case a missing piece is a failure.
    """
    if not missing:
        return

    message = ', '.join(missing)
    is_required = os.environ.get(required_variable) == '1'

    if is_required:
        raise Exception(message)

    pytest.skip(message)

# ################################################################################################################################
# ################################################################################################################################
