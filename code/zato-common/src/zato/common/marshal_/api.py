# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST
from inspect import isclass

try:
    from typing import _GenericAlias as _ListBaseClass
except ImportError:
    class _Sentinel:
        pass
    _ListBaseClass = _Sentinel

# orjson
from orjson import dumps

# typing-utils
from typing_utils import issubtype

# Zato
from zato.common.api import ZatoNotGiven
from zato.common.ext.dataclasses import asdict, _FIELDS, MISSING, _PARAMS
from zato.common.typing_ import extract_from_union, is_union

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from dataclasses import Field
    from zato.common.typing_ import any_, anydict
    from zato.server.service import Service

    Field = Field
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

_None_Type = type(None)

# ################################################################################################################################
# ################################################################################################################################

def is_list(field_type, is_class):
    # type: (Field, bool) -> bool

    # Using str is the only reliable method
    if 'typing.Union' in str(field_type):
        type_to_check = field_type.__args__[0] # type: ignore
    else:
        type_to_check = field_type

    is_list_base_class_instance = isinstance(type_to_check, _ListBaseClass)
    is_list_sub_type = issubtype(type_to_check, list) # type: ignore

    if is_list_base_class_instance:
        result = True
    elif (is_class and is_list_sub_type):
        result = True
    else:
        result = False

    return result

# ################################################################################################################################
# ################################################################################################################################

def extract_model_class(field_type):
    # type: (Field) -> Model

    # The attribute is defined by typing.List but not by list elements,
    # hence the getattr call ..
    type_args = getattr(field_type, '__args__', None)

    # .. if there are any arguments found ..
    if type_args:

        # .. the first one will be our model class.
        return type_args[0]

# ################################################################################################################################
# ################################################################################################################################

class Model:
    __name__: 'str'
    after_created = None

    def __getitem__(self, name, default=None):
        return getattr(self, name, default)

    @classmethod
    def zato_get_fields(class_:'any_') -> 'anydict':
        fields = getattr(class_, _FIELDS) # type: anydict
        return fields

    @classmethod
    def _zato_from_dict(class_, data):
        api = MarshalAPI()
        return api.from_dict(None, data, class_)

    def to_dict(self):
        return asdict(self)

    def to_json(self, default=None, impl_extra=0):
        return dumps(self, default=default, option=impl_extra)

# ################################################################################################################################
# ################################################################################################################################

class ModelCtx:
    def __init__(self):
        self.service = None   # type: Service
        self.data = None      # type: dict
        self.DataClass = None # type: object

# ################################################################################################################################
# ################################################################################################################################

class ModelValidationError(Exception):
    """ Base class for model validation errors.
    """
    def __init__(self, elem_path):
        # type: (str)
        self.elem_path   = elem_path
        self.reason = self.msg = self.get_reason()
        self.status = BAD_REQUEST
        self.needs_msg = False # Added for compatibility with BadRequest as used in channel.py:dispathc

# ################################################################################################################################

    def get_reason(self):
        raise NotImplementedError()

# ################################################################################################################################
# ################################################################################################################################

class ElementMissing(ModelValidationError):

    def __repr__(self):
        return '<{} at {} -> {}>'.format(self.__class__.__name__, hex(id(self)), self.reason)

    __str__ = __repr__

    def get_reason(self):
        return 'Element missing: {}'.format(self.elem_path)

# ################################################################################################################################
# ################################################################################################################################

class DictCtx:
    def __init__(self, service, current_dict, DataClass, list_idx):
        # type: (Service, dict, object, int) -> None

        # We get these on input ..
        self.service      = service
        self.current_dict = current_dict
        self.DataClass    = DataClass
        self.list_idx     = list_idx

        # .. while these we need to build ourselves in self.init.
        self.has_init = None # type: bool

        # These are the Field object that we expect this dict will contain,
        # i.e. it will be possible to map ourselves to these Field objects.
        self.fields = None # type: dict

        # This will be populated with parameters to the dataclass's __init__ method, assuming that the class has one.
        self.init_attrs = {}

        # This will be populated with parameters to be set via setattr, in case the class does not have __init__.
        self.setattr_attrs = {}

        # We can check it once upfront and make it point to either init_attrs or setattr_attrs
        self.attrs_container = None # type: dict

