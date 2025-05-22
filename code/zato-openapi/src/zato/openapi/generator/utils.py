# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import os
import inspect
from pathlib import Path
from types import ModuleType

# Zato
from zato.common.typing_ import any_, strnone
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

def find_services_and_models(module:'ModuleType', base_service_class:'type'=Service,
        base_model_class:'type'=Model) -> 'tuple[dict, dict]':
    """ Finds all service and model classes in a module.
    """
    services = {}
    models = {}

    for name, obj in inspect.getmembers(module):
        # Skip builtins and modules
        if name.startswith('_') or inspect.ismodule(obj):
            continue

        # Check if it's a service
        if inspect.isclass(obj):
            # Direct inheritance from Service
            if issubclass(obj, base_service_class) and obj != base_service_class:
                services[name] = obj
                if hasattr(obj, 'name'):
                    services[obj.name] = obj
            # Check for service-like patterns
            elif hasattr(obj, 'name') and isinstance(obj.name, str):
                has_handle = hasattr(obj, 'handle') and callable(getattr(obj, 'handle'))
                has_io = hasattr(obj, 'input') or hasattr(obj, 'output') or hasattr(obj, 'model')
                class_name = obj.__name__
                is_adapter = any(suffix for suffix in ('Adapter', 'API', 'Service') if class_name.endswith(suffix))

                if has_handle or has_io or is_adapter:
                    services[name] = obj
                    if hasattr(obj, 'name'):
                        services[obj.name] = obj
            # Check if it's a model
            elif hasattr(obj, '__annotations__') and issubclass(obj, base_model_class) and obj != base_model_class:
                models[name] = obj

    return services, models

# ################################################################################################################################

def scan_directory_for_modules(directory_path:'str | Path') -> 'list[Path]':
    """ Recursively scans a directory for Python files.
    """
    py_files = []
    for root, _, files in os.walk(directory_path):
        for file_name in files:
            if file_name.endswith('.py') and not file_name.startswith('__'):
                py_files.append(Path(os.path.join(root, file_name)))
    return py_files

# ################################################################################################################################

def extract_path_from_service_name(service_name:'str') -> 'str':
    """ Converts a service name to an API path.
    """
    # Replace dots with slashes
    path = service_name.replace('.', '/')

    # Ensure path starts with a slash
    if not path.startswith('/'):
        path = f'/{path}'

    return path

# ################################################################################################################################

def determine_http_method_from_service(service_name:'str') -> 'str':
    """ Determines the appropriate HTTP method for a service.
    """
    # Convert to lowercase for consistent matching
    name = service_name.lower()

    # Check for method indicators in the name
    if 'get' in name:
        return 'GET'
    elif 'delete' in name:
        return 'DELETE'
    elif 'post' in name or 'create' in name:
        return 'POST'
    elif 'put' in name or 'update' in name:
        return 'PUT'
    elif 'patch' in name:
        return 'PATCH'

    # Default to POST if no clear indicator
    return 'POST'

# ################################################################################################################################

def generate_operation_id(service_name:'str') -> 'str':
    """ Generates a camelCase operation ID from a service name.
    """
    # Clean the service name by removing non-alphanumeric characters
    clean_name = ''.join(c for c in service_name if c.isalnum() or c == '_')

    # Split by underscores or other delimiters
    parts = []
    current_part = ''
    for char in clean_name:
        if char == '_':
            if current_part:
                parts.append(current_part)
                current_part = ''
        else:
            current_part += char
    if current_part:
        parts.append(current_part)

    # Create camelCase operation ID
    if parts:
        # First part is lowercase, rest are capitalized
        operation_id = parts[0].lower()
        for part in parts[1:]:
            operation_id += part.capitalize()
    else:
        operation_id = 'operation'

    return operation_id

# ################################################################################################################################

def extract_description_from_docstring(obj:'any_') -> 'strnone':
    """ Extracts a clean description from a docstring.
    """
    if not obj.__doc__:
        return None

    # Clean up docstring
    lines = [line.strip() for line in obj.__doc__.splitlines()]

    # Remove empty lines at the beginning and end
    while lines and not lines[0]:
        lines.pop(0)

    while lines and not lines[-1]:
        lines.pop()

    if not lines:
        return None

    # Join lines with space to create a single paragraph
    return ' '.join(lines)

# ################################################################################################################################

def generate_service_summary(service_name:'str') -> 'str':
    """ Generates a summary for a service based on its name.
    """
    # Use service name and convert to readable format
    clean_name = service_name.split('.')[-1]  # Get last part of name
    words = []

    # Split by underscores, dots, or camel case
    current_word = ''
    for i, char in enumerate(clean_name):
        if char == '_' or char == '.':
            if current_word:
                words.append(current_word)
                current_word = ''
        elif char.isupper() and i > 0 and clean_name[i-1].islower():
            # CamelCase boundary
            words.append(current_word)
            current_word = char
        else:
            current_word += char

    if current_word:
        words.append(current_word)

    # Capitalize each word and join with spaces
    if words:
        title = ' '.join(word.capitalize() for word in words)
        return f'{title} Operation'

    return 'API Operation'

# ################################################################################################################################
# ################################################################################################################################
