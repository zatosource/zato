# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import dataclasses
from typing import Optional
from unittest import TestCase

# Zato
from zato.server.connection.mcp.schema import _is_field_required

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

@dataclasses.dataclass
class _RequiredField:
    name: str

@dataclasses.dataclass
class _HasDefault:
    name: str = 'default_value'

@dataclasses.dataclass
class _HasFactory:
    items: list = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class _OptionalType:
    name: 'Optional[str]' = None  # noqa: UP007

@dataclasses.dataclass
class _PipeNone:
    name: 'str | None' = None

# ################################################################################################################################
# ################################################################################################################################

class TestIsFieldRequired(TestCase):
    """ Tests for _is_field_required covering all branches.
    """

# ################################################################################################################################

    def test_field_required_no_default(self) -> 'None':
        """ A field with no default and a non-Optional type is required.
        """

        field = dataclasses.fields(_RequiredField)[0]
        annotation = _RequiredField.__annotations__['name']

        result:'any_' = _is_field_required(field, annotation)

        self.assertTrue(result)

# ################################################################################################################################

    def test_field_not_required_has_default(self) -> 'None':
        """ A field with a default value is not required.
        """

        field = dataclasses.fields(_HasDefault)[0]
        annotation = _HasDefault.__annotations__['name']

        result:'any_' = _is_field_required(field, annotation)

        self.assertFalse(result)

# ################################################################################################################################

    def test_field_not_required_has_factory(self) -> 'None':
        """ A field with default_factory is not required.
        """

        field = dataclasses.fields(_HasFactory)[0]
        annotation = _HasFactory.__annotations__['items']

        result:'any_' = _is_field_required(field, annotation)

        self.assertFalse(result)

# ################################################################################################################################

    def test_field_not_required_optional_type(self) -> 'None':
        """ A field typed Optional[str] is not required even without a default.
        """

        field = dataclasses.fields(_OptionalType)[0]
        annotation = Optional[str]

        result:'any_' = _is_field_required(field, annotation)

        self.assertFalse(result)

# ################################################################################################################################

    def test_field_not_required_pipe_none(self) -> 'None':
        """ A field typed str | None (PEP 604) is not required even without a default.
        """

        field = dataclasses.fields(_PipeNone)[0]
        annotation = str | None

        result:'any_' = _is_field_required(field, annotation)

        self.assertFalse(result)

# ################################################################################################################################
# ################################################################################################################################
