# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

@dataclass(init=False)
class HotDeployTree:
    sys_path_entry:'str'
    pickup_from_path:'str'
