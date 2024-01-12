# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.typing_ import dataclass
from zato.server.service import Model

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class GoogleAPIDescription(Model):
    id: 'str'
    name: 'str'
    title: 'str'
    version: 'str'
    title_full: 'str'

# ################################################################################################################################
# ################################################################################################################################
