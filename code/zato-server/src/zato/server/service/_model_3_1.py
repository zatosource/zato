# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from zato.common.ext.dataclasses import dataclass

# ################################################################################################################################

@dataclass(init=False)
class AsyncCtx:
    """ Used by self.invoke_async to relay context of the invocation.
    """
    calling_service: str
    service_name: str
    cid: str
    data: str
    data_format: str
    callback: optional[list] = None
    zato_ctx: object
    environ: dict

# ################################################################################################################################
