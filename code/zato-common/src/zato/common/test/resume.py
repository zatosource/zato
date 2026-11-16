# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The hooks through which a run of an active-standby suite with the --sw option resumes from the test
# that failed or was interrupted, including a test interrupted during its setup or teardown.

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pytest import Item
    from zato.common.typing_ import any_, strnone

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Stepwise_Plugin = 'stepwiseplugin'

# ################################################################################################################################
# ################################################################################################################################

def _set_resume_point(item:'Item', nodeid:'strnone') -> 'None':
    """ Records the test that the next run of the suite starts from, or no test once the suite completes.
    """
    stepwise = item.config.pluginmanager.get_plugin(ModuleCtx.Stepwise_Plugin)

    # Stepwise is enabled only by the --sw option, without which every run starts from the beginning ..
    if stepwise is None:
        return

    # .. and the point is persisted immediately, because an interrupted run may not reach the end of its session.
    stepwise.cached_info.last_failed = nodeid
    stepwise.pytest_sessionfinish()

# ################################################################################################################################

@pytest.hookimpl(wrapper=True)
def pytest_runtest_protocol(item:'Item', nextitem:'Item | None') -> 'any_':
    """ Resumes from the test until it completes, including its teardown, and from the next test afterwards.
    """
    _set_resume_point(item, item.nodeid)

    out = yield

    # A test that failed remains the resume point, as recorded by stepwise ..
    if item.session.testsfailed:
        return out

    # .. otherwise the run resumes from the next test, or from the beginning once the suite completes.
    if nextitem is None:
        _set_resume_point(item, None)
    else:
        _set_resume_point(item, nextitem.nodeid)

    return out

# ################################################################################################################################

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_teardown(item:'Item') -> 'None':
    """ Keeps the test as the resume point during its teardown, since stepwise discards it once the test body passes.
    """
    if not item.session.testsfailed:
        _set_resume_point(item, item.nodeid)

# ################################################################################################################################
# ################################################################################################################################
