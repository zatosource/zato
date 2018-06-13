# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals


# Zato
from zato.cli import ZatoCommand
from zato.common.util import get_client_from_server_conf

# ################################################################################################################################

stderr_sleep_fg = 0.9
stderr_sleep_bg = 1.2

# ################################################################################################################################

class APISpec(ZatoCommand):
    """API specifications generator."""

# ################################################################################################################################

    def execute(self, args):
        client = get_client_from_server_conf(args.path)
        print(client.invoke('zato.ping'))
        print()