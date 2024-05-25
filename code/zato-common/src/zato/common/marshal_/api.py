# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import asdict, _FIELDS, make_dataclass, MISSING, _PARAMS # type: ignore
from http.client import BAD_REQUEST
from inspect import isclass
from typing import Any

try:
    from typing import _GenericAlias as _ListBaseClass # type: ignore
except ImportError:
    class _Sentinel:
        pass
    _ListBaseClass = _Sentinel

# BSON (MongoDB)
from bson import ObjectId

# dateutil
from dateutil.parser import parse as dt_parse

# orjson
from orjson import dumps

# SQLAlchemy
from sqlalchemy.sql.schema import Table

# typing-utils
from typing_utils import issubtype

# Zato
from zato.common.api import ZatoNotGiven
from zato.common.marshal_.model import BaseModel
from zato.common.typing_ import cast_, date_, datetime_, datetimez, extract_from_union, isotimestamp, is_union, type_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from dataclasses import Field
    from zato.common.typing_ import any_, anydict, anylist, boolnone, dictnone, intnone, optional, tuplist
    from zato.server.base.parallel import ParallelServer
    from zato.server.service import Service

    Field = Field
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

_None_Type = type(None)

# ################################################################################################################################
# ################################################################################################################################

def is_list(field_type:'Field', is_class:'bool') -> 'bool':

    # Using str is the only reliable method
    if 'typing.Union' in str(field_type):
        type_to_check = field_type.__args__[0] # type: ignore
    else:
        type_to_check = field_type

    # This will exist if input is, for instance abc = type_[Service]
    # Again, this is the only reliable way to check it.
    is_type = 'typing.Type' in str(type_to_check)

    # If it is a type object, we know it cannot be a list so we can return here.
    if is_type:
        return False

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

def extract_model_class(field_type:'Field') -> 'Model | None':

    # The attribute is defined by typing.List but not by list elements,
    # hence the getattr call ..
    type_args = getattr(field_type, '__args__', None)

    # .. if there are any arguments found ..
    if type_args:

        # .. the first one will be our model class.
        return type_args[0]

# ################################################################################################################################
# ################################################################################################################################

class Model(BaseModel):
    __name__: 'str'
    after_created = None

    def __getitem__(self, name, default=None):
        if not isinstance(name, str):
            name = str(name)
        return getattr(self, name, default)

    def __contains__(self, name):
        return hasattr(self, name)

    def get(self, name):
        return self.__getitem__(name)

    @classmethod
    def zato_get_fields(class_:'any_') -> 'anydict':
        fields = getattr(class_, _FIELDS) # type: anydict
        return fields

    @classmethod
    def _zato_from_dict(class_, data, extra=None):
        api = MarshalAPI()
        return api.from_dict(cast_('Service', None), data, class_, extra=extra)

    from_dict = _zato_from_dict

    def to_dict(self):
        return asdict(self)

    def _json_default_serializer(self, value):

        # Serialize BSON / MongoDB objects
        if isinstance(value, ObjectId):
            return str(value)

        elif isinstance(value, bytes):
            return value.decode('utf8')

        # We do not know how to serialize it
        return value

    def to_json(self, default=None, impl_extra=0):
        return dumps(self, default=default or self._json_default_serializer, option=impl_extra)

    def clone(self) -> 'any_':
        data = self.to_dict()
        out = self.__class__._zato_from_dict(None, data)
        return out

    @staticmethod
    def build_model_from_flat_input(
        server,            # type: ParallelServer
        sio_server_config, # type: ignore
        _CySimpleIO,       # type: ignore
        name,  # type: str
        input, # type: str | tuplist
    ) -> 'type_[BaseModel]':

        # Local imports
        from zato.simpleio import is_sio_bool, is_sio_int

        # Local aliases
        model_fields = []

        # Make sure this is a list-like container ..
        if isinstance(input, str):
            input = [input]

        # .. build an actual SIO handler ..
        _cy_simple_io = _CySimpleIO(server, sio_server_config, input) # type: ignore

        # .. now, go through everything we have on input ..
        for item in input:

            # .. find out if this is a required element or not ..
            is_optional = item.startswith('-')
            is_required = not is_optional

            # .. turn each element input into a Cython-based one ..
            sio_elem = _cy_simple_io.convert_to_elem_instance(item, is_required) # type: ignore

            # .. check if it is not a string ..
            is_int:'bool'  = is_sio_int(sio_elem)
            is_bool:'bool' = is_sio_bool(sio_elem)

            # .. turn the type into a model-compatible name ..
            if is_int:
                _model_type = int
            elif is_bool:
                _model_type = bool
            else:
                _model_type = str

            # .. append a model-compatible definition of this field for later use ..
            model_fields.append((sio_elem.name, _model_type))

        model = make_dataclass(name, model_fields, bases=(Model,))
        return model # type: ignore

