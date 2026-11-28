# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Service entry points
from service_entry_points.compare import assert_same_invocation
from service_entry_points.requests import HL7_Target, new_request_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import Suite
    from service_entry_points.compare import references_dict

    Suite = Suite

# ################################################################################################################################
# ################################################################################################################################

def test_mllp(suite:'Suite', references:'references_dict') -> 'None':
    """ An HL7 v2 message sent over MLLP through HAProxy gives the record that self.invoke gives,
    and the acknowledgment that the service returned to self.invoke.
    """
    request_id = new_request_id()
    ack = suite.send_mllp(request_id)

    assert_same_invocation(references[HL7_Target.kind], suite.client, request_id, ack, 'an MLLP channel')

# ################################################################################################################################

def test_rest(suite:'Suite', references:'references_dict') -> 'None':
    """ An HL7 v2 message posted to a REST channel of the hl7-v2 data format gives the record and the acknowledgment
    that self.invoke gives.
    """
    request_id = new_request_id()
    ack = suite.post_rest_hl7(request_id)

    assert_same_invocation(references[HL7_Target.kind], suite.client, request_id, ack, 'an HL7 v2 REST channel')

# ################################################################################################################################
# ################################################################################################################################
