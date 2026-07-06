# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# Zato
from zato.edifact.base import EDIComponent, EDIComposite, EDIElement, EDISegment, Usage

# ################################################################################################################################
# ################################################################################################################################

class SyntaxIdentifier(EDIComposite):
    """ UNB S001 - the syntax identifier and version, e.g. UNOA:1 or UNOC:3.
    """
    identifier = EDIComponent[str](position=1, usage=Usage.REQUIRED, format='a4')
    version    = EDIComponent[str](position=2, usage=Usage.REQUIRED, format='n1')

# ################################################################################################################################
# ################################################################################################################################

class InterchangeParty(EDIComposite):
    """ UNB S002/S003 - the sender or recipient of an interchange, with an optional code qualifier.
    """
    identification    = EDIComponent[str](position=1, usage=Usage.REQUIRED, format='an..35')
    qualifier         = EDIComponent[str](position=2, usage=Usage.OPTIONAL, format='an..4')
    internal_id       = EDIComponent[str](position=3, usage=Usage.OPTIONAL, format='an..14')

# ################################################################################################################################
# ################################################################################################################################

class DateTimeOfPreparation(EDIComposite):
    """ UNB S004 - the date and time an interchange was prepared.
    """
    date = EDIComponent[str](position=1, usage=Usage.REQUIRED, format='n..8')
    time = EDIComponent[str](position=2, usage=Usage.REQUIRED, format='n4')

# ################################################################################################################################
# ################################################################################################################################

class MessageIdentifier(EDIComposite):
    """ UNH S009 - the message type identification, e.g. MEDLAB:1 or MEDRPT:D:93A:UN:MRPN32.
    """
    message_type     = EDIComponent[str](position=1, usage=Usage.REQUIRED, format='an..6')
    version          = EDIComponent[str](position=2, usage=Usage.OPTIONAL, format='an..3')
    release          = EDIComponent[str](position=3, usage=Usage.OPTIONAL, format='an..3')
    controlling_agency = EDIComponent[str](position=4, usage=Usage.OPTIONAL, format='an..2')
    association_code = EDIComponent[str](position=5, usage=Usage.OPTIONAL, format='an..6')

# ################################################################################################################################
# ################################################################################################################################

class UNB(EDISegment):
    """ Interchange header.
    """
    _segment_tag = 'UNB'

    syntax             = EDIElement[SyntaxIdentifier](position=1, usage=Usage.REQUIRED, composite='SyntaxIdentifier')
    sender             = EDIElement[InterchangeParty](position=2, usage=Usage.REQUIRED, composite='InterchangeParty')
    recipient          = EDIElement[InterchangeParty](position=3, usage=Usage.REQUIRED, composite='InterchangeParty')
    prepared_at        = EDIElement[DateTimeOfPreparation](position=4, usage=Usage.REQUIRED, composite='DateTimeOfPreparation')
    control_reference  = EDIElement[str](position=5, usage=Usage.REQUIRED, format='an..14')
    password           = EDIElement[str](position=6, usage=Usage.OPTIONAL, format='an..14')
    application_reference = EDIElement[str](position=7, usage=Usage.OPTIONAL, format='an..14')
    priority           = EDIElement[str](position=8, usage=Usage.OPTIONAL, format='a1')
    acknowledgement_request = EDIElement[str](position=9, usage=Usage.OPTIONAL, format='n1')
    agreement_identifier = EDIElement[str](position=10, usage=Usage.OPTIONAL, format='an..35')
    test_indicator     = EDIElement[str](position=11, usage=Usage.OPTIONAL, format='n1')

# ################################################################################################################################
# ################################################################################################################################

class UNH(EDISegment):
    """ Message header.
    """
    _segment_tag = 'UNH'

    reference_number = EDIElement[str](position=1, usage=Usage.REQUIRED, format='an..14')
    identifier       = EDIElement[MessageIdentifier](position=2, usage=Usage.REQUIRED, composite='MessageIdentifier')
    common_access_reference = EDIElement[str](position=3, usage=Usage.OPTIONAL, format='an..35')

# ################################################################################################################################
# ################################################################################################################################

class UNT(EDISegment):
    """ Message trailer.
    """
    _segment_tag = 'UNT'

    segment_count    = EDIElement[str](position=1, usage=Usage.REQUIRED, format='n..6')
    reference_number = EDIElement[str](position=2, usage=Usage.REQUIRED, format='an..14')

# ################################################################################################################################
# ################################################################################################################################

class UNZ(EDISegment):
    """ Interchange trailer.
    """
    _segment_tag = 'UNZ'

    message_count     = EDIElement[str](position=1, usage=Usage.REQUIRED, format='n..6')
    control_reference = EDIElement[str](position=2, usage=Usage.REQUIRED, format='an..14')

# ################################################################################################################################
# ################################################################################################################################
