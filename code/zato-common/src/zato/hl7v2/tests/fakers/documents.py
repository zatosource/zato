# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.hl7v2.tests.fakers.base import fake

# ################################################################################################################################
# ################################################################################################################################

def fake_txa() -> 'str':
    """ Returns a fake TXA (transcription document header) segment.
    """

    # Random details of the document ..
    document_type      = fake.random_element(['HP', 'DS', 'CN', 'OP'])
    activity_timestamp = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')
    document_id        = fake.numerify('DOC######')

    # .. random details of its author ..
    author_id    = fake.numerify('##########')
    author_last  = fake.last_name().upper()
    author_first = fake.first_name().upper()

    # .. and now we can build the whole segment.
    out = (
        f'TXA|1|{document_type}|TX|'
        f'{activity_timestamp}|'
        f'{author_id}^{author_last}^{author_first}|||||||'
        f'{document_id}||AU\r'
    )

    return out

# ################################################################################################################################
# ################################################################################################################################
