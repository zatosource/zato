# -*- coding: utf-8 -*-

# cython: auto_pickle=False

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
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
from zato.common.api import DATA_FORMAT, simple_types, ZATO_OK
from zato.common.marshal_.api import Model
from zato.cy.reqresp.payload import SimpleIOPayload

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode as past_unicode

# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.simpleio import CySimpleIO
    any_ = any_
    CySimpleIO = CySimpleIO
    past_unicode = past_unicode

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

direct_payload:tuple = simple_types + (EtreeElement, ObjectifiedElement)

# ################################################################################################################################
# ################################################################################################################################

@cy.cclass
class Response:
    """ A response from a service's invocation.
    """
    # Public attributes
    result           = cy.declare(cy.object, visibility='public')  # type: past_unicode
    result_details   = cy.declare(cy.object, visibility='public')  # type: past_unicode
    _payload         = cy.declare(cy.object, visibility='public')   # type: object
    content_encoding = cy.declare(cy.object, visibility='public')  # type: past_unicode
    cid              = cy.declare(cy.object, visibility='public')  # type: past_unicode
    data_format      = cy.declare(cy.object, visibility='public')  # type: past_unicode
    headers          = cy.declare(cy.dict, visibility='public')     # type: dict
    status_code      = cy.declare(cy.int, visibility='public')      # type: int
    status_message   = cy.declare(cy.object, visibility='public')  # type: past_unicode
    sio              = cy.declare(object, visibility='public')      # type: CySimpleIO

    # Private-use attributes (still declared as public)
    _content_type        = cy.declare(cy.object, visibility='public') # type: past_unicode
    _has_sio_output      = cy.declare(cy.bint, visibility='public')    # type: bool
    content_type_changed = cy.declare(cy.bint, visibility='public')    # type: bool

    def __cinit__(self):
        self.result = ZATO_OK
        self.result_details = ''
        self._payload = ''
        self.content_encoding = None
        self.cid = None
        self.data_format = None
        self.headers = {}
        self.status_code = OK
        self.status_message = 'OK'
        self.sio = None
        self._content_type = 'text/plain'
        self._has_sio_output = False

    def __len__(self):
        return len(self._payload)

# ################################################################################################################################

    def init(self, cid, sio:object, data_format):
        self.cid = cid
        self.sio = sio # type: CySimpleIO
        self.data_format = data_format

        # We get below only if there is an SIO definition, but not a dataclass-based one, and it has output declared
        if self.sio:
            if not self.sio.is_dataclass:
                if cy.cast(cy.bint, self.sio.definition.has_output_declared):
                    self._payload = SimpleIOPayload(self.sio, self.sio.definition.all_output_elem_names, self.cid,
                        self.data_format)
                    self._has_sio_output = True

# ################################################################################################################################

    def _get_content_type(self):
        return self._content_type

    def _set_content_type(self, value):
        self._content_type = value
        self.content_type_changed = True

    content_type = property(_get_content_type, _set_content_type) # type: past_unicode

# ################################################################################################################################

    def _get_payload(self):
        return self._payload

    def _set_payload(self, value, _json=DATA_FORMAT.JSON):
        """ Strings, lists and tuples are assigned as-is. Dicts as well if SIO is not used. However, if SIO is used
        the dicts are matched and transformed according to the SIO definition.
        """
        # 1)
        # This covers dict and subclasses, e.g. Bunch
        if isinstance(value, dict):

            # 1a)
            # If we are using SimpleIO, extract elements from that dict ..
            if self._has_sio_output:
                self._payload.set_payload_attrs(value)

            # 1b)
            # .. otherwise, assign the dict as-is.
            else:
                self._payload = value

        # 2)
        else:

            # 2a)
            # Must be an object of a type that we do not serialise ourselves ..
            if isinstance(value, direct_payload) and not isinstance(value, KeyedTuple):
                self._payload = value

            # 2b)
            # .. otherwise, we will try to serialise it ..
            else:

                # 2b1)
                # .. if using SimpleIO ..
                if self._has_sio_output:
                    self._payload.set_payload_attrs(value)

                # 2b2)
                else:
                    if value:
                        if isinstance(value, Model):
                            if self.data_format == _json:
                                self._payload = value.to_dict()
                            else:
                                self._payload = value

                        elif hasattr(value, 'to_dict'):
                            self._payload = value.to_dict()

                        elif hasattr(value, 'to_json'):
                            self._payload = value.to_json()

                        else:
                            # .. someone assigned to self.response.payload an object that needs
                            # serialisation but we do not know how to do it.
                            raise Exception('Cannot serialise value without SimpleIO ouput declaration ({})'.format(value))

    payload = property(_get_payload, _set_payload) # type: any_

# ################################################################################################################################
# ################################################################################################################################
