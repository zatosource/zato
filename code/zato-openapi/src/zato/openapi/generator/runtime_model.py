# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import dataclasses
import sys
from inspect import get_annotations

# Zato
from zato.openapi.generator.annotation import get_runtime_type, is_model_class, NameResolver
from zato.openapi.generator.basic_types import Basic_Types

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strlist, strset
    any_ = any_
    strlist = strlist
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

# The file path under which models read at runtime are listed
_runtime_file_path = 'runtime'

# ################################################################################################################################
# ################################################################################################################################

class ModuleNameResolver(NameResolver):
    """ Resolves the names in the annotations of a model against the module that the model is defined in,
    and reads each model that an annotation refers to into the models of the reader.
    """

    def __init__(self, namespace:'anydict', reader:'ModelReader') -> 'None':
        self.namespace = namespace
        self.reader = reader
        self.names_in_progress:'strset' = set()

# ################################################################################################################################

    def resolve(self, name:'str') -> 'any_':
        """ Returns the type that a name in an annotation of the model stands for.
        """
        # Names that the mapper knows stay as they are ..
        if name in Basic_Types:
            out = name

        # .. a name whose own value refers back to it stays as it is too ..
        elif name in self.names_in_progress:
            out = name

        # .. a name that the module defines at runtime is what its value stands for ..
        elif name in self.namespace:
            value = self.namespace[name]

            self.names_in_progress.add(name)
            out = get_runtime_type(value, self)
            self.names_in_progress.discard(name)

        # .. and a name that the module imports for type checkers only is resolved the default way.
        else:
            out = super().resolve(name)

        return out

# ################################################################################################################################

    def resolve_qualified(self, name_parts:'strlist') -> 'any_':
        """ Returns the type that a qualified name stands for, e.g. models.Customer, looking each part up
        in the module of the model and in the objects that the preceding parts stand for.
        """
        first_part = name_parts[0]

        # A name whose first part the module does not define is resolved the default way ..
        if first_part not in self.namespace:
            out = super().resolve_qualified(name_parts)
            return out

        # .. otherwise, each next part is an attribute of what the part before it stands for ..
        value = self.namespace[first_part]
        remaining_parts = name_parts[1:]

        for part in remaining_parts:
            if not hasattr(value, part):
                out = super().resolve_qualified(name_parts)
                return out
            value = getattr(value, part)

        # .. and the last one is the type that the whole name stands for.
        out = get_runtime_type(value, self)
        return out

# ################################################################################################################################

    def on_model(self, class_:'type') -> 'str':
        """ Reads a model that an annotation refers to and returns the name under which the mapper finds it.
        """
        self.reader.read(class_)

        out = class_.__name__
        return out

# ################################################################################################################################
# ################################################################################################################################

class ModelReader:
    """ Reads the fields of models at runtime into model definitions, together with the models that the fields refer to.
    """

    def __init__(self, all_models:'anydict', visited:'strset') -> 'None':
        self.all_models = all_models
        self.visited = visited

# ################################################################################################################################

    def get_resolver(self, class_:'type') -> 'ModuleNameResolver':
        """ Returns a resolver of the names in the annotations of a class, against the module that the class is defined in.
        """
        # Hot-deployed modules are in sys.modules too, while classes created at runtime may have no module to look into
        if module := sys.modules.get(class_.__module__):
            namespace = vars(module)
        else:
            namespace = {}

        out = ModuleNameResolver(namespace, self)
        return out

# ################################################################################################################################

    def read(self, model_class:'type') -> 'None':
        """ Reads a model into the model definitions, unless it is there already.
        """
        model_name = model_class.__name__

        # Each model is read once, which also ends the reading of models that refer to one another ..
        if model_name in self.visited:
            return

        self.visited.add(model_name)

        # .. a model that a scan of the source code found is not read again ..
        if model_name in self.all_models:
            return

        # .. and classes that are not models have no fields to document.
        if not is_model_class(model_class):
            return

        resolver = self.get_resolver(model_class)
        fields:'anydict' = {}

        # Dataclasses know their fields, including the inherited ones, and their defaults ..
        if dataclasses.is_dataclass(model_class):
            for field in dataclasses.fields(model_class):
                fields[field.name] = self._get_dataclass_field(field, resolver)

        # .. while other models have their annotations only.
        else:
            annotations = get_annotations(model_class)

            for field_name, annotation in annotations.items():
                field_type = get_runtime_type(annotation, resolver)
                fields[field_name] = {
                    'type': field_type,
                    'default': None,
                    'required': True,
                }

        self.all_models[model_name] = {'fields': fields, 'file_path': _runtime_file_path}

# ################################################################################################################################

    def _get_dataclass_field(self, field:'dataclasses.Field[any_]', resolver:'ModuleNameResolver') -> 'anydict':
        """ Returns the definition of one field of a dataclass.
        """
        field_type = get_runtime_type(field.type, resolver)

        has_default = field.default is not dataclasses.MISSING
        has_default_factory = field.default_factory is not dataclasses.MISSING

        # A field is required unless it has a default value or a default factory
        is_required = True

        if has_default:
            default = field.default
            is_required = False
        else:
            default = None

        if has_default_factory:
            is_required = False

        out = {
            'type': field_type,
            'default': default,
            'required': is_required,
        }

        return out

# ################################################################################################################################
# ################################################################################################################################

def extract_model_fields_recursive(model_class:'type', all_models:'anydict', visited:'strset | None'=None) -> 'None':
    """ Reads a model class and every model that its fields refer to into the given model definitions.
    """
    if visited is None:
        visited = set()

    reader = ModelReader(all_models, visited)
    reader.read(model_class)

# ################################################################################################################################

def read_runtime_type(type_hint:'any_', all_models:'anydict') -> 'any_':
    """ Returns the type that the mapper documents for an annotation of a service's input or output,
    reading the models that it refers to into the given model definitions.
    """
    reader = ModelReader(all_models, set())
    resolver = ModuleNameResolver({}, reader)

    out = get_runtime_type(type_hint, resolver)
    return out

# ################################################################################################################################
# ################################################################################################################################
