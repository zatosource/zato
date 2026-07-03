# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7v2.tests.fakers.base import fake

# ################################################################################################################################
# ################################################################################################################################

def fake_pth() -> 'str':
    """ Returns a fake PTH (pathway) segment.
    """

    # Random details of the pathway ..
    pathway_code = fake.numerify('#####')
    pathway_name = fake.random_element(['DIABETES', 'CHF', 'COPD', 'HTN'])

    # .. and now we can build the whole segment.
    out = f'PTH|AD|{pathway_code}^{pathway_name}\r'

    return out

# ################################################################################################################################

def fake_prb() -> 'str':
    """ Returns a fake PRB (problem detail) segment.
    """

    # Random details of the problem ..
    problem_timestamp = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')
    problem_code      = fake.numerify('#####')
    problem_name      = fake.random_element(['DIABETES', 'HTN', 'CHF'])

    # .. and now we can build the whole segment.
    out = f'PRB|AD|{problem_timestamp}|{problem_code}^{problem_name}\r'

    return out

# ################################################################################################################################

def fake_gol() -> 'str':
    """ Returns a fake GOL (goal detail) segment.
    """

    # Random details of the goal ..
    goal_timestamp = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')
    goal_code      = fake.numerify('#####')
    goal_name      = fake.random_element(['WEIGHT LOSS', 'BP CONTROL', 'GLUCOSE CONTROL'])

    # .. and now we can build the whole segment.
    out = f'GOL|AD|{goal_timestamp}|{goal_code}^{goal_name}\r'

    return out

# ################################################################################################################################

def fake_rf1() -> 'str':
    """ Returns a fake RF1 (referral information) segment.
    """

    # Random details of the referral ..
    status        = fake.random_element(['P', 'A', 'R'])
    priority      = fake.random_element(['R', 'S', 'I'])
    referral_type = fake.random_element(['RP', 'RF', 'AM'])

    # .. and now we can build the whole segment.
    out = f'RF1|{status}|{priority}|{referral_type}\r'

    return out

# ################################################################################################################################
# ################################################################################################################################
