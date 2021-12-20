# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass, field, Field, MISSING
from inspect import isclass
from operator import attrgetter

# Bunch
from bunch import Bunch

# Zato
from zato.common.typing_ import extract_from_union, is_union
from zato.common.marshal_.api import extract_model_class, is_list, Model

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    from zato.server.service import Service
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

_sio_attrs = (
    'input',
    'input_required',
    'input_optional',
    'output',
    'output_required',
    'output_optional',
)

_singleton = object()

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class FieldTypeInfo:
    field_type:      'any_'
    field_type_args: 'anylist'
    union_with:      'any_'

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

# ################################################################################################################################

    @staticmethod
    def get_field_type_info(field:'Field') -> 'FieldTypeInfo':

        field_type = field.type

        if is_union(field_type):
            result = extract_from_union(field_type)
            field_type_args, field_type, union_with = result
        else:
            field_type_args = []
            union_with = _singleton

        info = FieldTypeInfo()
        info.field_type = field_type
        info.field_type_args = field_type_args
        info.union_with = union_with

        return info

# ################################################################################################################################

    @staticmethod
    def from_python_field(field:'Field', api_spec_info:'Bunch') -> 'FieldInfo':

        if not field.type:
            raise ValueError('Value missing -> field.type ({})'.format(field))

        info = FieldInfo()
        info.name = field.name or '<field-no-name>'
        info.is_required = field.default is MISSING
        info.description = field.__doc__ or ''

        field_type_info = FieldInfo.get_field_type_info(field)
        field_type = field_type_info.field_type

        # If this was a union with a None type, it means that it was actually an optional field
        # because optional[Something] is equal to Union[Something, None], in which case
        # we set the is_required flag to None, no matter what was set earlier up.
        if field_type_info.union_with is type(None): # noqa: E721
            info.is_required = False

        is_class = isclass(field_type)

        if is_list(field_type, is_class):
            info.is_list = True
            ref = extract_model_class(field_type)

            if is_union(ref):
                result = extract_from_union(ref)
                _, field_type, _ = result
                ref = field_type

            info.ref = '#/components/schemas/{}.{}'.format(ref.__module__, ref.__name__)
            type_info = '', ref.__name__

        elif issubclass(field_type, bool):
            type_info = api_spec_info.BOOLEAN

        elif issubclass(field_type, int):
            type_info = api_spec_info.INTEGER

        elif issubclass(field_type, float):
            type_info = api_spec_info.FLOAT

        elif issubclass(field_type, Model):
            info.ref = '#/components/schemas/{}.{}'.format(field_type.__module__, field_type.__name__)
            type_info = '', field_type.__name__
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

@dataclass(init=False)
class Config:
    ns: 'str' = ''
    services: 'anylist' = field(default_factory=list)
    is_module_level: 'bool' = True

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class DocstringModel:

    full:      'str' = ''
    full_html: 'str' = ''

    summary:      'str' = ''
    summary_html: 'str' = ''

    description:      'str' = ''
    description_html: 'str' = ''

    # Keys are tags used, values are documentation for key
    by_tag: 'anydict' = field(default_factory=dict)
    tags:   'anylist' = field(default_factory=list)

# ################################################################################################################################
# ################################################################################################################################

class SimpleIO:
    """ Represents a SimpleIO definition of a particular service.
    """
    input:          'anylist'
    input_required: 'anylist'
    input_optional: 'anylist'

    output:          'anylist'
    output_required: 'anylist'
    output_optional: 'anylist'

    request_elem:   'any_'
    response_elem:  'any_'

    spec_name:      'str'
    description:    'SimpleIODescription'
    needs_sio_desc: 'bool'

    def __init__(
        self,
        spec_info,      # type: APISpecInfo
        description,    # type: SimpleIODescription
        needs_sio_desc, # type: bool
        ) -> 'None':

        self.input          = spec_info.field_list.get('input', [])
        self.input_required = []
        self.input_optional = []

        self.output          = spec_info.field_list.get('output', [])
        self.output_required = []
        self.output_optional = []

        self.request_elem   = spec_info.request_elem
        self.response_elem  = spec_info.response_elem

        self.spec_name      = spec_info.name
        self.description    = description
        self.needs_sio_desc = needs_sio_desc

# ################################################################################################################################

    def assign_required_optional(self) -> 'None':

        item: 'FieldInfo'

        for item in self.input:
            if item.is_required:
                self.input_required.append(item)
            else:
                self.input_optional.append(item)

        for item in self.output:
            if item.is_required:
                self.output_required.append(item)
            else:
                self.output_optional.append(item)

# ################################################################################################################################

    def sort_elems(self) -> 'None':
        self.input          = sorted(self.input,          key=attrgetter('name'))
        self.input_required = sorted(self.input_required, key=attrgetter('name'))
        self.input_optional = sorted(self.input_optional, key=attrgetter('name'))

        self.output          = sorted(self.output,          key=attrgetter('name'))
        self.output_required = sorted(self.output_required, key=attrgetter('name'))
        self.output_optional = sorted(self.output_optional, key=attrgetter('name'))

# ################################################################################################################################

    def to_bunch(self) -> 'Bunch':
        out = Bunch()
        for name in _sio_attrs + ('request_elem', 'response_elem', 'spec_name'):
            out[name] = getattr(self, name)

        if self.needs_sio_desc:
            out.description = self.description.to_bunch()

        return out

# ################################################################################################################################
# ################################################################################################################################

class SimpleIODescription:

    input:  'anydict'
    output: 'anydict'

    def __init__(self) -> 'None':
        self.input  = {}
        self.output = {}

# ################################################################################################################################

    def to_bunch(self) -> 'Bunch':
        out = Bunch()
        out.input  = self.input
        out.output = self.output

        return out

# ################################################################################################################################
# ################################################################################################################################
