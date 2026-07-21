# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from http.client import OK
from inspect import isclass
from logging import getLogger

# lxml
from lxml.etree import _Element as EtreeElement
from lxml.objectify import ObjectifiedElement

# SQLAlchemy
from sqlalchemy.engine.result import Row as KeyedTuple

# Zato
from zato.common.api import DATA_FORMAT, RESTAdapterResponse, simple_types, ZATO_OK
from zato.common.marshal_.api import Model
from zato.common.util.message import Message
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
        self.cid = None
        self.data_format = None
        self.headers = {}
        self.status_code = OK
        self.status_message = 'OK'
        self.io = None
        self._content_type = 'text/plain'
        self._has_io_output = False
        self._output_model_class = None
        self._payload_vivified = False
        self.content_type_changed = False

    def __len__(self):
        return len(self._payload)

# ################################################################################################################################

    def init(self, cid, io:object, data_format, output_model_class:'any_'=None):
        self.cid = cid
        self.io = io # type: IOProcessor
        self.data_format = data_format

        # A string-based I/O definition with output declared filters the payload through the declared names ..
        if self.io:
            if not self.io.is_dataclass:
                if self.io.has_output_declared:
                    self._payload = IOPayload(self.io, self.io.all_output_elem_names, self.cid,
                        self.data_format)
                    self._has_io_output = True

                # .. an I/O definition without any output declared means the payload is free-form ..
                else:
                    self._payload = Message()

            # .. a dataclass-based definition with an output model lets the payload getter vivify
            # an instance of that model on first access - a list-based output (e.g. list_[MyModel])
            # cannot be instantiated up front and keeps today's assignment-only behavior ..
            else:
                if self.io.has_output_declared:
                    if isclass(output_model_class) and issubclass(output_model_class, Model):
                        self._output_model_class = output_model_class

                # .. a dataclass-based definition that declares input only means the payload is free-form ..
                else:
                    self._payload = Message()

        # .. and with no I/O declarations at all the payload is free-form as well, which is what
        # makes self.response.payload.abc.hello.world = 123 work with zero declarations.
        else:
            self._payload = Message()

# ################################################################################################################################

    def _get_content_type(self):
        return self._content_type

    def _set_content_type(self, value):
        self._content_type = value
        self.content_type_changed = True

    content_type = property(_get_content_type, _set_content_type) # type: past_unicode

# ################################################################################################################################

    def _get_payload(self):

        # A dataclass output model is created on the first access if nothing was assigned yet,
        # which means the service's own self.response.payload.abc = ... line is what creates it.
        # The instance is built through __new__ because models commonly use init=False
        # and requiring all the field values up front would defeat vivification.
        if self._output_model_class is not None and isinstance(self._payload, str):
            self._payload = self._output_model_class.__new__(self._output_model_class)
            self._payload_vivified = True

        return self._payload

    def _set_payload(self, value, _json=DATA_FORMAT.JSON):
        """ Strings, lists and tuples are assigned as-is. Dicts as well if I/O is not used. However, if I/O is used
        the dicts are matched and transformed according to the I/O definition.
        Generators/iterators (used for SSE streaming) are stored directly without serialization.
        """
        # An explicit assignment means the value is authoritative - model vivification is off from now on.
        self._output_model_class = None
        self._payload_vivified = False

        if hasattr(value, '__next__'):
            self._payload = value
            return

        if isinstance(value, dict):

            if self._has_io_output:
                self._payload.set_payload_attrs(value)
            else:
                self._payload = value

        else:

            # A message assigned by a service is stored as-is - a free-form one serializes
            # through getvalue later on and a SOAP one is wrapped by its channel in an envelope
            # of the request's SOAP version. It must be recognized before the to_dict probe below
            # because dot access on these messages auto-vivifies any attribute that is asked about.
            if isinstance(value, Message):
                self._payload = value

            elif isinstance(value, direct_payload) and not isinstance(value, KeyedTuple):
                self._payload = value
            else:

                if self._has_io_output:
                    self._payload.set_payload_attrs(value)
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
                            raise Exception('Cannot serialise value without I/O output declaration ({})'.format(value))

    payload = property(_get_payload, _set_payload) # type: any_

# ################################################################################################################################
# ################################################################################################################################
