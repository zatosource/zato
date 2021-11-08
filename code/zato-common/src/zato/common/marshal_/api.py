# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST
from inspect import isclass
from typing import _GenericAlias, List as list_

# typing-utils
from typing_utils import issubtype

# Zato
from zato.common.api import ZatoNotGiven
from zato.common.ext.dataclasses import _FIELDS, MISSING, _PARAMS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from dataclasses import Field
    from zato.server.service import Service

    Field = Field
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

class Model:
    after_created = None

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
    def __init__(self, elem_path, parent_list, field, value):
        # type: (list, list, Field, object)
        self.elem_path   = elem_path
        self.parent_list = parent_list
        self.field       = field
        self.value       = value
        self.reason = self.msg = self.get_reason()
        self.status = BAD_REQUEST

# ################################################################################################################################

    def get_reason(self):
        raise NotImplementedError()

# ################################################################################################################################
# ################################################################################################################################

class ElementMissing(ModelValidationError):

    def __repr__(self):
        return '<{} at {} -> {}>'.format(self.__class__.__name__, hex(id(self)), self.reason)

    __str__ = __repr__

# ################################################################################################################################

    def get_reason(self):
        return 'Element missing: {}'.format(self.elem_path)

# ################################################################################################################################
# ################################################################################################################################

class MarshalAPI:

    def __init__(self):
        self._field_cache = {}

# ################################################################################################################################

    def get_validation_error(self, field, value, parent_list, list_depth=None):
        # type: (Field, object, list, int) -> ModelValidationError

        # This needs to be empty if field is a top-level element
        parent_to_elem_sep = '/' if parent_list else ''
        list_depth_sep = '[{}]'.format(list_depth) if list_depth is not None else ''

        print()
        print(111, field)
        print(222, value)
        print(333, parent_list)
        print(444, list_depth)
        print()

        parent_path = '/' + '/'.join(parent_list)
        elem_path   = parent_path + list_depth_sep + parent_to_elem_sep + field.name

        return ElementMissing(elem_path, parent_list, field, value)

# ################################################################################################################################

    def _visit_list(self, list_, service, data, DataClass, parent_list):
        # type: (list, Service, dict, object, list) -> list

        # Respone to produce
        out = []

        # Visit each element in the list ..
        for idx, elem in enumerate(list_):

            # .. convert it to a model instance ..
            instance = self.from_dict(service, elem, DataClass, parent_list, list_depth=idx)

            # .. and append it for our caller ..
            out.append(instance)

        # .. finally, return the response.
        return out

# ################################################################################################################################

    def from_dict(self, service, data, DataClass, parent_list=None, extra=None, list_depth=None):
        # type: (Service, dict, object, list, dict, int) -> object

        # This will be None the first time around
        parent_list = parent_list or []

        # Whether the dataclass defines the __init__method
        has_init = getattr(DataClass, _PARAMS).init

        # This will be populated with parameters to the dataclass's __init__ method, assuming that the class has one.
        init_attrs = {}

        # This will be populated with parameters to be set via setattr, in case the class does not have __init__.
        setattr_attrs = {}

        # We can check it once upfront here
        attrs_container = init_attrs if has_init else setattr_attrs

        fields = getattr(DataClass, _FIELDS) # type: dict

        for _ignored_name, field in sorted(fields.items()): # type: (str, Field)

            # Local aliases
            is_class = isclass(field.type)

            # Is this particular field a further dataclass-based model?
            is_model = is_class and issubclass(field.type, Model)

            # Is this field a list that we can recurse into as well?
            is_list = isinstance(field.type, _GenericAlias) or (is_class and issubtype(field.type, list))

            # Get the value given on input
            value = data.get(field.name, ZatoNotGiven)

            # This field points to a model ..
            if is_model:

                # .. first, we need a dict as value as it is the only container possible for nested values ..
                if not isinstance(value, dict):
                    raise self.get_validation_error(field, value, parent_list, list_depth=list_depth)

                # .. if we are here, it means that we can recurse into the nested data structure.
                else:

                    # Note that we do not pass extra data on to nested models because we can only ever
                    # overwrite top-level elements with what extra contains.
                    parent_list.append(field.name)
                    value = self.from_dict(service, value, field.type, parent_list=parent_list,
                        extra=None, list_depth=list_depth)

            elif is_list:

                #
                # This is a list and we need to check if its definition
                # contains information about the actual type of elements inside.
                #
                # If it does, we will be extracting that particular type.
                # Otherwise, we will just pass this list on as it is.
                #

                # By default, assume we have no type information (we do not know what model class it is)
                model_class = None

                # Access the list's arguments ..
                type_args = getattr(field.type, '__args__', None)

                # .. if there are any ..
                if type_args:

                    # .. the first one will be our model class.
                    model_class = type_args[0]

                print()
                print(111, field)
                #print(222, issubclass(field.type, list))
                print(333, field.type)
                print(444, dir(field.type))
                #print(555, field.type.__args__)
                print(666, model_class)
                print(777, value)
                print()

                # If we have a model class the elements of the list are of
                # we need to visit each one of them now.
                if model_class:
                    if value:
                        value = self._visit_list(value, service, data, model_class,
                            parent_list=[field.name])

            # If we do not have a value yet, perhaps we will find a default one
            if value == ZatoNotGiven:
                if field.default and field.default is not MISSING:
                    value = field.default

            # Let's check if found any value
            if value != ZatoNotGiven:
                attrs_container[field.name] = value
            else:
                raise self.get_validation_error(field, value, parent_list, list_depth=list_depth)

            # If we have any extra elements, we need to add them as well
            if extra:
                for param, value in extra.items():
                    if param not in attrs_container:
                        attrs_container[param] = value

        # Create a new instance, potentially with attributes ..
        instance = DataClass(**init_attrs) # type: Model

        # .. and add extra ones in case __init__ was not defined ..
        for k, v in setattr_attrs.items():
            setattr(instance, k, v)

        # .. run the post-creation hook ..
        if instance.after_created:

            ctx = ModelCtx()
            ctx.service = service
            ctx.data = data
            ctx.DataClass = DataClass

            instance.after_created(ctx)

        # .. and return the new dataclass to our caller.
        return instance

    def to_dict(self):
        pass

# ################################################################################################################################
# ################################################################################################################################
