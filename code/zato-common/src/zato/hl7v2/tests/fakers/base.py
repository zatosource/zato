# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Faker
from faker import Faker

# ################################################################################################################################
# ################################################################################################################################

fake = Faker()
Faker.seed(12345)

# ################################################################################################################################
# ################################################################################################################################

# The maximum length of application and facility names in MSH segments
_max_name_length = 10

# ################################################################################################################################
# ################################################################################################################################

def fake_msh(message_type:'str', trigger:'str', structure_id:'str') -> 'str':
    """ Returns a fake MSH segment for the given message type, trigger and structure ID.
    """

    # Random names for the sending and receiving sides ..
    sending_application   = fake.company().upper()
    sending_facility      = fake.company().upper()
    receiving_application = fake.company().upper()
    receiving_facility    = fake.company().upper()

    # .. truncated to the maximum length allowed ..
    sending_application   = sending_application[:_max_name_length]
    sending_facility      = sending_facility[:_max_name_length]
    receiving_application = receiving_application[:_max_name_length]
    receiving_facility    = receiving_facility[:_max_name_length]

    # .. a timestamp and control ID for the header ..
    message_timestamp = fake.date_time_this_year().strftime('%Y%m%d%H%M%S')
    msg_id            = fake.numerify('MSG######')

    # .. and now we can build the whole segment.
    out = (
        f'MSH|^~\\&|{sending_application}|{sending_facility}|'
        f'{receiving_application}|{receiving_facility}|'
        f'{message_timestamp}||'
        f'{message_type}^{trigger}^{structure_id}|{msg_id}|P|2.9\r'
    )

    return out

# ################################################################################################################################

def fake_segment(segment_id:'str') -> 'str':
    """ Returns a minimal valid segment for any segment type.
    """
    out = f'{segment_id}|1\r'
    return out

# ################################################################################################################################
# ################################################################################################################################
