# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# Zato
from zato.hl7v2.base import HL7Segment

# ################################################################################################################################
# ################################################################################################################################

# Z-segments are locally defined by vendors and sites - no HL7 version specifies
# their fields, so the classes below carry no field descriptors. Values are read
# and assigned positionally (e.g. zds_1), which HL7Segment supports natively,
# and serialization reproduces the assigned positions verbatim.

# ################################################################################################################################
# ################################################################################################################################

class ZDS(HL7Segment):
    """ Study instance UID reference, a de-facto standard Z-segment from the IHE
    Radiology Scheduled Workflow profile, emitted by RIS and PACS systems.
    """
    _segment_id = 'ZDS'

# ################################################################################################################################
# ################################################################################################################################
