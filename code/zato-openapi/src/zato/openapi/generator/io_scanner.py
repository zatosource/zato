# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import ast
import importlib.util
import logging
import os
import sys

# Zato
from zato.input_output import IOProcessor, is_io_bool, is_io_int
from zato.openapi.generator.annotation import Container_Kinds, get_io_container, NameResolver, parse_annotation
from zato.openapi.generator.basic_types import Any_Type_Schema, Basic_Types
from zato.openapi.generator.runtime_model import extract_model_fields_recursive
from zato.openapi.generator.schemas import get_container_schema_builder, get_enum_schema, make_nullable

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anydictnone, anylist, strlist
    anydict = anydict
    anydictnone = anydictnone
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# Logger for this module
logger = logging.getLogger(__name__)

# Turns the strings of flat input and output declarations into typed elements, as the server does
_io_processor = IOProcessor()

# Resolves the names in the annotations of scanned source code, which is not imported
_name_resolver = NameResolver()

# The file path of models whose definitions do not name one
_unknown_file_path = 'unknown_file'

# ################################################################################################################################
# ################################################################################################################################

class TypeConversionError(Exception):
    """ Raised when a type cannot be converted to an OpenAPI type.
    """

# ################################################################################################################################
# ################################################################################################################################

def get_element_info(declaration:'any_') -> 'anydict':
    """ Returns the name, the required flag and the OpenAPI type of one element of a flat input or output declaration,
    which is a string or a typed element, the way the server's I/O processor reads it.
    """
    # A string becomes a typed element the same way the server makes it one, with the type that its name implies ..
    if isinstance(declaration, str):
        is_required = not declaration.startswith('-')
        element = _io_processor.convert_to_elem_instance(declaration, is_required)

    # .. while a typed element is one already.
    else:
        element = declaration

    # The server gives flat elements one of these three types
    if is_io_int(element):
        schema_type = 'integer'
    elif is_io_bool(element):
        schema_type = 'boolean'
    else:
        schema_type = 'string'

    out = {
        'name': element.name,
        'required': element.is_required,
        'schema_type': schema_type,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class IOVisitor(ast.NodeVisitor):
    """ AST visitor that extracts I/O definitions from service classes and model classes.
    """
    def __init__(self):
        self.services = []
        self.models = {}
        self.current_class = None
        self.is_service = False
        self.is_model = False
        self.service_name = None
        self.service_input = None
        self.service_output = None
        self.model_fields = {}
        self.handle_method_exists = False

    def visit_ClassDef(self, node:'ast.ClassDef') -> 'None':
        """ Visit class definitions to identify services and models.
        """
        prev_class = self.current_class
        prev_is_service = self.is_service
        prev_is_model = self.is_model
        prev_model_fields = self.model_fields

        self.current_class = node.name
        self.is_service = False
        self.is_model = False
        self.service_name = None
        self.service_input = None
        self.service_output = None
        self.model_fields = {}

        # Check if the class inherits from Service, RESTAdapter, or WSXAdapter
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in ('Service', 'RESTAdapter', 'WSXAdapter'):
                self.is_service = True
                break
            # Check if this is a Model class
            elif isinstance(base, ast.Name) and base.id == 'Model':
                self.is_model = True
                break

        # Visit all class contents
        for item in node.body:
            self.visit(item)

        # If this is a service, collect its information
        if self.is_service and self.service_name:
            service_info = {
                'name': self.service_name,
                'class_name': self.current_class,
                'input': self.service_input,
                'output': self.service_output,
                'has_handle_method': self.handle_method_exists
            }
            self.services.append(service_info)

        # If this is a model, collect its field information
        if self.is_model and self.model_fields:
            self.models[self.current_class] = self.model_fields

        self.current_class = prev_class
        self.is_service = prev_is_service
        self.is_model = prev_is_model
        self.model_fields = prev_model_fields

    def visit_AnnAssign(self, node:'ast.AnnAssign') -> 'None':
        """ Visit annotated assignments to find model field definitions.
        """
        if not self.current_class or not self.is_model:
            return

        # Handle model field annotations
        if isinstance(node.target, ast.Name):
            field_name = node.target.id
            field_type = parse_annotation(node.annotation, _name_resolver)
            field_default = None

            # Check if there's a default value
            if node.value:
                if isinstance(node.value, ast.Constant):
                    field_default = node.value.value
                elif isinstance(node.value, ast.Name) and node.value.id == 'None':
                    field_default = None

            # A field is required unless it has a default value or it accepts None
            has_default = node.value is not None

            if isinstance(field_type, dict):
                is_optional = 'optional' in field_type
            else:
                is_optional = False

            self.model_fields[field_name] = {
                'type': field_type,
                'default': field_default,
                'required': not has_default and not is_optional,
            }

    def visit_Assign(self, node:'ast.Assign') -> 'None':
        """ Visit assignments to find service attributes like name, input, output.
        """
        if not self.current_class:
            return

        # Check for service attributes
        if self.is_service:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # Check for name attribute
                    if target.id == 'name' and isinstance(node.value, ast.Constant):
                        self.service_name = node.value.value

                    # Check for input attribute
                    elif target.id == 'input':
                        if isinstance(node.value, ast.Name):
                            # Input as a model class
                            self.service_input = {'type': 'model', 'model_name': node.value.id}
                        elif isinstance(node.value, ast.Constant):
                            # Input as a string
                            element = get_element_info(node.value.value)
                            self.service_input = {
                                'type': 'string',
                                'name': element['name'],
                                'required': element['required'],
                                'schema_type': element['schema_type'],
                            }

                        elif isinstance(node.value, ast.Tuple):
                            # Input as a tuple of strings
                            elts = []
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant):
                                    elts.append(get_element_info(elt.value))

                            if elts:
                                self.service_input = {'type': 'tuple', 'elements': elts}
                        elif isinstance(node.value, ast.Subscript):
                            # Input as a container, e.g. list_[ModelClass]
                            io_type = parse_annotation(node.value, _name_resolver)
                            self.service_input = get_io_container(io_type)

                    # Check for output attribute
                    elif target.id == 'output':
                        if isinstance(node.value, ast.Name):
                            # Output as a model class
                            self.service_output = {'type': 'model', 'model_name': node.value.id}
                        elif isinstance(node.value, ast.Constant):
                            # Output as a string
                            element = get_element_info(node.value.value)
                            self.service_output = {
                                'type': 'string',
                                'name': element['name'],
                                'required': element['required'],
                                'schema_type': element['schema_type'],
                            }
                        elif isinstance(node.value, ast.Tuple):
                            # Output as a tuple of strings
                            elts = []
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant):
                                    elts.append(get_element_info(elt.value))
                            if elts:
                                self.service_output = {'type': 'tuple', 'elements': elts}
                        elif isinstance(node.value, ast.Subscript):
                            # Output as a container, e.g. list_[ModelClass]
                            io_type = parse_annotation(node.value, _name_resolver)
                            self.service_output = get_io_container(io_type)

    def visit_FunctionDef(self, node:'ast.FunctionDef') -> 'None':
        """ Visit function definitions to find handle() method.
        """
        if self.current_class and self.is_service and node.name == 'handle':
            self.handle_method_exists = True

