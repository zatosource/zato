# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals


# Zato
from zato.cli import ZatoCommand
from zato.common.util import get_client_from_server_conf

# ################################################################################################################################

if 0:
    # stdlib
    from argparse import Namespace

    Namespace = Namespace

# ################################################################################################################################

class Cache(ZatoCommand):
    """ Base class for cache-related commands.
    """
    def execute(self, args):
        # type: (Namespace) -> object

        self.logger.warn('QQQ %s', args)

# ################################################################################################################################
