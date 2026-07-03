# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7v2.tests.fakers.base import fake

# ################################################################################################################################
# ################################################################################################################################

def fake_bpo() -> 'str':
    """ Returns a fake BPO (blood product order) segment.
    """

    # Random details of the blood product ..
    product_code = fake.numerify('#####')
    product_type = fake.random_element(['PRBC', 'PLT', 'FFP', 'CRYO'])

    # .. and now we can build the whole segment.
    out = f'BPO|1|{product_code}^{product_type}\r'

    return out

# ################################################################################################################################
# ################################################################################################################################
