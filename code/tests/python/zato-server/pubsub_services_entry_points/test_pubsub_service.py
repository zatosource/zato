# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Service entry points
from service_entry_points.compare import assert_same_record, wait_for_record
from service_entry_points.requests import All_Targets, Model_Target, new_request_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import Suite
    from service_entry_points.compare import references_dict
    from service_entry_points.requests import Target

    Suite = Suite

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('target', All_Targets, ids=[target.kind for target in All_Targets])
def test_publish_to_service(suite:'Suite', references:'references_dict', target:'Target') -> 'None':
    """ A request published with self.pubsub to a service by its name reaches the service the same way
    that self.invoke does.
    """
    request_id = new_request_id()

    suite.publish_to_service(target, request_id)
    record = wait_for_record(suite.client, request_id)

    assert_same_record(references[target.kind], record, 'self.pubsub to a service')

# ################################################################################################################################

def test_publish_model_to_service(suite:'Suite', references:'references_dict') -> 'None':
    """ A model instance published with self.pubsub to a service is rebuilt into the model that self.invoke gives.
    """
    request_id = new_request_id()

    suite.publish_to_service(Model_Target, request_id, should_publish_model=True)
    record = wait_for_record(suite.client, request_id)

    assert_same_record(references[Model_Target.kind], record, 'self.pubsub of a model to a service')

# ################################################################################################################################
# ################################################################################################################################
