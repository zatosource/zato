# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import path_, pathlist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False, repr=False)
class HotDeployProject:
    sys_path_entry:  'path_'
    pickup_from_path:'pathlist'

    def __repr__(self) -> 'str':
        pickup_from = ', '.join(str(item) for item in self.pickup_from_path)
        return f'HotDeployProject(sys_path_entry={self.sys_path_entry}, pickup_from_path=[{pickup_from}])'

# ################################################################################################################################
# ################################################################################################################################

#
# These are default patterns that can be extended in runtime
# via the HotDeploy.Env.Pickup_Patterns environment variable.
#
pickup_order_patterns = [

    '  common*/**',
    '  util*/**',
    '  model*/**',
    '  core*/**',
    '  channel*/**',
    '  adapter*/**',
    '  api*/**',
    '  services*/**',
    '  **/enmasse*.y*ml',
]

# ################################################################################################################################
# ################################################################################################################################
