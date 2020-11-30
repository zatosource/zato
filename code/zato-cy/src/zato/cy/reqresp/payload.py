# -*- coding: utf-8 -*-

# cython: auto_pickle=False

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from logging import getLogger
from operator import getitem

# Cython
import cython as cy

# SQLAlchemy
from sqlalchemy.util import KeyedTuple

# Zato
from zato.common.api import DATA_FORMAT
from zato.common.odb.api import WritableKeyedTuple

# Zato - Cython
from zato.simpleio import CySimpleIO, SIODefinition

# Python 2/3 compatibility
from past.builtins import unicode as past_unicode

# ################################################################################################################################

if 0:
    from zato.simpleio import CySimpleIO

    CySimpleIO = CySimpleIO
    past_unicode = past_unicode

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

DATA_FORMAT_DICT:str = DATA_FORMAT.DICT
_not_given:object = object()

# ################################################################################################################################
# ################################################################################################################################

@cy.cclass
class SimpleIOPayload(object):
    """ Represents a payload, i.e. individual response elements, set via SimpleIO.
    """
    sio = cy.declare(cy.object, visibility='public')              # type: CySimpleIO
    all_output_elem_names = cy.declare(list, visibility='public') # type: list
    output_repeated = cy.declare(cy.bint, visibility='public')    # type: bool

    cid         = cy.declare(cy.object, visibility='public') # type: past_unicode
    data_format = cy.declare(cy.object, visibility='public') # type: past_unicode

    # One of the two will be used to produce a response
    user_attrs_dict = cy.declare(dict, visibility='public') # type: dict
    user_attrs_list = cy.declare(list, visibility='public') # type: list

    # This is used by Zato internal services only
    zato_meta = cy.declare(cy.object, visibility='public') # type: object

# ################################################################################################################################

    def __cinit__(self, sio:CySimpleIO, all_output_elem_names:list, cid, data_format):
        self.sio = sio
        self.all_output_elem_names = all_output_elem_names
        self.output_repeated = self.sio.definition.output_repeated
        self.cid = cid
        self.data_format = data_format
        self.user_attrs_dict = {}
        self.user_attrs_list = []
        self.zato_meta = None

# ################################################################################################################################

    @cy.returns(dict)
    def _extract_payload_attrs(self, item:object) -> dict:
        """ Extract response attributes from a single object. Used with items other than dicts.
        """
        extracted:dict = {}
        is_dict:bint = isinstance(item, dict)

        # Use a different function depending on whether the object is dict-like or not.
        # Note that we need .get to be able to provide a default value.
        has_get = hasattr(item, 'get') # type: bool
        name = None

        for name in self.all_output_elem_names: # type: str
            if is_dict:
                value = cy.cast(dict, item).get(name, _not_given)
            elif has_get:
                value = item.get(name, _not_given)
            else:
                value = getattr(item, name, _not_given)
            if value is not _not_given:
                extracted[name] = value

        return extracted

# ################################################################################################################################

    @cy.returns(dict)
    def _extract_payload_attrs_dict(self, item:object) -> dict:
        """ Extract response attributes from a dict.
        """
        extracted:dict = {}
        name = None

        for name in self.all_output_elem_names:
            value = item.get(name, _not_given)
            if value is not _not_given:
                extracted[name] = value

        return extracted

# ################################################################################################################################

    @cy.cfunc
    def _is_sqlalchemy(self, item:object):
        return hasattr(item, '_sa_class_manager')

# ################################################################################################################################

    @cy.cfunc
    def _preprocess_payload_attrs(self, value):

        # First, check if this is not a response from a Zato service wrapped in a response element.
        # If it is, extract the actual inner response first.
        if isinstance(value, dict) and len(value) == 1:
            response_name:str = list(value.keys())[0] # type: str
            if response_name.startswith('zato') and response_name.endswith('_response'):
                return value[response_name]
        else:
            return value

# ################################################################################################################################

    @cy.ccall
    def set_payload_attrs(self, value:object):
        """ Assigns user-defined attributes to what will eventually be a response.
        """

        # #####################################################################################################
        #
        # In a rare case that we do something like the below ..
        #
        # service.response.payload = service.response.payload.getvalue(False)
        #
        # .. that is, assigning to payload its own value without previous serialisation,
        # just like it used to be done in WorkerStore._set_service_response_data,
        # we will need possibly to rethink the idea of clearing out the user attributes
        #
        # For now, this is not a concern because, with the exception of WorkerStore._set_service_response_data,
        # which is no longer doing it, no other component will attempt it
        # and this comment is left just in case reconsidering it in the future.
        #
        # #####################################################################################################

        # First, clear out what was potentially set earlier
        self.user_attrs_dict.clear()
        self.user_attrs_list[:] = []

        value = self._preprocess_payload_attrs(value)
        is_dict:cy.bint = isinstance(value, dict)

        # Shortcut in case we know already this is a dict on input
        if is_dict:
            dict_attrs:dict = self._extract_payload_attrs_dict(value)
            self.user_attrs_dict.update(dict_attrs)
        else:
            # Check if this is something that can be explicitly serialised for our purposes
            if hasattr(value, 'to_zato'):
                value = value.to_zato()

            if isinstance(value, (list, tuple)):
                for item in value:
                    self.user_attrs_list.append(self._extract_payload_attrs(item))
            else:
                self.user_attrs_dict.update(self._extract_payload_attrs(value))

# ################################################################################################################################

    @cy.ccall
    def getvalue(self, serialize:bool=True, force_dict_serialisation:bool=True):
        """ Returns a service's payload, either serialised or not.
        """
        if self.data_format == DATA_FORMAT_DICT:
            if force_dict_serialisation:
                serialize = True

        # If data format is DICT, we force serialisation to that format
        # unless overridden on input.
        value = self.user_attrs_list if self.output_repeated else self.user_attrs_dict

        # Special-case internal services that return metadata (e.g GetList-like ones)
        if self.zato_meta:

            # If search is provided, we need to first get output,
            # append the search the metadata and then serialise ..
            search = self.zato_meta.get('search')
            if search:
                output = self.sio.get_output(value, self.data_format, False)
                output['_meta'] = search
                return self.sio.serialise(output, self.data_format)

            # .. otherwise, with no search metadata provided,
            # we can data, serialised or not, immediately.
            return self.sio.get_output(value, self.data_format) if serialize else value

        else:
            out = self.sio.get_output(value, self.data_format) if serialize else value
            return out

# ################################################################################################################################

    def __iter__(self):
        return iter(self.user_attrs_list if self.output_repeated else self.user_attrs_dict)

    def __setitem__(self, key, value):

        if isinstance(key, slice):
            self.user_attrs_list[key.start:key.stop] = value
            self.output_repeated = True
        else:
            setattr(self, key, value)

    def __setattr__(self, key, value):

        # Special-case Zato's own internal attributes
        if key == 'zato_meta':
            self.zato_meta = value
        else:
            self.user_attrs_dict[key] = value

    def __getattr__(self, key):
        try:
            return self.user_attrs_dict[key]
        except KeyError:
            raise KeyError('No such key `{}` among `{}` ({})'.format(key, self.user_attrs_dict, hex(id(self.user_attrs_dict))))

    def append(self, value):
        self.user_attrs_list.append(value)
        self.output_repeated = True

# ################################################################################################################################
# ################################################################################################################################
