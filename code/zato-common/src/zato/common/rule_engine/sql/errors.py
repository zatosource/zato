# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

class RuleSQLStoreError(Exception):
    """ Base class for all errors raised by the rule SQL backend.
    """

# ################################################################################################################################

class RecordNotFoundError(RuleSQLStoreError):
    """ A requested definition, version or decision does not exist.
    """

# ################################################################################################################################

class VersionConflictError(RuleSQLStoreError):
    """ The caller attempted to write against a definition version that is no longer current.
    """

# ################################################################################################################################

class InvalidDocumentError(RuleSQLStoreError):
    """ A document or payload cannot be represented as JSON.
    """

# ################################################################################################################################

class InvalidStoreInputError(RuleSQLStoreError):
    """ A required store input is empty or outside its accepted range.
    """

# ################################################################################################################################

class DecisionBufferFullError(RuleSQLStoreError):
    """ The asynchronous decision buffer is full, no decision was silently discarded.
    """

# ################################################################################################################################

class DecisionAlreadyExistsError(RuleSQLStoreError):
    """ A decision identifier was submitted more than once.
    """

# ################################################################################################################################

class DecisionWriterError(RuleSQLStoreError):
    """ The asynchronous decision writer failed.
    """

# ################################################################################################################################

class ApprovalRequiredError(RuleSQLStoreError):
    """ Publishing is blocked because the approval gate is on and the version has no approval.
    """

# ################################################################################################################################

class ApprovalContentMismatchError(RuleSQLStoreError):
    """ An approval exists for the version but its content hash does not match the current document.
    """

# ################################################################################################################################

class SelfApprovalNotAllowedError(RuleSQLStoreError):
    """ The author of a version tried to approve their own work while self-approval is disabled.
    """

# ################################################################################################################################
# ################################################################################################################################
