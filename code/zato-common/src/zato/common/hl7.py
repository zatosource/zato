# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

class HL7Exception(Exception):
    """ A common class for raising HL7 parsing-related exceptions.
    """
    __slots__ = 'exc_message', 'data', 'inner_exc'

    def __init__(self, exc_message, data, inner_exc=None):
        # type: (str, str, Exception)
        self.exc_message = exc_message
        self.data = data
        self.inner_exc = inner_exc
