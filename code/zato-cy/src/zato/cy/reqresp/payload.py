# -*- coding: utf-8 -*-

# cython: auto_pickle=False

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Cython
import cython as cy

# Python 2/3 compatibility
from past.builtins import unicode as past_unicode

if 0:
    past_unicode = past_unicode

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

@cy.cclass
class SimpleIOPayload(object):
    """ Represents a payload, i.e. individual response elements, set via SimpleIO.
    """
    cid         = cy.declare(cy.unicode, visibility='public') # type: past_unicode
    data_format = cy.declare(cy.unicode, visibility='public') # type: past_unicode

    def __cinit__(self, cid:str, data_format:str):
        self.cid = cid
        self.data_format = data_format

# ################################################################################################################################
# ################################################################################################################################
