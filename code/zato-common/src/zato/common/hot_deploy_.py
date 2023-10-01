# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

@dataclass(init=False)
class HotDeployProject:
    sys_path_entry:'str'
    pickup_from_path:'str'

pickup_order_patterns = [

    '  common*',
    '*_common*',

    '  model_core*_common',
    '  model*_common',
    '  model*',
    '*_model*_common',
    '*_model*',

    '  lib*',
    '*_lib*',

    '  util*_common',
    '  util*',
    '*_util*',

    '  pri_*',
    '*_pri',

    '  core_*_common',
    '  core_*',

    '  channel_*_common',
    '  channel_*',

    '  adapter_*_common',
    '  adapter_*',
]
