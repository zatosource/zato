# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import FOUND

# Django
from django.test import Client

# Zato
from zato.rule_engine_dashboard.app.storage import get_backend, get_engine, get_manager, init_storage

# ################################################################################################################################

from rule_views_test_data import create_ruleset

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def test_storage_is_shared_and_idempotent() -> 'None':
    """ Repeated initialization keeps handing out the same engine, facade and manager.
    """
    engine = get_engine()
    backend = get_backend()
    manager = get_manager()

    init_storage()

    assert get_engine() is engine
    assert get_backend() is backend
    assert get_manager() is manager

# ################################################################################################################################

def test_tables_exist_and_accept_writes(backend:'any_') -> 'None':
    """ The rule-engine tables are created at bootstrap and accept a definition right away.
    """
    definition = create_ruleset(backend)

    assert definition.id > 0
    assert definition.current_version == 1

# ################################################################################################################################

def test_views_require_a_signed_in_user() -> 'None':
    """ An anonymous request never reaches a rule view - it goes to the sign-in screen instead.
    """
    anonymous = Client()
    response:'any_' = anonymous.get('/rules/rulesets/')

    assert response.status_code == FOUND
    assert response.url.startswith('/login/')

# ################################################################################################################################
# ################################################################################################################################
