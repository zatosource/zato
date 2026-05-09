# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from http.client import OK
from logging import getLogger

# lxml
from lxml.etree import _Element as EtreeElement
from lxml.objectify import ObjectifiedElement

# SQLAlchemy
from sqlalchemy.engine.result import Row as KeyedTuple

# Zato
from zato.common.api import DATA_FORMAT, RESTAdapterResponse, simple_types, ZATO_OK
from zato.common.marshal_.api import Model
from zato.server.reqresp.payload import IOPayload

# Python 2/3 compatibility
from zato.common.py23_.past.builtins import unicode as past_unicode

# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.input_output import IOProcessor
    any_ = any_
    IOProcessor = IOProcessor
    past_unicode = past_unicode

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

direct_payload:tuple = simple_types + (RESTAdapterResponse, EtreeElement, ObjectifiedElement)

# ################################################################################################################################
# ################################################################################################################################

class Response:
    """ A response from a service's invocation.
    """

    def __init__(self):
        self.result = ZATO_OK
        self.result_details = ''
        self._payload = ''
        self.content_encoding = None
        self.cid = None
        self.data_format = None
        self.headers = {}
        self.status_code = OK
        self.status_message = 'OK'
        self.io = None
        self._content_type = 'text/plain'
        self._has_io_output = False
        self.content_type_changed = False

    def __len__(self):
        return len(self._payload)

# ################################################################################################################################

    def init(self, cid, io:object, data_format):
        self.cid = cid
        self.io = io # type: IOProcessor
        self.data_format = data_format

        # We get below only if there is an I/O definition, but not a dataclass-based one, and it has output declared
        if self.io:
            if not self.io.is_dataclass:
                if bool(self.io.definition.has_output_declared):
                    self._payload = IOPayload(self.io, self.io.definition.all_output_elem_names, self.cid,
                        self.data_format)
                    self._has_io_output = True

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
        """ Strings, lists and tuples are assigned as-is. Dicts as well if I/O is not used. However, if I/O is used
        the dicts are matched and transformed according to the I/O definition.
        Generators/iterators (used for SSE streaming) are stored directly without serialization.
        """
        # 0)
        # Streaming iterators (e.g. SSE generators) bypass all serialization ..
        if hasattr(value, '__next__'):
            self._payload = value
            return

        # 1)
        # This covers dict and subclasses, e.g. Bunch
        if isinstance(value, dict):

            # 1a)
            # If we are using I/O, extract elements from that dict ..
            if self._has_io_output:
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
            # .. otherwise, we will try to serialize it ..
            else:

                # 2b1)
                # .. if using I/O ..
                if self._has_io_output:
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
                            raise Exception('Cannot serialise value without I/O output declaration ({})'.format(value))

    payload = property(_get_payload, _set_payload) # type: any_

# ################################################################################################################################
# ################################################################################################################################
