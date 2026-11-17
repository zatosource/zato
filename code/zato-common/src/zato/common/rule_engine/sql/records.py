# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from .data import any_, RuleDefinitionRecord, RuleVersionRecord

# ################################################################################################################################
# ################################################################################################################################

def definition_record(row:'any_') -> 'RuleDefinitionRecord':
    """ Converts one SQL row into a detached definition record.
    """
    # Copy the SQLAlchemy mapping ..
    mapping = row._mapping
    values = dict(mapping)

    # .. and return a backend-owned immutable record.
    out = RuleDefinitionRecord(**values)
    return out

# ################################################################################################################################

def version_record(row:'any_') -> 'RuleVersionRecord':
    """ Converts one SQL row into a detached version record.
    """
    # Copy the SQLAlchemy mapping ..
    mapping = row._mapping
    values = dict(mapping)

    # .. and return a backend-owned immutable record.
    out = RuleVersionRecord(**values)
    return out

# ################################################################################################################################
# ################################################################################################################################
