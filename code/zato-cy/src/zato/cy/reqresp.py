# -*- coding: utf-8 -*-

# cython: auto_pickle=False

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from http.client import OK
from logging import getLogger

# Cython
import cython as cy


# Zato
from zato.common import ZATO_OK

# Python 2/3 compatibility
from past.builtins import unicode as past_unicode

# ################################################################################################################################

if 0:
    from zato.cy.simpleio import SIODefinition

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

@cy.cclass
class SimpleIOPayload(object):
    """ Represents a payload, i.e. individual response elements, set via SimpleIO.
    """

# ################################################################################################################################
# ################################################################################################################################

@cy.cclass
class Response(object):
    """ A response from a service's invocation.
    """
    # Public attributes
    result           = cy.declare(cy.unicode, visibility='public') # type: past_unicode
    result_details   = cy.declare(cy.unicode, visibility='public') # type: past_unicode
    payload          = cy.declare(cy.unicode, visibility='public') # type: past_unicode
    content_encoding = cy.declare(cy.unicode, visibility='public') # type: past_unicode
    data_format      = cy.declare(cy.unicode, visibility='public') # type: past_unicode
    headers          = cy.declare(cy.dict, visibility='public')    # type: dict
    sio_config:SIODefinition = None

    outgoing_declared = cy.declare(cy.bint, visibility='public')    # type: bool
    _content_type     = cy.declare(cy.unicode, visibility='public') # type: past_unicode

    def __cinit__(self):
        self.result = ZATO_OK
        self.result_details = ''
        self.payload = ''
        self.content_encoding = None
        self.data_format = None
        self.headers = None
        self.status_code = OK
        self.status_message = 'OK'
        self.simple_io_config = None
        self.outgoing_declared = False
        self._content_type = 'text/plain'

        print(111, self.sio_config.has_input_required)
        print(222, self.headers['aaa'])

# ################################################################################################################################
# ################################################################################################################################