# ################################################################################################################################
# ################################################################################################################################

class ModelCtx:
    service: 'Service'
    data: 'anydict | Model'
    DataClass: 'any_'

# ################################################################################################################################
# ################################################################################################################################

class ModelValidationError(Exception):
    """ Base class for model validation errors.
    """
    def __init__(self, elem_path:'str'):
        self.elem_path   = elem_path
        self.reason = self.msg = self.get_reason()
        self.status = BAD_REQUEST
        self.needs_msg = True # Added for compatibility with BadRequest as used in channel.py:dispatch

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

class ElementIsNotAList(ElementMissing):

    def get_reason(self):
        return 'Element is not a list: {}'.format(self.elem_path)

# ################################################################################################################################
# ################################################################################################################################

class DictCtx:
    def __init__(
        self,
        service:      'Service',
        current_dict: 'anydict | Model',
        DataClass:    'any_',
        extra:        'dictnone',
        list_idx:     'intnone',
        parent:       'optional[FieldCtx]' = None
        ) -> 'None':

        # We get these on input ..
        self.service      = service
        self.current_dict = current_dict
        self.extra        = extra
        self.DataClass    = DataClass
        self.list_idx     = list_idx
        self.parent       = parent

        # .. while these we need to build ourselves in self.init.
        self.has_init = None # type: boolnone

        # These are the Field object that we expect this dict will contain,
        # i.e. it will be possible to map ourselves to these Field objects.
        self.fields = None # type: dictnone

        # This will be populated with parameters to the dataclass's __init__ method, assuming that the class has one.
        self.init_attrs = {}

        # This will be populated with parameters to be set via setattr, in case the class does not have __init__.
        self.setattr_attrs = {}

        # We can check it once upfront and make it point to either init_attrs or setattr_attrs
        self.attrs_container = cast_('dict', None) # type: dictnone

# ################################################################################################################################

    def init(self):

        # Whether the dataclass defines the __init__method
        dataclass_params = getattr(self.DataClass, _PARAMS, None)
        self.has_init = dataclass_params.init if dataclass_params else False

        self.attrs_container = self.init_attrs if self.has_init else self.setattr_attrs
        self.fields = getattr(self.DataClass, _FIELDS) # type: dictnone

# ################################################################################################################################
# ################################################################################################################################

class FieldCtx:
    def __init__(self, dict_ctx, field, parent):
        # type: (DictCtx, Field, optional[FieldCtx]) -> None

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
        self.value    = None # type: any_
        self.is_class = None # type: boolnone
        self.is_list  = None # type: boolnone
        self.is_required = None # type: boolnone

        # This indicates if ourselves, we are a Model instance
        self.is_model = None # type: boolnone

        # This indicates whether we are a list that contains a Model instance.
        # The value is based on whether self.model_class exists or not
        # and whether self.is_model points to a Model rather than, for instance, the str class,
        # as the latter is possible in strlist definitions.
        self.contains_model = False

        # We set this flag to True only if there is some extra data that we have
        # and if we are a top-level element, as indicated by the lack of parent.
        self.has_extra = self.dict_ctx.extra and (not self.dict_ctx.parent)

