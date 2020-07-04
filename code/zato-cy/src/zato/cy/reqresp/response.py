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

# lxml
from lxml.etree import _Element as EtreeElement
from lxml.objectify import ObjectifiedElement

# SQLAlchemy
from sqlalchemy.util import KeyedTuple

# Zato
from zato.common import simple_types, ZATO_OK
from zato.cy.reqresp.payload import SimpleIOPayload

# Python 2/3 compatibility
from past.builtins import unicode as past_unicode

# ################################################################################################################################

if 0:
    from zato.cy.simpleio import SIODefinition

    past_unicode = past_unicode
    SIODefinition = SIODefinition

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

direct_payload:tuple = simple_types + (EtreeElement, ObjectifiedElement)

# ################################################################################################################################
# ################################################################################################################################

@cy.cclass
class Response(object):
    """ A response from a service's invocation.
    """
    # Public attributes
    result           = cy.declare(cy.unicode, visibility='public') # type: past_unicode
    result_details   = cy.declare(cy.unicode, visibility='public') # type: past_unicode
    _payload          = cy.declare(cy.unicode, visibility='public') # type: past_unicode
    content_encoding = cy.declare(cy.unicode, visibility='public') # type: past_unicode
    cid              = cy.declare(cy.unicode, visibility='public') # type: past_unicode
    data_format      = cy.declare(cy.unicode, visibility='public') # type: past_unicode
    headers          = cy.declare(cy.dict, visibility='public')    # type: dict
    status_code      = cy.declare(cy.int, visibility='public')     # type: int
    status_message   = cy.declare(cy.unicode, visibility='public') # type: past_unicode
    sio_config:SIODefinition = None

    # Private-use attributes (still declared as public)
    _content_type     = cy.declare(cy.unicode, visibility='public') # type: past_unicode

    def __cinit__(self):
        self.result = ZATO_OK
        self.result_details = ''
        self._payload = ''
        self.content_encoding = None
        self.cid = None
        self.data_format = None
        self.headers = None
        self.status_code = OK
        self.status_message = 'OK'
        self._content_type = 'text/plain'

    def __len__(self):
        return len(self._payload)

# ################################################################################################################################

    def init(self, cid:str, data_format:str):
        self.cid = cid
        self.data_format = data_format

        if self.sio_config.has_output_declared:
            self._payload = SimpleIOPayload(self.cid, self.data_format)

# ################################################################################################################################

    def _get_content_type(self):
        return self._content_type

    def _set_content_type(self, value):
        self._content_type = value
        self.content_type_changed = True

    content_type = property(_get_content_type, _set_content_type)

# ################################################################################################################################

    def _get_payload(self):
        return self._payload

    def _set_payload(self, value):
        """ Strings, lists and tuples are assigned as-is. Dicts as well if SIO is not used. However, if SIO is used
        the dicts are matched and transformed according to the SIO definition.
        """

        # This covers dict and subclasses, e.g. Bunch
        if isinstance(value, dict):

            # If we are using SimpleIO, extract elements from that dict ..
            if self.sio_config.has_output_declared:
                self._payload.set_payload_attrs(value)

            # .. otherwise, assign the dict as-is.
            else:
                self._payload = value
        else:

            # Must be an object of a type that we do not serialise ourselves ..
            if isinstance(value, direct_payload) and not isinstance(value, KeyedTuple):
                self._payload = value

            # .. otherwise, we will try to serialise it ..
            else:

                # .. if using SimpleIO ..
                if self.sio_config.has_output_declared:
                    self._payload.set_payload_attrs(value)

                # .. someone assigns to self.response.payload an object that needs
                # serialisation but we do not know how to do it.
                else:
                    raise Exception('Cannot serialise value without SimpleIO ouput declaration ({})'.format(value))

    payload = property(_get_payload, _set_payload)

# ################################################################################################################################
# ################################################################################################################################
