# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.server.service import Model

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Member(Model):

    id: 'int'
    name: 'str'
    type: 'str'

    group_id: 'int'
    security_id: 'int'

    sec_type: 'str'
    username: 'str' = ''
    password: 'str' = ''
    header_value: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################
