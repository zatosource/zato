# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

class HL7Exception(Exception):
    """ Raised when an HL7 parsing or processing error occurs.
    """
    def __init__(self, msg:'str', data:'object'=None, orig_exc:'object'=None) -> 'None':
        self.data = data
        self.orig_exc = orig_exc
        super().__init__(msg)