# ################################################################################################################################
# ################################################################################################################################

def _get_model_file_path(model_def:'anydict') -> 'str':
    """ Returns the path of the file that a model is defined in, or the default name if its definition has none.
    """
    if file_path := model_def.get('file_path'):
        out = file_path
    else:
        out = _unknown_file_path

    return out

# ################################################################################################################################
# ################################################################################################################################

class TypeMapper:
    """ Maps Zato types to OpenAPI types. Nullability is expressed with type lists,
    e.g. ['string', 'null'], which is the OpenAPI 3.1 form the generator emits.
    """
    # The schemas of the type names that the mapper knows
    BASIC_TYPES = Basic_Types

    def __init__(self):
        self.schema_components = {}
        self.registered_models = set()

    def map_type(self, zato_type:'any_', model_definitions:'anydictnone'=None) -> 'anydict':
        """ Map a Zato type to an OpenAPI type.
        """
        model_definitions = model_definitions or {}

        # Names are types that the mapper knows, models, or types defined elsewhere ..
        if isinstance(zato_type, str):
            out = self._map_name(zato_type, model_definitions)

        # .. enumerations and literals are one of the values that they list ..
        elif 'enum' in zato_type:
            out = get_enum_schema(zato_type['enum'])

        # .. optional types accept null too ..
        elif zato_type.get('optional'):
            mapped_type = self.map_type(zato_type['type'], model_definitions)
            out = make_nullable(mapped_type)

        # .. unions accept a value of any of their types ..
        elif zato_type.get('container') == 'union':
            out = self._map_union(zato_type['union_types'], model_definitions)

        # .. containers have elements of a type of their own ..
        elif 'container' in zato_type:
            out = self._map_container(zato_type, model_definitions)

        # .. and anything else is a value of any type.
        else:
            out = dict(Any_Type_Schema)

        return out

