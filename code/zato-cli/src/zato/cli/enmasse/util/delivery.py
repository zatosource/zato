# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queue switch and the DLQ settings of an outgoing connection in enmasse.

# Zato
from zato.common.util.delivery_config import apply_delivery_defaults, Delivery_Field_Defaults, Delivery_Fields, \
    validate_delivery_fields

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

Delivery_Fields = Delivery_Fields

# ################################################################################################################################
# ################################################################################################################################

def prepare_delivery_fields(connection_def:'anydict', connection_type:'str') -> 'None':
    """ Fills in, in place, the defaults of a YAML definition and validates its delivery fields.
    """
    apply_delivery_defaults(connection_def)

    try:
        validate_delivery_fields(connection_def)
    except ValueError as e:
        connection_name = connection_def['name']
        raise Exception(f'{e} for {connection_type} connection `{connection_name}`')

# ################################################################################################################################

def delivery_needs_update(yaml_def:'anydict', db_def:'anydict') -> 'bool':
    """ Whether a stored connection differs from its YAML definition in any delivery field.
    """
    for name, default in Delivery_Field_Defaults.items():

        yaml_value = yaml_def.get(name)
        if yaml_value is None:
            yaml_value = default

        db_value = db_def.get(name)
        if db_value is None:
            db_value = default

        if yaml_value != db_value:
            return True

    return False

# ################################################################################################################################

def export_delivery_fields(exported_conn:'anydict', opaque:'anydict') -> 'None':
    """ Copies the delivery fields from a connection's opaque attributes to its exported definition.
    """
    for name, default in Delivery_Field_Defaults.items():

        value = opaque.get(name)
        if value is None:
            continue

        # Defaults are not exported
        if value != default:
            exported_conn[name] = value

# ################################################################################################################################
# ################################################################################################################################
