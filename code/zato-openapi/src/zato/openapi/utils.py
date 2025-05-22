# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import importlib
import inspect
import logging
import sys
from typing import Any, Dict, List, Optional, Set, Tuple, Type

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def get_full_class_name(cls: Type) -> str:
    """Get the fully qualified name of a class."""
    module = cls.__module__
    if module == 'builtins':
        return cls.__name__
    return f'{module}.{cls.__name__}'

# ################################################################################################################################
# ################################################################################################################################

def is_model_class(cls: Any) -> bool:
    """Check if a class is a Zato model class."""
    if not inspect.isclass(cls):
        return False

    # Check if it inherits from Model or BaseModel
    for base in cls.__mro__:
        base_name = base.__name__
        if base_name in ['Model', 'BaseModel']:
            return True

    # Check if it has the dataclass decorator
    if hasattr(cls, '__dataclass_fields__'):
        return True

    return False

# ################################################################################################################################
# ################################################################################################################################

def resolve_model_class(model_name: str) -> Optional[Type]:
    """Resolve a model class name to the actual class."""
    # Try to import the model
    parts = model_name.split('.')

    # If it's just a class name without a module
    if len(parts) == 1:
        # Check if it's already in sys.modules
        for module_name, module in sys.modules.items():
            if hasattr(module, model_name):
                cls = getattr(module, model_name)
                if is_model_class(cls):
                    return cls
        return None

    # If it's a fully qualified name
    module_name = '.'.join(parts[:-1])
    class_name = parts[-1]

    try:
        module = importlib.import_module(module_name)
        if hasattr(module, class_name):
            cls = getattr(module, class_name)
            if is_model_class(cls):
                return cls
    except (ImportError, AttributeError) as e:
        logger.debug(f"Could not resolve model {model_name}: {e}")

    return None

# ################################################################################################################################
# ################################################################################################################################

def follow_inheritance_chain(cls: Type) -> List[Type]:
    """Follow the inheritance chain of a class up to the Service base class."""
    chain = []
    for base in cls.__mro__:
        chain.append(base)
        if base.__name__ == 'Service':
            break
    return chain

# ################################################################################################################################
# ################################################################################################################################

def extract_inline_io_fields(io_definition: Any) -> Dict[str, Dict[str, Any]]:
    """Extract field information from an inline I/O definition."""
    fields = {}

    if isinstance(io_definition, tuple):
        for field in io_definition:
            # Check if it's an optional field (prefixed with -)
            if isinstance(field, str) and field.startswith('-'):
                field_name = field[1:]  # Remove the - prefix
                fields[field_name] = {
                    'type': 'string',
                    'nullable': True
                }
            elif isinstance(field, str):
                fields[field] = {
                    'type': 'string'
                }

    return fields

# ################################################################################################################################
# ################################################################################################################################
