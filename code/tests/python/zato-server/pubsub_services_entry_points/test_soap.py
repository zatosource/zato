# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Service entry points
from service_entry_points.compare import assert_same_invocation
from service_entry_points.requests import new_request_id, SOAPVersion, Structured_Targets

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import Suite
    from service_entry_points.compare import references_dict
    from service_entry_points.requests import Target

    Suite = Suite

# ################################################################################################################################
# ################################################################################################################################

_soap_versions = (SOAPVersion.V11, SOAPVersion.V12)

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('soap_version', _soap_versions, ids=[f'soap-{version}' for version in _soap_versions])
@pytest.mark.parametrize('target', Structured_Targets, ids=[target.kind for target in Structured_Targets])
def test_soap(suite:'Suite', references:'references_dict', target:'Target', soap_version:'str') -> 'None':
    """ The SOAP envelope of a request posted to the SOAP channel of a service gives the record that self.invoke
    gives, and a response element whose children are the response of self.invoke.
    """
    request_id = new_request_id()
    response = suite.post_soap(target, request_id, soap_version)

    assert_same_invocation(references[target.kind], suite.client, request_id, response, f'a SOAP {soap_version} channel')

# ################################################################################################################################
# ################################################################################################################################
