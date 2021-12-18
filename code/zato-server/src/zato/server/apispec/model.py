# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass, Field, MISSING
from inspect import isclass

# Bunch
from bunch import Bunch

# Zato
from zato.common.api import APISPEC
from zato.common.marshal_.api import extract_model_class, is_list, Model

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist
    from zato.server.service import Service
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

_sio_attrs = (
    'input',
    'output'
)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class FieldInfo:
    name:        'str'
    type:        'str'  = ''
    subtype:     'str'  = ''
    is_required: 'bool' = False
    description: 'str'  = ''
    ref:         'str'  = ''
    is_list:     'bool' = False

    @staticmethod
    def from_python_field(field:'Field', api_spec_info:'Bunch') -> 'FieldInfo':

        if not field.type:
            raise ValueError('Value missing -> field.type ({})'.format(field))

        info = FieldInfo()
        info.name = field.name or '<field-no-name>'
        info.is_required = field.default is MISSING
        info.description = field.__doc__ or ''

        is_class = isclass(field.type)

        if is_list(field.type, is_class):
            type_info = '', ''
            ref = extract_model_class(field.type)
            info.is_list = True
            info.ref = '#/components/schemas/{}.{}'.format(ref.__module__, ref.__name__)

        elif issubclass(field.type, bool):
            type_info = api_spec_info.BOOLEAN

        elif issubclass(field.type, int):
            type_info = api_spec_info.INTEGER

        elif issubclass(field.type, float):
            type_info = api_spec_info.FLOAT

        elif issubclass(field.type, Model):
            type_info = '', ''
            info.ref = '#/components/schemas/{}.{}'.format(field.type.__module__, field.type.__name__)
        else:
            try:
                type_info = api_spec_info.map[field.__class__]
            except KeyError:
                type_info = api_spec_info.DEFAULT

        info.type, info.subtype = type_info

        return info

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class APISpecInfo:
    name: str
    field_list: 'anydict'
    request_elem: str
    response_elem: str

# ################################################################################################################################
# ################################################################################################################################

class Config:
    def __init__(self):
        self.is_module_level = True
        self.ns = ''
        self.services = []

# ################################################################################################################################
# ################################################################################################################################

class Docstring:
    __slots__ = 'summary', 'description', 'full', 'tags', 'by_tag'

    def __init__(self, tags:'anylist') -> 'None':
        self.summary = ''
        self.description = ''
        self.full = ''
        self.tags = tags
        self.by_tag = {} # Keys are tags used, values are documentation for key

# ################################################################################################################################
# ################################################################################################################################

class Namespace:

    name: str
    docs: str

    def __init__(self):
        self.name = APISPEC.NAMESPACE_NULL
        self.docs = ''

# ################################################################################################################################
# ################################################################################################################################

class SimpleIO:
    __slots__ = 'input', 'output', 'request_elem', 'response_elem', 'spec_name', 'description', 'needs_sio_desc'

    def __init__(
        self,
        api_spec_info,  # type: APISpecInfo
        description,    # type: SimpleIODescription
        needs_sio_desc, # type: bool
        ) -> 'None':

        self.input = api_spec_info.field_list.get('input', [])
        self.output = api_spec_info.field_list.get('output', [])
        self.request_elem = api_spec_info.request_elem
        self.response_elem = api_spec_info.response_elem
        self.spec_name = api_spec_info.name
        self.description = description
        self.needs_sio_desc = needs_sio_desc

# ################################################################################################################################

    def to_bunch(self):
        out = Bunch()
        for name in _sio_attrs + ('request_elem', 'response_elem', 'spec_name'):
            out[name] = getattr(self, name)

        if self.needs_sio_desc:
            out.description = self.description.to_bunch()

        return out

# ################################################################################################################################
# ################################################################################################################################

class SimpleIODescription:
    __slots__ = 'input', 'output'

    def __init__(self):
        self.input = {}
        self.output = {}

# ################################################################################################################################

    def to_bunch(self):
        out = Bunch()
        out.input = self.input
        out.output = self.output

        return out

# ################################################################################################################################
# ################################################################################################################################