# ################################################################################################################################

    def _map_name(self, type_name:'str', model_definitions:'anydict') -> 'anydict':
        """ Maps the name of a type that the mapper knows, of a model, or of a type defined elsewhere.
        """
        # Types that the mapper knows are copied, so that callers can never mutate the shared mapping ..
        if type_name in self.BASIC_TYPES:
            out = dict(self.BASIC_TYPES[type_name])

        # .. models are registered as components and referred to ..
        elif type_name in model_definitions:
            try:
                self._register_model_schema(type_name, model_definitions)
            except TypeConversionError as e:
                file_path = _get_model_file_path(model_definitions[type_name])
                raise TypeConversionError(f'Error with model {type_name} from file {file_path}: {e}')

            out = {'$ref': f'#/components/schemas/{type_name}'}

        # .. and a name that is neither, e.g. that of a class from a library, is a value of any type.
        else:
            out = dict(Any_Type_Schema)

        return out

# ################################################################################################################################

    def _map_union(self, union_types:'any_', model_definitions:'anydict') -> 'anydict':
        """ Maps a union into a schema that accepts a value of any of the union's types.
        """
        one_of_schemas = []

        for type_name in union_types:
            try:
                mapped_type = self.map_type(type_name, model_definitions)
                one_of_schemas.append(mapped_type)
            except TypeConversionError as e:
                logger.warning(f'Could not map union type {type_name}: {e}')

        # The union is made of the types that could be mapped ..
        if one_of_schemas:
            out = {'oneOf': one_of_schemas}

        # .. or of the JSON types in general if none could be.
        else:
            out = {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'number'},
                    {'type': 'object'},
                    {'type': 'array', 'items': {'type': 'object'}}
                ]
            }

        return out

# ################################################################################################################################

    def _map_container(self, zato_type:'anydict', model_definitions:'anydict') -> 'anydict':
        """ Maps a list, a set, a tuple or a dict, whose elements, or values in the case of dicts, have a type of their own.
        """
        container_name = zato_type['container']
        kind = Container_Kinds.get(container_name)

        # Containers of known kinds have schemas of their elements ..
        if builder := get_container_schema_builder(kind):
            element_schema = self.map_type(zato_type['element_type'], model_definitions)
            out = builder(element_schema)

        # .. while other containers are values of any type.
        else:
            out = dict(Any_Type_Schema)

        return out

# ################################################################################################################################

    def _register_model_schema(self, model_name:'str', model_definitions:'anydict') -> 'None':
        """ Register a model schema in the components section.
        """
        if model_name in self.registered_models:
            return

        model_def = model_definitions.get(model_name)
        if not model_def:
            raise TypeConversionError(f'Model \'{model_name}\' not found in definitions')

        # The model is registered before its fields are mapped, so that a model that refers to itself,
        # directly or through other models, has a reference to its own schema.
        self.registered_models.add(model_name)

        try:
            schema = self._get_model_schema(model_name, model_def, model_definitions)
        except TypeConversionError:
            self.registered_models.discard(model_name)
            raise

        self.schema_components[model_name] = schema

# ################################################################################################################################

    def _get_model_schema(self, model_name:'str', model_def:'any_', model_definitions:'anydict') -> 'anydict':
        """ Returns the schema of a model from the definitions of its fields.
        """
        properties = {}
        required = []

        # Extract file path information if available
        file_path = _get_model_file_path(model_def)

        # Definitions of models with a file path have their fields under a key of their own
        if 'file_path' in model_def:
            fields = model_def['fields']
        else:
            fields = model_def

        for field_name, field_info in fields.items():
            field_type = field_info['type']
            try:
                properties[field_name] = self.map_type(field_type, model_definitions)

                # Scalar defaults from the model definition are copied into the schema
                default = field_info.get('default')
                if isinstance(default, (str, int, float, bool)):
                    properties[field_name]['default'] = default

                # Add to required list if the field is required
                if field_info.get('required', True):
                    required.append(field_name)
            except TypeConversionError as e:
                # Re-raise with additional context
                raise TypeConversionError(f'Error mapping field \'{field_name}\' in model \'{model_name}\' (from {file_path}): {str(e)}')

        schema:'anydict' = {
            'type': 'object',
            'properties': properties
        }

        if required:
            schema['required'] = required

        return schema

# ################################################################################################################################

    def get_schema_components(self):
        """ Get all registered schema components.
        """
        return self.schema_components

# ################################################################################################################################
# ################################################################################################################################