# ################################################################################################################################

    def init(self):

        # Assume that we do not have any value
        value = ZatoNotGiven

        # If we have extra data, that will take priority over our regular dict, which is why we check it first here.
        if self.has_extra:
            if self.dict_ctx.extra:
                value = self.dict_ctx.extra.get(self.name, ZatoNotGiven)

        # If we do not have a value here, it means that we have no extra,
        # or that it did not contain the expected value so we look it up in the current dictionary.
        if value == ZatoNotGiven:
            if isinstance(self.dict_ctx.current_dict, dict):
                value = self.dict_ctx.current_dict.get(self.name, ZatoNotGiven)
            elif isinstance(self.dict_ctx.current_dict, Model): # type: ignore
                value = getattr(self.dict_ctx.current_dict, self.name, ZatoNotGiven)

        # We do not handle SQLAlchemy Table objects
        is_table = isinstance(value, Table)

        # If this field has a value, we can try to parse it into a specific type ..
        if (not is_table) and value and (value != ZatoNotGiven):

            try:
                # .. as an integer ..
                if self.field_type is int:
                    if not isinstance(value, int):
                        value = int(value)

                if self.field_type is date_:
                    if not isinstance(value, date_):
                        value = dt_parse(value).date() # type: ignore

                # .. as a datetime object ..
                elif self.field_type in (datetime_, datetimez):
                    if not isinstance(value, (date_, datetime_, datetimez)):
                        _is_datetimez = self.field_type is datetimez
                        value = dt_parse(value) # type: ignore
                        if _is_datetimez:
                            value = datetimez(
                                year=value.year,
                                month=value.month,
                                day=value.day,
                                hour=value.hour,
                                minute=value.minute,
                                second=value.second,
                                microsecond=value.microsecond,
                                tzinfo=value.tzinfo,
                                fold=value.fold,
                            )

                # .. as a datetime object formatted as string ..
                elif self.field_type is isotimestamp:
                    if isinstance(value, str):
                        value = dt_parse(value) # type: ignore
                        value = value.isoformat()

            except Exception as e:
                msg = f'Value `{repr(value)}` of field {self.name} could not be parsed -> {e} -> {self.dict_ctx.current_dict}'
                raise Exception(msg)

        # At this point, we know there will be something to assign although it still may be ZatoNotGiven.
        self.value = value

        self.is_class = isclass(self.field.type)
        self.is_model = self.is_class and issubclass(self.field.type, Model)
        self.is_list = is_list(self.field.type, self.is_class) # type: ignore

        #
        # This is a list and we need to check if its definition
        # contains information about the actual type of elements inside.
        #
        # If it does, in runtime, we will be extracting that particular type.
        # Otherwise, we will just pass this list on as it is.
        #
        if self.is_list:
            self.model_class = extract_model_class(self.field.type) # type: ignore
            self.contains_model = bool(self.model_class and hasattr(self.model_class, _FIELDS))

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

    def get_validation_error(
        self,
        field_ctx,                 # type: FieldCtx
        error_class=ElementMissing # type: any_
    ) -> 'ModelValidationError':

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

        return error_class(elem_path)

# ################################################################################################################################

    def _self_require_dict_or_model(self, field_ctx:'FieldCtx') -> 'None':
        if not isinstance(field_ctx.value, (dict, BaseModel)):
            raise self.get_validation_error(field_ctx)

# ################################################################################################################################

    def _visit_list(self, field_ctx:'FieldCtx') -> 'anylist':

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
        return out # type: ignore

# ################################################################################################################################

    def from_field_ctx(self, field_ctx:'FieldCtx') -> 'any_':
        return self.from_dict(field_ctx.dict_ctx.service, field_ctx.value, field_ctx.field.type,
            extra=None, list_idx=field_ctx.dict_ctx.list_idx, parent=field_ctx)

