# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Zato
from zato.server.connection.mcp.schema import io_to_json_schema

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class _ServiceNoIO:
    """ A service class that has no _io attribute at all.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################

class TestIOToJSONSchemaDispatch(TestCase):
    """ Tests for the io_to_json_schema top-level dispatcher.
    """

    def test_no_io_returns_empty_object_schema(self:'any_') -> 'None':
        """ A service with no _io attribute returns a plain object schema.
        """

        result = io_to_json_schema(_ServiceNoIO)
        self.assertEqual(result, {'type': 'object'})

# ################################################################################################################################
# ################################################################################################################################
