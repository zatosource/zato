# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import dataclass
from zato.server.service import Model

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ExpiryHookInput(Model):
    current_app: 'str'
    username: 'str'
    default_expiry: 'int'

# ################################################################################################################################
# ################################################################################################################################
