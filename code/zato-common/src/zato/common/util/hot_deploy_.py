# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import HotDeploy
from zato.common.hot_deploy_ import HotDeployTree
from zato.common.typing_ import cast_
from zato.common.util.file_system import resolve_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import iterator_, strdictdict

# ################################################################################################################################
# ################################################################################################################################

def extract_pickup_from_items(
    base_dir,      # type: str
    pickup_config, # type: strdictdict
) -> 'iterator_[str | HotDeployTree]':

    # Go through each piece of the hot-deployment configuration ..
    for key, value in pickup_config.items(): # type: ignore

        # .. we handle only specific keys ..
        if key.startswith(HotDeploy.UserPrefix):

            # .. proceed only if we know where to pick up from ..
            if pickup_from := value.get('pickup_from'): # type: ignore

                # .. type hints ..
                pickup_from = cast_('str', pickup_from)

                # .. this will resolve home directories and environment variables ..
                pickup_from = resolve_path(pickup_from, base_dir)

                yield pickup_from

# ################################################################################################################################
# ################################################################################################################################
