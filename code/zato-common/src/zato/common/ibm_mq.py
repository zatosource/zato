# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

class ConnectorClosedException(Exception):
    def __init__(self, exc, message):
        self.inner_exc = exc
        super().__init__(message)
