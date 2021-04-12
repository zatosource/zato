# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

class AsyncCtx:
    """ Used by self.invoke_async to relay context of the invocation.
    """
    def __init__(self):
        self.calling_service = ''
        self.service_name = ''
        self.cid = ''
        self.data = ''
        self.data_format = ''
        self.callback = []
        self.zato_ctx = None
        self.environ = {}

# ################################################################################################################################
