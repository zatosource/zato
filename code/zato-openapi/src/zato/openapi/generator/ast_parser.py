# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import ast
from pathlib import Path

# ################################################################################################################################
# ################################################################################################################################

# Helper functions to extract complex values
def extract_tuple_values(node):
    """ Extract values from a tuple node. """
    values = []
    for elt in node.elts:
        if isinstance(elt, ast.Constant):
            values.append(elt.value)

        elif isinstance(elt, ast.Call):
            values.append(extract_function_call(elt))
        else:
            values.append(None)
    return tuple(values)

def extract_list_values(node):
    """ Extract values from a list node. """
    values = []
    for elt in node.elts:
        if isinstance(elt, ast.Constant):
            values.append(elt.value)

        elif isinstance(elt, ast.Call):
            values.append(extract_function_call(elt))
        else:
            values.append(None)
    return values

def extract_function_call(node):
    """ Extract information from a function call node (e.g., Integer('port')). """
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
        return None

    func_name = node.func.id
    args = []

    for arg in node.args:
        if isinstance(arg, ast.Constant):
            args.append(arg.value)

        else:
            args.append(None)

    return {
        'type': func_name,
        'args': args
    }

# ################################################################################################################################
# ################################################################################################################################

def extract_class_definition(node):
    """ Extracts class definition information from an AST node.
    """
    # Get class name
    class_name = node.name

    # Get base classes
    bases = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)

    # Get class attributes
    attrs = {}
    for item in node.body:
        if isinstance(item, ast.Assign):
            # Simple attribute assignment
            for target in item.targets:
                if isinstance(target, ast.Name):
                    # Get the value if it's a constant
                    value = None
                    if isinstance(item.value, ast.Constant):
                        value = item.value.value

                    elif isinstance(item.value, ast.Tuple):
                        value = extract_tuple_values(item.value)
                    elif isinstance(item.value, ast.List):
                        value = extract_list_values(item.value)
                    elif isinstance(item.value, ast.Call):
                        # Handle function calls like Integer('port')
                        value = extract_function_call(item.value)

                    attrs[target.id] = value

    # Get annotations for dataclass fields
    annotations = {}
    for item in node.body:
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            # Get annotation as string
            if isinstance(item.annotation, ast.Name):
                annotations[item.target.id] = item.annotation.id
            elif isinstance(item.annotation, ast.Subscript) and isinstance(item.annotation.value, ast.Name):
                # Handle simple subscript types like List[str]
                container = item.annotation.value.id
                if isinstance(item.annotation.slice, ast.Index):
                    if hasattr(item.annotation.slice, 'value') and isinstance(item.annotation.slice.value, ast.Name):
                        elem_type = item.annotation.slice.value.id
                        annotations[item.target.id] = f'{container}[{elem_type}]'
                else:  # Python 3.9+
                    if isinstance(item.annotation.slice, ast.Name):
                        elem_type = item.annotation.slice.id
                        annotations[item.target.id] = f'{container}[{elem_type}]'

    # Check for input and output attributes
    input_def = attrs.get('input')
    output_def = attrs.get('output')
    model_def = attrs.get('model')

    # Check for SimpleIO attributes
    input_required = attrs.get('input_required')
    input_optional = attrs.get('input_optional')
    output_required = attrs.get('output_required')
    output_optional = attrs.get('output_optional')

    return {
        'name': class_name,
        'bases': bases,
        'attrs': attrs,
        'annotations': annotations,
        'input': input_def,
        'output': output_def,
        'model': model_def,
        'input_required': input_required,
        'input_optional': input_optional,
        'output_required': output_required,
        'output_optional': output_optional
    }

# ################################################################################################################################

def parse_file(file_path:'Path') -> 'list[dict]':
    """ Parses a Python file and extracts class definitions.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse the file into an AST
        tree = ast.parse(content)

        # Extract class definitions
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = extract_class_definition(node)
                classes.append(class_info)

        return classes

    except Exception:
        # Silently handle parsing errors
        return []

# ################################################################################################################################

def is_service_class(class_info:'dict', service_base_names:'list[str]'=['Service']) -> 'bool':
    """ Determines if a class is a service based on its attributes and base classes.
    """
    # Check if it inherits from a known service base class
    if any(base in service_base_names for base in class_info['bases']):
        return True

    # Check for SimpleIO-style service
    has_simpleio = any(base.endswith('SIO') for base in class_info['bases']) or 'SimpleIO' in class_info['bases']
    has_simpleio_attrs = ('input_required' in class_info['attrs'] or 'output_required' in class_info['attrs'] or
                         'input_optional' in class_info['attrs'] or 'output_optional' in class_info['attrs'])

    if has_simpleio or has_simpleio_attrs:
        return True

    # Check for service-like attributes
    has_name = 'name' in class_info['attrs']
    has_io = 'input' in class_info['attrs'] or 'output' in class_info['attrs'] or 'model' in class_info['attrs']

    # Check name patterns
    class_name = class_info['name']
    is_adapter = any(class_name.endswith(suffix) for suffix in ('Adapter', 'API', 'Service'))

    return has_name and (has_io or is_adapter)

# ################################################################################################################################

def is_model_class(class_info:'dict', model_base_names:'list[str]'=['Model']) -> 'bool':
    """ Determines if a class is a model based on its attributes and base classes.
    """
    # Check if it inherits from a known model base class
    if any(base in model_base_names for base in class_info['bases']):
        return True

    # Check for dataclass-like structure (has annotations)
    return len(class_info['annotations']) > 0

# ################################################################################################################################

def find_services_and_models(file_path:'Path', service_base_names:'list[str]'=['Service'],
                             model_base_names:'list[str]'=['Model']) -> 'tuple[list[dict], list[dict]]':
    """ Finds service and model classes in a Python file.
    """
    classes = parse_file(file_path)

    services = []
    models = []

    for class_info in classes:
        if is_service_class(class_info, service_base_names):
            services.append(class_info)
        elif is_model_class(class_info, model_base_names):
            models.append(class_info)

    return services, models

# ################################################################################################################################
# ################################################################################################################################
