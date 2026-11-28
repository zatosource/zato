# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Service entry points
from service_entry_points.compare import assert_same_invocation
from service_entry_points.requests import new_request_id, Structured_Targets

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import Suite
    from service_entry_points.compare import references_dict
    from service_entry_points.requests import Target

    Suite = Suite

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('target', Structured_Targets, ids=[target.kind for target in Structured_Targets])
def test_rest(suite:'Suite', references:'references_dict', target:'Target') -> 'None':
    """ The JSON body of a request posted to the REST channel of a service gives the record and the response
    that self.invoke gives.
    """
    request_id = new_request_id()
    response = suite.post_rest(target, request_id)

    assert_same_invocation(references[target.kind], suite.client, request_id, response, 'a REST channel')

# ################################################################################################################################
# ################################################################################################################################