# ################################################################################################################################

    def _ensure_value_is_a_list(self, field_ctx:'FieldCtx', value:'any_') -> 'None':
        if not isinstance(value, list):
            raise self.get_validation_error(field_ctx, error_class=ElementIsNotAList)

# ################################################################################################################################

    def from_dict(
        self,
        service:      'Service',
        current_dict: 'anydict | BaseModel',
        DataClass:    'any_',
        extra:        'dictnone' = None,
        list_idx:     'intnone'  = None,
        parent:       'optional[FieldCtx]' = None
        ) -> 'any_':

        dict_ctx = DictCtx(service, current_dict, DataClass, extra, list_idx, parent)
        dict_ctx.init()

        # All fields that we will visit
        field_items = sorted(dict_ctx.fields.items()) # type: any_

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
                self._self_require_dict_or_model(field_ctx)

                # .. if we are here, it means that we can check the dict and extract its fields,
                # but note that we do not pass extra data on to nested models
                # because we can only ever overwrite top-level elements with what extra contains.
                field_ctx.value = self.from_field_ctx(field_ctx)

            # .. if this field points to a list ..
            elif field_ctx.is_list:

                # If we have a model class the elements of the list are of,
                # we need to visit each of them now.
                if field_ctx.model_class:

                    # Enter further only if we have any value at all to check ..
                    if field_ctx.value and field_ctx.value != ZatoNotGiven: # type: ignore

                        # .. if the field is required, make sure that what we have on input really is a list object ..
                        if field_ctx.is_required:
                            self._ensure_value_is_a_list(field_ctx, field_ctx.value)

                        # However, that model class may actually point to <type 'str'> types
                        # in case of fields like strlist, and we need to take that into account
                        # before entering the _visit_list method below.
                        if field_ctx.is_model or field_ctx.contains_model:
                            field_ctx.value = self._visit_list(field_ctx)

                    # .. if we are here, it may be because the value is a dictlist instance
                    # .. for which there will be no underlying model and we can just assign it as is ..
                    else:

                        #
                        # Object current_field may be returned by a default factory
                        # in declarations, such as the one below. This is why we need to
                        # ensure that this name exist in current_dict before we extract its value.
                        #
                        #
                        # @dataclass(init=False, repr=False)
                        # class MyModel(Model):
                        #     my_list: anylistnone = list_field()
                        #     my_dict: anydictnone = dict_field()
                        #
                        if field_ctx.name in current_dict:

                            # .. extract the value first ..
                            value = current_dict[field_ctx.name]

                            # .. if the field is required, make sure that what we have on input really is a list object ..
                            if field_ctx.is_required:
                                self._ensure_value_is_a_list(field_ctx, value)

                            # .. assign the list now.
                            field_ctx.value = value

            # If we do not have a value yet, perhaps we will find a default one
            if field_ctx.value == ZatoNotGiven:

                default = field_ctx.field.default
                default_factory = field_ctx.field.default_factory

                if default is not MISSING:
                    field_ctx.value = default

                elif default_factory and default_factory is not MISSING:
                    field_ctx.value = default_factory()

            # Let's check if we found any value
            if field_ctx.value != ZatoNotGiven:
                value = field_ctx.value
            else:
                if field_ctx.is_required:
                    raise self.get_validation_error(field_ctx)
                else:
                    # This is the most reliable way
                    if 'typing.List' in str(field_ctx.field_type):
                        value = []
                    elif field_ctx.field_type is Any:
                        value = None
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
            dict_ctx.attrs_container[field_ctx.name] = value # type: ignore

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

    def unmarshall(self, data:'dict', class_:'any_') -> 'any_':
        """ A publicly available convenience method to unmarshall arbitrary dicts into model classes.
        """
        return self.from_dict(cast_('Service', None), data, class_)

# ################################################################################################################################
# ################################################################################################################################
