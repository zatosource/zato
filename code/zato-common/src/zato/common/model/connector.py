# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import Optional as optional

# Zato
from zato.common.typing_ import dataclass

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ConnectorConfig:
    id: int
    name: str
    port: optional[int]
    address: optional[str]
    is_active: optional[bool]
    pool_size: optional[int]
    def_name: optional[str]
    old_name: optional[str]
    password: optional[str]
    service_name: optional[str]

# ################################################################################################################################
# ################################################################################################################################
