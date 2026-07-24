# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.rule_engine.invocation import unmatched_ruleset_patterns

# ################################################################################################################################
# ################################################################################################################################

def test_unmatched_ruleset_patterns_support_exact_prefix_and_global_grants() -> 'None':
    """ Exact, subtree and global grants are checked against the sorted published catalog.
    """
    published_names = [
        'customer.credit',
        'payments.discounts',
        'payments.refunds',
    ]
    patterns = [
        'customer.credit',
        'payments.*',
        '*',
        'shipping.*',
        'treasury.limits',
    ]

    out = unmatched_ruleset_patterns(patterns, published_names)

    assert out == [
        'shipping.*',
        'treasury.limits',
    ]

# ################################################################################################################################

def test_every_grant_is_unmatched_when_nothing_is_published() -> 'None':
    """ An empty published catalog leaves exact, subtree and global grants unmatched.
    """
    patterns = [
        'customer.credit',
        'payments.*',
        '*',
    ]

    out = unmatched_ruleset_patterns(patterns, [])

    assert out == patterns

# ################################################################################################################################
# ################################################################################################################################