def import_module_from_file(file_path:'str') -> 'any_':
    """ Dynamically import a module from a file path.
    """
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            logger.warning(f'Could not import {file_path}: {e}')
            return None
    return None

# ################################################################################################################################

def resolve_model_from_import(model_name:'str', file_path:'str') -> 'any_':
    """ Try to resolve a model class by importing the service file's module.
    """
    file_dir = os.path.dirname(file_path)
    if file_dir not in sys.path:
        sys.path.insert(0, file_dir)

    try:
        module = import_module_from_file(file_path)
        if module:
            for name, obj in vars(module).items():
                if name == model_name and isinstance(obj, type):
                    return obj

            for name, obj in vars(module).items():
                if isinstance(obj, type) and obj.__name__ == model_name:
                    return obj
    except Exception as e:
        logger.warning(f'Could not resolve model {model_name}: {e}')

    return None

# ################################################################################################################################
# ################################################################################################################################

class IOScanner:
    """ Scans directories for Zato services and extracts their I/O information.
    """
    def __init__(self):
        self.type_mapper = TypeMapper()

    def is_python_file(self, file_path:'str') -> 'bool':
        """ Check if a file is a Python file.
        """
        return file_path.endswith('.py')

    def _add_results(self, all_results:'anydict', results:'anydict') -> 'None':
        """ Adds the services and models of one scan to the results of all the scans.
        """
        all_services:'anylist' = all_results['services']
        all_models:'anydict' = all_results['models']

        all_services.extend(results['services'])
        all_models.update(results['models'])

    def scan_file(self, file_path:'str') -> 'anydict':
        """ Scan a single Python file for services and models.
        """
        result:'anydict' = {'services': [], 'models': {}}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=file_path)
                visitor = IOVisitor()
                visitor.visit(tree)

                for service in visitor.services:
                    service['file_path'] = file_path

                models_with_path = {}
                for model_name, model_info in visitor.models.items():
                    models_with_path[model_name] = {
                        'fields': model_info,
                        'file_path': file_path
                    }

                result['services'] = visitor.services
                result['models'] = models_with_path

                for service in visitor.services:
                    for io_key in ('input', 'output'):
                        io_def = service.get(io_key)
                        if io_def and io_def.get('type') == 'model':
                            model_name = io_def['model_name']
                            if model_name not in result['models']:
                                model_class = resolve_model_from_import(model_name, file_path)
                                if model_class:
                                    extract_model_fields_recursive(model_class, result['models'])

        except Exception as e:
            error_msg = f'Error parsing {file_path}: {e}'
            logger.error(error_msg)
            logger.error('Stack trace: ', exc_info=True)

        return result

    def scan_directory(self, directory:'str') -> 'anydict':
        """ Recursively scan a directory for services and models.
        """
        all_results:'anydict' = {'services': [], 'models': {}}
        py_files:'strlist' = []

        # Find all Python files in the directory
        for root, _, files in os.walk(directory):
            for file in files:
                if self.is_python_file(file):
                    py_files.append(os.path.join(root, file))

        for file_path in py_files:
            file_results = self.scan_file(file_path)
            self._add_results(all_results, file_results)

        return all_results

    def scan_files(self, file_paths:'strlist') -> 'anydict':
        """ Scan multiple files for services and models.
        """
        all_results:'anydict' = {'services': [], 'models': {}}
        for file_path in file_paths:
            if self.is_python_file(file_path):
                file_results = self.scan_file(file_path)
                self._add_results(all_results, file_results)

        return all_results

    def scan_directories(self, directories:'strlist') -> 'anydict':
        """ Scan multiple directories for services and models.
        """
        all_results:'anydict' = {'services': [], 'models': {}}
        for directory in directories:
            results = self.scan_directory(directory)
            self._add_results(all_results, results)

        return all_results

# ################################################################################################################################
# ################################################################################################################################

def scan_io(directories:'strlist', output_file:'str') -> 'None':
    """ Scan directories for services and generate an OpenAPI specification with I/O information.
    """
    # Import here to avoid circular imports
    from zato.openapi.generator.openapi_ import OpenAPIGenerator

    # Scan for services and models
    scanner = IOScanner()
    scan_results = scanner.scan_directories(directories)

    # Generate OpenAPI specification using the separate generator
    openapi_generator = OpenAPIGenerator(scanner.type_mapper)
    openapi_generator.generate_openapi(scan_results, output_file)

    logger.info(f'Found {len(scan_results["services"])} services and {len(scan_results["models"])} models. ' + \
               f'OpenAPI specification saved to {output_file}')

# ################################################################################################################################
# ################################################################################################################################
