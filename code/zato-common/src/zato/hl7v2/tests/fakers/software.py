# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7v2.tests.fakers.base import fake

# ################################################################################################################################
# ################################################################################################################################

def fake_sft() -> 'str':
    """ Returns a fake SFT (software) segment.
    """

    # Random details of the software that produced the message ..
    vendor    = fake.company().upper()
    version   = fake.numerify('#.#.#')
    product   = fake.catch_phrase().upper()
    binary_id = fake.numerify('######')

    # .. and now we can build the whole segment.
    out = f'SFT|{vendor}|{version}|{product}|{binary_id}\r'

    return out

# ################################################################################################################################
# ################################################################################################################################
