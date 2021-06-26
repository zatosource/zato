# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################
# ################################################################################################################################

class TestingService(object):

    schema = None

    @staticmethod
    def after_add_to_store(*ignored_args, **ignored_kwargs):
        pass

# ################################################################################################################################
# ################################################################################################################################
