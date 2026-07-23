# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from .data import any_, RuleDecisionRecord, RuleDefinitionRecord, RuleEventRecord, RuleFollowRecord, \
    RuleRecentRecord, RuleReferenceRecord, RuleVersionRecord, RuleViewRecord

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

def event_record(row:'any_') -> 'RuleEventRecord':
    """ Converts one SQL row into a detached event record.
    """
    # Copy the SQLAlchemy mapping ..
    mapping = row._mapping
    values = dict(mapping)

    # .. and return a backend-owned immutable record.
    out = RuleEventRecord(**values)
    return out

# ################################################################################################################################

def decision_record(row:'any_') -> 'RuleDecisionRecord':
    """ Converts one SQL row into a detached decision record.
    """
    # Copy the SQLAlchemy mapping ..
    mapping = row._mapping
    values = dict(mapping)

    # .. and return a backend-owned immutable record.
    out = RuleDecisionRecord(**values)
    return out

# ################################################################################################################################

def reference_record(row:'any_') -> 'RuleReferenceRecord':
    """ Converts one SQL row into a detached where-used index record.
    """
    # Copy the SQLAlchemy mapping ..
    mapping = row._mapping
    values = dict(mapping)

    # .. and return a backend-owned immutable record.
    out = RuleReferenceRecord(**values)
    return out

# ################################################################################################################################

def follow_record(row:'any_') -> 'RuleFollowRecord':
    """ Converts one SQL row into a detached follow record.
    """
    # Copy the SQLAlchemy mapping ..
    mapping = row._mapping
    values = dict(mapping)

    # .. and return a backend-owned immutable record.
    out = RuleFollowRecord(**values)
    return out

# ################################################################################################################################

def view_record(row:'any_') -> 'RuleViewRecord':
    """ Converts one SQL row into a detached saved-view record.
    """
    # Copy the SQLAlchemy mapping ..
    mapping = row._mapping
    values = dict(mapping)

    # .. and return a backend-owned immutable record.
    out = RuleViewRecord(**values)
    return out

# ################################################################################################################################

def recent_record(row:'any_') -> 'RuleRecentRecord':
    """ Converts one SQL row into a detached recent-visit record.
    """
    # Copy the SQLAlchemy mapping ..
    mapping = row._mapping
    values = dict(mapping)

    # .. and return a backend-owned immutable record.
    out = RuleRecentRecord(**values)
    return out

# ################################################################################################################################
# ################################################################################################################################
