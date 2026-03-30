# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import dataclass, strnone

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class HL7MLLPConfigObject:
    id: int = 0
    name: str = ''
    is_active: bool = False
    is_internal: bool = False
    address: str = ''
    service: strnone = None
    security_name: strnone = None
    pool_size: int = 1

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class HL7FHIRConfigObject:
    id: int = 0
    name: str = ''
    is_active: bool = False
    is_internal: bool = False
    address: str = ''
    security_id: strnone = None
    security_name: strnone = None
    pool_size: int = 1

# ################################################################################################################################
# ################################################################################################################################
