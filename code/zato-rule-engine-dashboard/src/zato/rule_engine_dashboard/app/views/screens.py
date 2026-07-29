# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Django
from django.shortcuts import redirect, render

# Zato
from zato.rule_engine_dashboard.app.views.common import signed_in_required

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def _screen(req:'any_', name:'str', template:'str') -> 'any_':
    """ Renders one screen, saying in the log who opened it - what the screen then loads
    arrives through its own logged endpoints.
    """
    logger.info('Opening the %s screen (%s)', name, req.user.username)

    out = render(req, template)
    return out

# ################################################################################################################################
# ################################################################################################################################

def home(req:'any_') -> 'any_':
    """ The root path leads to the rulesets home screen, which handles the sign-in gate itself.
    """
    out = redirect('rulesets')
    return out

# ################################################################################################################################

@signed_in_required
def rulesets(req:'any_') -> 'any_':
    """ The rulesets home screen.
    """
    out = _screen(req, 'rulesets', 'rulesets.html')
    return out

# ################################################################################################################################

@signed_in_required
def editor(req:'any_') -> 'any_':
    """ The sentence editor screen.
    """
    out = _screen(req, 'editor', 'editor.html')
    return out

# ################################################################################################################################

@signed_in_required
def tables(req:'any_') -> 'any_':
    """ The decision table screen.
    """
    out = _screen(req, 'decision table', 'table.html')
    return out

# ################################################################################################################################

@signed_in_required
def tests(req:'any_') -> 'any_':
    """ The tests and simulation screen.
    """
    out = _screen(req, 'tests and simulation', 'test.html')
    return out

# ################################################################################################################################

@signed_in_required
def versions(req:'any_') -> 'any_':
    """ The versions and changes screen.
    """
    out = _screen(req, 'versions and changes', 'versions.html')
    return out

# ################################################################################################################################

@signed_in_required
def decision_log(req:'any_') -> 'any_':
    """ The decision log screen.
    """
    out = _screen(req, 'decision log', 'log.html')
    return out

# ################################################################################################################################

@signed_in_required
def vocabulary(req:'any_') -> 'any_':
    """ The vocabulary screen.
    """
    out = _screen(req, 'vocabulary', 'vocabulary.html')
    return out

# ################################################################################################################################

@signed_in_required
def notifications(req:'any_') -> 'any_':
    """ The notifications screen - destinations per ruleset, chat credentials for admins.
    """
    out = _screen(req, 'notifications', 'notifications.html')
    return out

# ################################################################################################################################
# ################################################################################################################################
