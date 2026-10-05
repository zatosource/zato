# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.exception import ZatoException

# ################################################################################################################################
# ################################################################################################################################

class CCDAError(ZatoException):
    """ Raised when a C-CDA document cannot be converted - the reason says whether the converter is missing,
    the input is not a CDA document, the converter failed or it ran out of time.
    """
    cid: 'str'
    msg: 'str'

    def __init__(self, cid:'str', reason:'str', msg:'str', *, exit_code:'int'=0, stderr:'str'='') -> 'None':
        super().__init__(cid, msg)
        self.reason = reason
        self.exit_code = exit_code
        self.stderr = stderr

# ################################################################################################################################
# ################################################################################################################################
