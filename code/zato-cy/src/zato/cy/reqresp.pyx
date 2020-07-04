# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from http.client import OK
from logging import getLogger

# Zato
from zato.common import ZATO_OK
cimport src.zato.cy.simpleio._simpleio as sio

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

cdef class SimpleIOPayload(object):
    """ Represents a payload, i.e. individual response elements, set via SimpleIO.
    """

# ################################################################################################################################
# ################################################################################################################################

cdef class Response(object):
    """ A response from a service's invocation.
    """

    cdef:
        # Public attributes
        public str result
        public str result_details
        public str payload
        public str content_encoding
        public str data_format
        public dict headers
        public int status_code
        public str status_message
        public sio.SIODefinition sio_config

        # Private attributes
        bint outgoing_declared
        str _content_type

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

        print(111, self.sio_config.zzz)

# ################################################################################################################################
# ################################################################################################################################