# ################################################################################################################################

    def init(self):

        # Whether the dataclass defines the __init__method
        #params = getattr(self.DataClass, _PARAMS, None)
        #if params:
        #    self.has_init = params.init
        #else:
        #    self.has_init = False

        self.has_init = getattr(self.DataClass, _PARAMS).init

        self.attrs_container = self.init_attrs if self.has_init else self.setattr_attrs
        self.fields = getattr(self.DataClass, _FIELDS) # type: dict

# ################################################################################################################################
# ################################################################################################################################

class FieldCtx:
    def __init__(self, dict_ctx, field, parent):
        # type: (DictCtx, Field, FieldCtx) -> None

        # We get these on input ..
        self.dict_ctx   = dict_ctx
        self.field      = field
        self.parent     = parent
        self.name       = self.field.name # type: str

        # This will be the same as self.field.type unless self.field.type is a union (e.g. optional[str]).
        # In this case, self.field_type will be str whereas self.field.type will be the original type.
        self.field_type = None # type: object

        # .. by default, assume we have no type information (we do not know what model class it is)
        self.model_class = None # type: object

        # .. while these we need to build ourselves in self.init ..
        self.value    = None # type: object
        self.is_class = None # type: bool
        self.is_model = None # type: bool
        self.is_list  = None # type: bool
        self.is_required = None # type: bool

# ################################################################################################################################

    def init(self):

        self.value = self.dict_ctx.current_dict.get(self.name, ZatoNotGiven)
        self.is_class = isclass(self.field.type)
        self.is_model = self.is_class and issubclass(self.field.type, Model)
        self.is_list = is_list(self.field.type, self.is_class)

        #
        # This is a list and we need to check if its definition
        # contains information about the actual type of elements inside.
        #
        # If it does, in runtime, we will be extracting that particular type.
        # Otherwise, we will just pass this list on as it is.
        #
        if self.is_list:
            self.model_class = extract_model_class(self.field.type)

# ################################################################################################################################

    def get_name(self):
        if self.dict_ctx.list_idx is not None:
            return '{}[{}]'.format(self.name, self.dict_ctx.list_idx)
        else:
            return self.name

# ################################################################################################################################
# ################################################################################################################################

class MarshalAPI:

    def __init__(self):
        self._field_cache = {}

# ################################################################################################################################

    def get_validation_error(self, field_ctx):
        # type: (FieldCtx) -> ModelValidationError

        # This will always exist
        elem_path = [field_ctx.name]

        # Keep checking parent fields as long as they exist
        while field_ctx.parent:
            elem_path.append(field_ctx.parent.get_name())
            field_ctx = field_ctx.parent

        # We need to reverse it now to present a top-down view
        elem_path = reversed(elem_path)

        # Now, join it with a elem_path separator
        elem_path = '/' + '/'.join(elem_path)

        return ElementMissing(elem_path)

# ################################################################################################################################

    def _self_require_dict(self, field_ctx):
        # type: (FieldCtx) -> None
        if not isinstance(field_ctx.value, dict):
            raise self.get_validation_error(field_ctx)

# ################################################################################################################################

    def _visit_list(self, field_ctx):
        # type: (FieldCtx) -> list

        # Local aliases
        service     = field_ctx.dict_ctx.service
        model_class = field_ctx.model_class

        # Respone to produce
        out = []

        # Visit each element in the list ..
        for idx, elem in enumerate(field_ctx.value):

            if field_ctx.is_list:
                field_ctx.dict_ctx.list_idx = idx

            # .. convert it to a model instance ..
            instance = self.from_dict(service, elem, model_class, list_idx=idx, parent=field_ctx)

            # .. and append it for our caller ..
            out.append(instance)

        # .. finally, return the response.
        return out

