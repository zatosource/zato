# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# Zato
from zato.x12.base import EDIElement, Usage, X12Segment

# ################################################################################################################################
# ################################################################################################################################

class ISA(X12Segment):
    """ Interchange control header - the fixed-width segment every X12 interchange starts with.
    """
    _segment_tag = 'ISA'

    auth_qualifier       = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/2')
    auth_information     = EDIElement[str](position=2, usage=Usage.REQUIRED, format='AN 10/10')
    security_qualifier   = EDIElement[str](position=3, usage=Usage.REQUIRED, format='ID 2/2')
    security_information = EDIElement[str](position=4, usage=Usage.REQUIRED, format='AN 10/10')
    sender_qualifier     = EDIElement[str](position=5, usage=Usage.REQUIRED, format='ID 2/2')
    sender_id            = EDIElement[str](position=6, usage=Usage.REQUIRED, format='AN 15/15')
    receiver_qualifier   = EDIElement[str](position=7, usage=Usage.REQUIRED, format='ID 2/2')
    receiver_id          = EDIElement[str](position=8, usage=Usage.REQUIRED, format='AN 15/15')
    date                 = EDIElement[str](position=9, usage=Usage.REQUIRED, format='DT 6/6')
    time                 = EDIElement[str](position=10, usage=Usage.REQUIRED, format='TM 4/4')

    # ISA11 is the repetition separator in version 00402 and later -
    # in older interchanges it carries the standards identifier U instead.
    repetition_separator = EDIElement[str](position=11, usage=Usage.REQUIRED, format='1/1')

    version              = EDIElement[str](position=12, usage=Usage.REQUIRED, format='ID 5/5')
    control_number       = EDIElement[str](position=13, usage=Usage.REQUIRED, format='N0 9/9')
    ack_requested        = EDIElement[str](position=14, usage=Usage.REQUIRED, format='ID 1/1')
    usage_indicator      = EDIElement[str](position=15, usage=Usage.REQUIRED, format='ID 1/1')
    component_separator  = EDIElement[str](position=16, usage=Usage.REQUIRED, format='1/1')

# ################################################################################################################################
# ################################################################################################################################

class IEA(X12Segment):
    """ Interchange control trailer.
    """
    _segment_tag = 'IEA'

    group_count    = EDIElement[str](position=1, usage=Usage.REQUIRED, format='N0 1/5')
    control_number = EDIElement[str](position=2, usage=Usage.REQUIRED, format='N0 9/9')

# ################################################################################################################################
# ################################################################################################################################

class GS(X12Segment):
    """ Functional group header.
    """
    _segment_tag = 'GS'

    functional_id_code = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 2/2')
    sender_code        = EDIElement[str](position=2, usage=Usage.REQUIRED, format='AN 2/15')
    receiver_code      = EDIElement[str](position=3, usage=Usage.REQUIRED, format='AN 2/15')
    date               = EDIElement[str](position=4, usage=Usage.REQUIRED, format='DT 8/8')
    time               = EDIElement[str](position=5, usage=Usage.REQUIRED, format='TM 4/8')
    control_number     = EDIElement[str](position=6, usage=Usage.REQUIRED, format='N0 1/9')
    agency_code        = EDIElement[str](position=7, usage=Usage.REQUIRED, format='ID 1/2')
    version            = EDIElement[str](position=8, usage=Usage.REQUIRED, format='AN 1/12')

# ################################################################################################################################
# ################################################################################################################################

class GE(X12Segment):
    """ Functional group trailer.
    """
    _segment_tag = 'GE'

    transaction_set_count = EDIElement[str](position=1, usage=Usage.REQUIRED, format='N0 1/6')
    control_number        = EDIElement[str](position=2, usage=Usage.REQUIRED, format='N0 1/9')

# ################################################################################################################################
# ################################################################################################################################

class ST(X12Segment):
    """ Transaction set header.
    """
    _segment_tag = 'ST'

    identifier_code = EDIElement[str](position=1, usage=Usage.REQUIRED, format='ID 3/3')
    control_number  = EDIElement[str](position=2, usage=Usage.REQUIRED, format='AN 4/9')

    # ST03 carries the implementation convention reference in version 005010, e.g. 005010X222A1.
    implementation_reference = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='AN 1/35')

# ################################################################################################################################
# ################################################################################################################################

class SE(X12Segment):
    """ Transaction set trailer.
    """
    _segment_tag = 'SE'

    segment_count  = EDIElement[str](position=1, usage=Usage.REQUIRED, format='N0 1/10')
    control_number = EDIElement[str](position=2, usage=Usage.REQUIRED, format='AN 4/9')

# ################################################################################################################################
# ################################################################################################################################

class TA1(X12Segment):
    """ Interchange acknowledgment - reports the disposition of a whole interchange.
    """
    _segment_tag = 'TA1'

    control_number = EDIElement[str](position=1, usage=Usage.REQUIRED, format='N0 9/9')
    date           = EDIElement[str](position=2, usage=Usage.REQUIRED, format='DT 6/6')
    time           = EDIElement[str](position=3, usage=Usage.REQUIRED, format='TM 4/4')
    ack_code       = EDIElement[str](position=4, usage=Usage.REQUIRED, format='ID 1/1')
    note_code      = EDIElement[str](position=5, usage=Usage.REQUIRED, format='ID 3/3')

# ################################################################################################################################
# ################################################################################################################################
