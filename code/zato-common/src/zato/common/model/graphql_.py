# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import dataclass, intnone, strnone

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class GraphQLConfigObject:
    id: int = 0
    name: str = ''
    is_active: bool = False
    is_internal: bool = False
    address: str = ''
    security_id: strnone = None
    security_name: strnone = None
    sec_type: strnone = None
    username: strnone = None
    password: strnone = None
    default_query_timeout: intnone = None
    extra: strnone = None

# ################################################################################################################################
# ################################################################################################################################
