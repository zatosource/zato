# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.contrib.staticfiles.views import serve as serve_static_file
from django.shortcuts import redirect, render

# Zato
from zato.rule_engine_dashboard.app.views.common import signed_in_required

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def home(req:'any_') -> 'any_':
    """ The root path leads to the rulesets home screen, which handles the sign-in gate itself.
    """
    out = redirect('rulesets')
    return out

# ################################################################################################################################

def static_file(req:'any_', path:'str') -> 'any_':
    """ The application serves its own static files - it runs without a separate web server in front of it,
    so the staticfiles finders answer directly, which is what insecure=True means here.
    """
    out = serve_static_file(req, path, insecure=True)
    return out

# ################################################################################################################################

@signed_in_required
def rulesets(req:'any_') -> 'any_':
    """ The rulesets home screen.
    """
    out = render(req, 'rulesets.html')
    return out

# ################################################################################################################################

@signed_in_required
def editor(req:'any_') -> 'any_':
    """ The sentence editor screen.
    """
    out = render(req, 'editor.html')
    return out

# ################################################################################################################################

@signed_in_required
def tables(req:'any_') -> 'any_':
    """ The decision table screen.
    """
    out = render(req, 'table.html')
    return out

# ################################################################################################################################

@signed_in_required
def tests(req:'any_') -> 'any_':
    """ The tests and simulation screen.
    """
    out = render(req, 'test.html')
    return out

# ################################################################################################################################

@signed_in_required
def versions(req:'any_') -> 'any_':
    """ The versions and changes screen.
    """
    out = render(req, 'versions.html')
    return out

# ################################################################################################################################

@signed_in_required
def decision_log(req:'any_') -> 'any_':
    """ The decision log screen.
    """
    out = render(req, 'log.html')
    return out

# ################################################################################################################################

@signed_in_required
def vocabulary(req:'any_') -> 'any_':
    """ The vocabulary screen.
    """
    out = render(req, 'vocabulary.html')
    return out

# ################################################################################################################################

@signed_in_required
def notifications(req:'any_') -> 'any_':
    """ The notifications screen - destinations per ruleset, chat credentials for admins.
    """
    out = render(req, 'notifications.html')
    return out

# ################################################################################################################################
# ################################################################################################################################
