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
class HL7MLLPChannelConfigObject:
    id: int = 0
    name: str = ''
    is_active: bool = False
    is_internal: bool = False
    service: strnone = None
    security_name: strnone = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class HL7MLLPOutconnConfigObject:
    id: int = 0
    name: str = ''
    is_active: bool = False
    is_internal: bool = False
    address: str = ''
    security_name: strnone = None
    pool_size: int = 1

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class HL7RESTChannelConfigObject:
    id: int = 0
    name: str = ''
    is_active: bool = False
    is_internal: bool = False
    hl7_version: str = ''
    url_path: str = ''
    service_name: strnone = None
    security_id: strnone = None
    security_name: strnone = None
    sec_type: strnone = None
    sec_type_name: strnone = None
    data_format: str = ''

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