# ################################################################################################################################

    def from_field_ctx(self, field_ctx):
        # type: (FieldCtx) -> object
        return self.from_dict(field_ctx.dict_ctx.service, field_ctx.value, field_ctx.field.type,
            extra=None, list_idx=field_ctx.dict_ctx.list_idx, parent=field_ctx)

# ################################################################################################################################

    def from_dict(self, service, current_dict, DataClass, extra=None, list_idx=None, parent=None):
        # type: (Service, dict, object, list, dict, int) -> any_

        dict_ctx = DictCtx(service, current_dict, DataClass, list_idx)
        dict_ctx.init()

        # All fields that we will visit
        field_items = sorted(dict_ctx.fields.items()) # type: (str, Field)

        for _ignored_name, _field in field_items:

            # Assume we are required ..
            is_required = True

            # Use this by default ..
            field_type = _field.type

            # .. unless it is a union with None = this field is really optional[type_]
            if is_union(_field.type):
                result = extract_from_union(_field.type)
                _, field_type, union_with = result

                # .. check if this was an optional field.
                is_required = not (union_with is _None_Type)

            # Represents a current field in the model in the context of the input dict ..
            field_ctx = FieldCtx(dict_ctx, _field, parent)
            field_ctx.is_required = is_required
            field_ctx.field_type = field_type

            # .. this call will populate the initial value of the field as well (field_ctx..
            field_ctx.init()

            # If this field points to a model ..
            if field_ctx.is_model:

                # .. first, we need a dict as value as it is the only container that we can extract model fields from ..
                self._self_require_dict(field_ctx)

                # .. if we are here, it means that we can check the dict and extract its fields,
                # but note that we do not pass extra data on to nested models
                # because we can only ever overwrite top-level elements with what extra contains.
                field_ctx.value = self.from_field_ctx(field_ctx)

            # .. if this field points to a list ..
            elif field_ctx.is_list:

                # If we have a model class the elements of the list are of
                # we need to visit each of them now.
                if field_ctx.model_class:

                    if field_ctx.value and field_ctx.value != ZatoNotGiven:
                        if field_ctx.is_model:
                            field_ctx.value = self._visit_list(field_ctx)

            # If we do not have a value yet, perhaps we will find a default one
            if field_ctx.value == ZatoNotGiven:
                if field_ctx.field.default and field_ctx.field.default is not MISSING:
                    field_ctx.value = field_ctx.field.default

            # Let's check if found any value
            if field_ctx.value != ZatoNotGiven:
                value = field_ctx.value
            else:
                if field_ctx.is_required:
                    raise self.get_validation_error(field_ctx)
                else:
                    # This is most reliable
                    if 'typing.List' in str(field_ctx.field_type):
                        value = []
                    elif issubclass(field_ctx.field_type, str):
                        value = ''
                    elif issubclass(field_ctx.field_type, int):
                        value = 0
                    elif issubclass(field_ctx.field_type, list):
                        value = []
                    elif issubclass(field_ctx.field_type, dict):
                        value = {}
                    elif issubclass(field_ctx.field_type, float):
                        value = 0.0
                    else:
                        value = None

            # Assign the value now
            dict_ctx.attrs_container[field_ctx.name] = value

            # If we have any extra elements, we need to add them as well
            if extra:
                for param, value in extra.items():
                    if param not in dict_ctx.attrs_container:
                        dict_ctx.attrs_container[param] = value

        # Create a new instance, potentially with attributes ..
        instance = DataClass(**dict_ctx.init_attrs) # type: Model

        # .. and add extra ones in case __init__ was not defined ..
        for k, v in dict_ctx.setattr_attrs.items():
            setattr(instance, k, v)

        # .. run the post-creation hook ..
        if instance.after_created:

            ctx = ModelCtx()
            ctx.service = service
            ctx.data = dict_ctx.current_dict
            ctx.DataClass = DataClass

            instance.after_created(ctx)

        # .. and return the new dataclass to our caller.
        return instance

# ################################################################################################################################
# ################################################################################################################################
