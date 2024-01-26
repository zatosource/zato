# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class HL7Exception(Exception):
    """ A common class for raising HL7 parsing-related exceptions.
    """
    data: 'str'
    inner_exc: 'Exception | None'
    exc_message: 'str'

    def __init__(
        self,
        exc_message,   # type: str
        data,          # type: str
        inner_exc=None # type: Exception | None
    ) -> 'None':
        self.exc_message = exc_message
        self.data = data
        self.inner_exc = inner_exc

# ################################################################################################################################
# ################################################################################################################################
