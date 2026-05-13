# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

class HL7Exception(Exception):
    """ Raised when an HL7 parsing or processing error occurs.
    """
    def __init__(self, message:'str', data:'object'=None, original_exception:'object'=None) -> 'None':
        self.data = data
        self.original_exception = original_exception
        super().__init__(message)
