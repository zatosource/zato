# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import ZatoNotGiven
from zato.common.ext.dataclasses import _FIELDS, _PARAMS

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

# ################################################################################################################################
# ################################################################################################################################

class ElementMissing(ModelValidationError):

    def __repr__(self):
        return 'Element missing: {}'.format(self.elem_path)

    __str__ = __repr__

# ################################################################################################################################
# ################################################################################################################################

class MarshalAPI:

    def __init__(self):
        self._field_cache = {}

# ################################################################################################################################

    def get_validation_error(self, field, value, parent_list):
        # type: (Field, object, list) -> ModelValidationError

        parent_path = '/' + '/'.join(parent_list)
        elem_path   = parent_path + field.name

        return ElementMissing(elem_path, parent_list, field, value)

# ################################################################################################################################

    def from_dict(self, service, data, DataClass, parent_list=None, extra=None):
        # type: (Service, dict, object, list, dict)

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

        for field in fields.values(): # type: Field

            # Is this particular field a further dataclass-based model?
            is_model = issubclass(field.type, Model)

            # Get the value given on input
            value = data.get(field.name, ZatoNotGiven)

            # This field points to a model ..
            if is_model:

                # .. first, we need a dict as value as it is the only container possible for nested values ..
                if not isinstance(value, dict):
                    raise self.get_validation_error(field, value, parent_list)

                # .. if we are here, it means that we can recurse into the nested data structure.
                else:

                    # Note that we do not pass extra data on to nested models because we can only ever
                    # overwrite top-level elements with what extra contains.
                    parent_list.append(field.name)
                    value = self.from_dict(service, value, field.type, parent_list=parent_list, extra=None)

            # Add the computed value for later use
            if value != ZatoNotGiven:
                attrs_container[field.name] = value

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
