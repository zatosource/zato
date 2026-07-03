# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7v2.tests.fakers.base import fake

# ################################################################################################################################
# ################################################################################################################################

def fake_mfi(identifier:'str'='CDM') -> 'str':
    """ Returns a fake MFI (master file identification) segment for the given master file identifier.
    """

    # Random timestamps for the master file exchange ..
    effective_timestamp = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')
    response_timestamp  = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')

    # .. and now we can build the whole segment.
    out = (
        f'MFI|{identifier}|APP|UPD|'
        f'{effective_timestamp}|'
        f'{response_timestamp}|NE\r'
    )

    return out

# ################################################################################################################################

def fake_mfe() -> 'str':
    """ Returns a fake MFE (master file entry) segment.
    """

    # Random details of the master file entry ..
    mfn_id              = fake.numerify('MFN######')
    effective_timestamp = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')
    primary_key         = fake.numerify('######')

    # .. and now we can build the whole segment.
    out = f'MFE|MAD|{mfn_id}|{effective_timestamp}|{primary_key}\r'

    return out

# ################################################################################################################################
# ################################################################################################################################
