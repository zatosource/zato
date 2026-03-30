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
    id: int
    name: str
    is_active: bool
    is_internal: bool
    address: str
    service: strnone = None
    security_name: strnone = None
    pool_size: int = 1

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class HL7FHIRConfigObject:
    id: int
    name: str
    is_active: bool
    is_internal: bool
    address: str
    security_id: strnone = None
    security_name: strnone = None
    sec_tls_ca_cert_id: strnone = None
    sec_def_type_name: strnone = None
    pool_size: int = 1

# ################################################################################################################################
# ################################################################################################################################
