# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import CONNECTION
from zato.common.destination.constants import Channel_Fan_Out_Fields

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import anylist, strdict

# ################################################################################################################################
# ################################################################################################################################

# The fan-out of a channel - the destinations each message it accepts is delivered to once its service has run. A
# REST channel backing an HL7 MLLP one is given the MLLP channel's, so that a message received over REST reaches
# the same destinations as one received over MLLP. All three are optional, since most REST channels have no fan-out.
_destination_fields = []

for _name in Channel_Fan_Out_Fields:
    _destination_fields.append('-' + _name)

destination_input = tuple(_destination_fields)

# ################################################################################################################################
# ################################################################################################################################

def prepare_destination_settings(input:'Bunch', skip_opaque:'anylist', stored:'strdict') -> 'None':
    """ Fills in the fan-out of the channel being written - a caller that sent none of it keeps the stored
    values, which is the case of an edit of the REST channel from its own page.
    """
    if input.connection != CONNECTION.CHANNEL:
        skip_opaque.extend(Channel_Fan_Out_Fields)
        return

    for name in Channel_Fan_Out_Fields:

        if input.get(name) is not None:
            continue

        if name in stored:
            input[name] = stored[name]

# ################################################################################################################################
# ################################################################################################################################
