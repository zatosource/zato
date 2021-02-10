# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from typing import Optional as optional

# Zato
from zato.common.dataclasses_ import dataclass

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ConnectorConfig:
    id: int
    name: str
    is_active: bool
    pool_size: int
    password: optional[str]
    service_name: optional[str]

# ################################################################################################################################
# ################################################################################################################################


