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

# SQLAlchemy
from sqlalchemy.util import KeyedTuple

# Zato
from zato.common.odb.api import WritableKeyedTuple

# Zato - Cython
from zato.cy.simpleio import SIODefinition

# Python 2/3 compatibility
from past.builtins import unicode as past_unicode

if 0:
    past_unicode = past_unicode

# ################################################################################################################################

logger = getLogger('zato')

# ################################################################################################################################

list_like:tuple = (list, tuple)

# ################################################################################################################################
# ################################################################################################################################

@cy.cclass
class SimpleIOPayload(object):
    """ Represents a payload, i.e. individual response elements, set via SimpleIO.
    """
    all_output_elem_names = cy.declare(list, visibility='public') # type: list

    cid         = cy.declare(str, visibility='public') # type: past_unicode
    data_format = cy.declare(str, visibility='public') # type: past_unicode

    # One of the two will be used to produce a response
    user_attrs_dict = cy.declare(dict, visibility='public') # type: dict
    user_attrs_list  = cy.declare(list, visibility='public') # type: list

    def __cinit__(self, all_output_elem_names:list, cid:str, data_format:str):
        self.all_output_elem_names = all_output_elem_names
        self.cid = cid
        self.data_format = data_format
        self.user_attrs_dict = {}
        self.user_attrs_list = []

    @cy.cfunc
    @cy.returns(dict)
    def _extract_payload_attrs(self, value:object) -> dict:
        """ Extract response attributes from a single object.
        """
        extracted:dict = {}
        # Now, check if this is a dict-like object
        if isinstance(value, dict):
            pass

        # .. or an SQL response-like object ..

        return extracted

    @cy.cfunc
    def _is_sqlalchemy(self, item:object):
        return hasattr(item, '_sa_class_manager')

    @cy.ccall
    def set_payload_attrs(self, value:object):
        """ Assigns user-defined attributes to what will eventually be a response.
        """
        # First, clear out what was potentially set earlier
        self.user_attrs_dict.clear()
        self.user_attrs_list.clear()

        # Check if this is something that can be explicitly serialised for our purposes
        if hasattr(value, 'to_zato'):
            value = value.to_zato()

        # Now, check if this is a dict or an SQL response-like object ..
        if isinstance(value, list_like):
            for item in value:
                self.user_attrs_list.append(self._extract_payload_attrs(item))
        else:
            self.user_attrs_dict.update(self._extract_payload_attrs(value))

        print()
        print(666, value)
        print(777, self.all_output_elem_names)
        print()

# ################################################################################################################################
# ################################################################################################################################
