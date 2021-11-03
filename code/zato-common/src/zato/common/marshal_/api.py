# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from zato.common.ext.dataclasses import dataclass
from dataclasses import _FIELDS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from dataclasses import Field

    Field = Field

# ################################################################################################################################
# ################################################################################################################################

def is_simple_type(value):
    return issubclass(value, (int, str, float))

# ################################################################################################################################
# ################################################################################################################################

class Model:
    pass

# ################################################################################################################################
# ################################################################################################################################

class MarshalAPI:

    def __init__(self):
        self._field_cache = {}

    def from_dict(self, data:dict, DataClass:object):

        # Whether the dataclass defines the __init__method
        has_init = DataClass.__dataclass_params__.init

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
            value = data.get(field.name)

            # If this is to be a model, we need a dict as value as it is the only container possible for nested values
            if is_model and (not isinstance(value, dict)):
                raise ValueError('Expected for `{}` to be a dict instead of `{}` ({})'.format(
                    field.name, value, value.__class__.__name__))

            print()
            print(111, field.name, field.type, field.init)
            print(222, )
            print(333, value)
            print()

            # Add the computed value for later use
            attrs_container[field.name] = value

        # Create a new instance, potentially with attributes ..
        instance = DataClass(**init_attrs)

        # .. and add extra ones in case __init__ was not defined.
        for k, v in setattr_attrs.items():
            setattr(instance, k, v)

        return instance

    def to_dict(self):
        pass

# ################################################################################################################################
# ################################################################################################################################
