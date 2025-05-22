# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import ast
import importlib.util
import inspect
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# PyYAML
import yaml

# Zato
from zato.common.typing_ import list_, optional, union_
from zato.openapi.type_mapper import map_zato_type_to_openapi
from zato.openapi.utils import (
    extract_inline_io_fields, follow_inheritance_chain,
    get_full_class_name, is_model_class, resolve_model_class
)

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(frozen=True)
class ServiceIODefinition:
    service_name: str
    input_type: Any
    output_type: Any
    is_input_model: bool
    is_output_model: bool
    input_fields: Dict[str, Any]
    output_fields: Dict[str, Any]
    source_file: str

# ################################################################################################################################
# ################################################################################################################################

class ServiceScanner:
    """Scans service files to extract I/O definitions and maps them to OpenAPI types."""

    def __init__(self, directories: List[str], output_file: str):
        self.directories = directories
        self.output_file = output_file
        self.service_io_definitions = []
        self.model_definitions = {}
        self.processed_files = set()
        self.processed_models = set()

    def scan(self) -> None:
        """Scan all directories for service definitions and build type mappings."""
        for directory in self.directories:
            self._scan_directory(directory)

        # Map all collected types to OpenAPI equivalents
        openapi_mappings = self._build_openapi_mappings()

        # Write the mappings to a YAML file
        self._write_yaml(openapi_mappings)

    def _scan_directory(self, directory: str) -> None:
        """Recursively scan a directory for Python files containing service definitions."""
        directory_path = Path(directory)

        if not directory_path.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)

    def _process_file(self, file_path: str) -> None:
        """Process a Python file to extract service definitions and their I/O types."""
        if file_path in self.processed_files:
            return

        self.processed_files.add(file_path)

        try:
            # Parse the Python file
            with open(file_path, 'r') as f:
                file_content = f.read()

            tree = ast.parse(file_content)

            # Get the module's directory to resolve imports
            module_dir = os.path.dirname(file_path)
            if module_dir not in sys.path:
                sys.path.insert(0, module_dir)

            # Extract all class definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._process_class_definition(node, file_path, file_content)

            # Look for imports that might be model definitions
            self._process_imports(tree, file_path, module_dir)

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")

    def _process_class_definition(self, node: ast.ClassDef, file_path: str, file_content: str) -> None:
        """Process a class definition to check if it's a service and extract I/O."""
        # Check if this class inherits from Service or a subclass of Service
        is_service = False
        for base in node.bases:
            base_name = self._get_name_from_node(base)
            if base_name in ['Service', 'RESTAdapter', 'BaseAutopayAdapter', 'BaseKjarniAdapter']:
                is_service = True
                break

        if not is_service:
            return

        # Extract service name
        service_name = None
        input_type = None
        output_type = None

        # Look for class attributes
        for child in node.body:
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        # Check for service name
                        if target.id == 'name' and isinstance(child.value, ast.Constant):
                            service_name = child.value.value
                        # Check for input definition
                        elif target.id == 'input':
                            input_type = self._extract_io_type(child.value)
                        # Check for output definition
                        elif target.id == 'output':
                            output_type = self._extract_io_type(child.value)
                        # Check for model definition (used by some adapters)
                        elif target.id == 'model':
                            output_type = self._extract_io_type(child.value)

        if service_name:
            # Process the I/O definitions
            is_input_model, input_fields = self._process_io_definition(input_type)
            is_output_model, output_fields = self._process_io_definition(output_type)

            # Create and store the service I/O definition
            io_def = ServiceIODefinition(
                service_name=service_name,
                input_type=input_type,
                output_type=output_type,
                is_input_model=is_input_model,
                is_output_model=is_output_model,
                input_fields=input_fields,
                output_fields=output_fields,
                source_file=file_path
            )

            self.service_io_definitions.append(io_def)

    def _get_name_from_node(self, node: ast.AST) -> str:
        """Extract the name from an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return ""

    def _extract_io_type(self, node: ast.AST) -> Any:
        """Extract the I/O type from an AST node."""
        if isinstance(node, ast.Name):
            # Single class reference (e.g., input = MyModel)
            return node.id
        elif isinstance(node, ast.Tuple):
            # Tuple of strings (e.g., input = 'field1', 'field2')
            field_names = []
            for elt in node.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    field_names.append(elt.value)
            return tuple(field_names)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            # Single string (e.g., input = 'field1')
            return (node.value,)
        elif isinstance(node, ast.Subscript):
            # List of a type (e.g., model = list_[MyModel])
            if isinstance(node.value, ast.Name) and node.value.id == 'list_':
                if isinstance(node.slice, ast.Index):
                    # Python 3.8 and earlier
                    if isinstance(node.slice.value, ast.Name):
                        return f"list_[{node.slice.value.id}]"
                elif isinstance(node.slice, ast.Name):
                    # Python 3.9+
                    return f"list_[{node.slice.id}]"
        return None

    def _process_io_definition(self, io_type: Any) -> Tuple[bool, Dict[str, Any]]:
        """Process an I/O definition to determine if it's a model and extract fields."""
        if not io_type:
            return False, {}

        # If it's a tuple of strings, it's an inline definition
        if isinstance(io_type, tuple) and all(isinstance(field, str) for field in io_type):
            fields = {field: {'type': 'string'} for field in io_type}
            return False, fields

        # If it's a string, it might be a model class name
        if isinstance(io_type, str):
            # Check if it's a list of models
            if io_type.startswith('list_[') and io_type.endswith(']'):
                model_name = io_type[6:-1]  # Extract model name from list_[ModelName]
                is_model, fields = self._resolve_model_fields(model_name)
                return is_model, {'type': 'array', 'items': fields}

            # Otherwise, try to resolve it as a model
            return self._resolve_model_fields(io_type)

        return False, {}

    def _resolve_model_fields(self, model_name: str) -> Tuple[bool, Dict[str, Any]]:
        """Resolve a model class name to its field definitions."""
        # Check if we've already processed this model
        if model_name in self.model_definitions:
            return True, self.model_definitions[model_name]

        # Try to import and inspect the model class
        try:
            model_class = resolve_model_class(model_name)
            if model_class and is_model_class(model_class):
                fields = {}

                # Get annotations from the class
                annotations = getattr(model_class, '__annotations__', {})
                for field_name, field_type in annotations.items():
                    field_info = self._process_field_type(field_type)
                    fields[field_name] = field_info

                # Store the model definition for future reference
                self.model_definitions[model_name] = fields
                return True, fields
        except Exception as e:
            logger.debug(f"Could not resolve model {model_name}: {e}")

        return False, {}

    def _process_field_type(self, field_type: Any) -> Dict[str, Any]:
        """Process a field type annotation to extract OpenAPI type information."""
        # Handle union types
        if hasattr(field_type, '__origin__') and field_type.__origin__ is Union:
            # For union types, we'll use the first non-None type
            non_none_types = [t for t in field_type.__args__ if t is not type(None)]
            if non_none_types:
                return self._process_field_type(non_none_types[0])

        # Handle list types
        if hasattr(field_type, '__origin__') and field_type.__origin__ is list:
            item_type = field_type.__args__[0]
            return {
                'type': 'array',
                'items': self._process_field_type(item_type)
            }

        # Map the type to OpenAPI
        return map_zato_type_to_openapi(field_type)

    def _process_imports(self, tree: ast.AST, file_path: str, module_dir: str) -> None:
        """Process imports in a file to find model definitions."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    self._check_imported_module(name.name, module_dir)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_path = f"{node.module}"
                    for name in node.names:
                        self._check_imported_module(f"{module_path}.{name.name}", module_dir)

    def _check_imported_module(self, module_name: str, module_dir: str) -> None:
        """Check if an imported module contains model definitions."""
        try:
            # Try to find the module file
            module_parts = module_name.split('.')
            possible_paths = []

            # Try different combinations of the module path
            for i in range(len(module_parts)):
                base_module = '.'.join(module_parts[:i+1])
                try:
                    spec = importlib.util.find_spec(base_module)
                    if spec and spec.origin and spec.origin.endswith('.py'):
                        possible_paths.append(spec.origin)
                except (ModuleNotFoundError, AttributeError):
                    pass

            # Process each possible module file
            for path in possible_paths:
                if path not in self.processed_files and os.path.exists(path):
                    self._process_file(path)

        except Exception as e:
            logger.debug(f"Error checking imported module {module_name}: {e}")

    def _build_openapi_mappings(self) -> Dict[str, Any]:
        """Build OpenAPI type mappings from collected service I/O definitions."""
        mappings = {
            'components': {
                'schemas': {}
            }
        }

        # Add all model definitions to the schemas
        for model_name, fields in self.model_definitions.items():
            mappings['components']['schemas'][model_name] = {
                'type': 'object',
                'properties': fields
            }

        return mappings

    def _write_yaml(self, mappings: Dict[str, Any]) -> None:
        """Write the OpenAPI mappings to a YAML file."""
        with open(self.output_file, 'w') as f:
            yaml.dump(mappings, f, default_flow_style=False)

        logger.info(f"OpenAPI type mappings written to {self.output_file}")

# ################################################################################################################################
# ################################################################################################################################

def scan_directories(directories, output_file):
    """Scan directories for Zato services and generate OpenAPI type mappings.

    Args:
        directories: List of directories to scan
        output_file: Path to output YAML file
    """
    scanner = ServiceScanner(directories, output_file)
    scanner.scan()
    return scanner.model_definitions

# ################################################################################################################################
# ################################################################################################################################
