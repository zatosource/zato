# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST

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

    def get_validation_error(self, field, value, parent_list):
        # type: (Field, object, list) -> ModelValidationError

        # This needs to be empty if field is a top-level element
        parent_to_elem_sep = '/' if parent_list else ''

        parent_path = '/' + '/'.join(parent_list)
        elem_path   = parent_path + parent_to_elem_sep + field.name

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
            else:
                raise self.get_validation_error(field, value, parent_list)

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

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from shutil import copy as shutil_copy

# Zato
from api_model import MyRequest, User
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class MyService(Service):

    class SimpleIO:
        input = MyRequest

    def handle(self):

        # stdlib
        import gc
        import importlib
        from inspect import getmodule, getsourcefile

        my_class = MyRequest
        model_impl_name = '{}.{}'.format(my_class.__module__, my_class.__name__)

        # A set of Python objects, each representing a model class (rather than its name)
        model_classes = set()

        # All the modules to be reloaded due to changes to the data model
        to_auto_deploy = set()

        for item in gc.get_objects():

            if isinstance(item, type):
                item_impl_name = '{}.{}'.format(item.__module__, item.__name__)
                if item_impl_name == model_impl_name:
                    model_classes.add(item)

        for model_class in model_classes:
            for ref in gc.get_referrers(model_class):

                if isinstance(ref, dict):

                    print(111, type(ref))
                    print(222, sorted(ref))
                    print(333, ref.get('__file__'))
                    print()

                '''
                if isinstance(ref, dict):
                    mod_name = ref.get('__module__')
                    if mod_name:
                        to_auto_deploy.add(mod_name)
                '''

        zzz

        to_auto_deploy = sorted(to_auto_deploy)

        self.logger.warn('QQQ=1 %r', to_auto_deploy)
        self.logger.warn('QQQ=2 %r', model_classes)
        self.logger.warn('QQQ=3 %r', model_impl_name)

        # Inform users that we are to auto-redeploy services and why we are doing it
        self.logger.info('Model class `%s` changed; auto-redeploying `%s`', model_class, to_auto_deploy)

        # Go through each child service found and hot-deploy it
        for item in to_auto_deploy:

            mod = importlib.import_module(item)
            module_path = getsourcefile(mod)

            shutil_copy(module_path, self.server.hot_deploy_config.pickup_dir)

# ################################################################################################################################
# ################################################################################################################################
'''
