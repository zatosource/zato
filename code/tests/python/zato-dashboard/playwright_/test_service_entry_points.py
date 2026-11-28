# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from collections.abc import Generator
from json import loads

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from service_entry_points.compare import references_dict
    from service_entry_points.requests import Target
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from service_entry_points.compare import assert_same_invocation, assert_same_record, parse_soap_response, wait_for_record
from service_entry_points.requests import All_Targets, HL7, HL7_Target, Kind, new_caller_password, new_request, \
    new_request_id, SOAPVersion, Structured_Targets, to_json, to_soap_envelope
from service_entry_points_ui import deploy, invoke_in_ide, invoke_mllp_channel, invoke_rest_channel, invoke_soap_channel, \
    PayloadFormat, publish_to_topic, take_references

# ################################################################################################################################
# ################################################################################################################################

_soap_versions = (SOAPVersion.V11, SOAPVersion.V12)

_target_ids = [target.kind for target in All_Targets]
_structured_target_ids = [target.kind for target in Structured_Targets]
_soap_version_ids = [f'soap-{version}' for version in _soap_versions]

# ################################################################################################################################
# ################################################################################################################################

def _new_request_text(target:'Target', request_id:'str') -> 'str':
    """ The canonical request of a service as the text that a person enters - ER7 for HL7 v2, JSON otherwise.
    """
    request = new_request(target, request_id)

    if target.kind == Kind.HL7:
        out = request
    else:
        out = to_json(request)

    return out

# ################################################################################################################################

def _parse_response_text(target:'Target', response_text:'str') -> 'any_':
    """ The response of a service out of the text that Dashboard shows - ER7 for HL7 v2, JSON otherwise.
    """
    if target.kind == Kind.HL7:
        out = response_text
    else:
        out = loads(response_text)

    return out

# ################################################################################################################################

def _get_payload_format(target:'Target') -> 'str':
    """ The format of the IDE that a service takes its request in.
    """
    if target.kind == Kind.HL7:
        out = PayloadFormat.HL7
    else:
        out = PayloadFormat.JSON

    return out

# ################################################################################################################################

def _get_soap_channel(target:'Target', soap_version:'str') -> 'str':
    """ The SOAP channel of a service in the given SOAP version.
    """
    if soap_version == SOAPVersion.V11:
        out = target.soap_11_channel
    else:
        out = target.soap_12_channel

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def references(zato_dashboard:'anydict', api_client:'any_') -> 'Generator[references_dict, None, None]':
    """ Deploys the services under test with their definitions for the duration of this module and yields
    the reference of each service, invoked through self.invoke.
    """
    caller_password = new_caller_password()
    file_path = deploy(zato_dashboard, api_client, caller_password)

    yield take_references(api_client)

    os.remove(file_path)

# ################################################################################################################################
# ################################################################################################################################

class TestServiceEntryPoints:
    """ Every Dashboard entry point of a service gives the record and the response that self.invoke gives.
    """

    @pytest.mark.parametrize('target', All_Targets, ids=_target_ids)
    def test_ide(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'any_',
        references:'references_dict',
        target:'Target',
        ) -> 'None':
        """ A service invoked from the IDE with its request in the format of the service.
        """
        request_id = new_request_id()
        request_text = _new_request_text(target, request_id)
        payload_format = _get_payload_format(target)

        response_text = invoke_in_ide(
            logged_in_page, zato_dashboard['dashboard_url'], target.service_name, payload_format, request_text)

        response = _parse_response_text(target, response_text)
        assert_same_invocation(references[target.kind], api_client, request_id, response, 'the IDE')

# ################################################################################################################################

    @pytest.mark.parametrize('target', All_Targets, ids=_target_ids)
    def test_rest_channel(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'any_',
        references:'references_dict',
        target:'Target',
        ) -> 'None':
        """ The REST channel of a service invoked from the Invoke overlay of its row.
        """
        request_id = new_request_id()
        request_text = _new_request_text(target, request_id)

        response_text = invoke_rest_channel(
            logged_in_page, zato_dashboard['dashboard_url'], target.rest_channel, request_text)

        response = _parse_response_text(target, response_text)
        assert_same_invocation(references[target.kind], api_client, request_id, response, 'the REST channel overlay')

# ################################################################################################################################

    @pytest.mark.parametrize('soap_version', _soap_versions, ids=_soap_version_ids)
    @pytest.mark.parametrize('target', Structured_Targets, ids=_structured_target_ids)
    def test_soap_channel(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'any_',
        references:'references_dict',
        target:'Target',
        soap_version:'str',
        ) -> 'None':
        """ The SOAP channel of a service invoked with an envelope from the Invoke overlay of its row.
        """
        request_id = new_request_id()
        envelope = to_soap_envelope(new_request(target, request_id), soap_version)
        channel_name = _get_soap_channel(target, soap_version)

        response_text = invoke_soap_channel(logged_in_page, zato_dashboard['dashboard_url'], channel_name, envelope)

        response = parse_soap_response(response_text.encode('utf8'))
        assert_same_invocation(
            references[target.kind], api_client, request_id, response, f'the SOAP {soap_version} channel overlay')

# ################################################################################################################################

    def test_mllp_channel(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'any_',
        references:'references_dict',
        ) -> 'None':
        """ The MLLP channel of the HL7 service sent an HL7 v2 message from the Invoke overlay of its row.
        """
        request_id = new_request_id()
        message = new_request(HL7_Target, request_id)

        ack = invoke_mllp_channel(logged_in_page, zato_dashboard['dashboard_url'], HL7.Channel_Name, message)

        assert_same_invocation(references[HL7_Target.kind], api_client, request_id, ack, 'the MLLP channel overlay')

# ################################################################################################################################

    @pytest.mark.parametrize('target', All_Targets, ids=_target_ids)
    def test_topic_publish(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'any_',
        references:'references_dict',
        target:'Target',
        ) -> 'None':
        """ A request published from the Publish overlay of the topic of a service, which a push subscription delivers.
        """
        request_id = new_request_id()
        payload = _new_request_text(target, request_id)

        publish_to_topic(logged_in_page, zato_dashboard['dashboard_url'], target.topic_name, payload)
        record = wait_for_record(api_client, request_id)

        assert_same_record(references[target.kind], record, 'the topic publish overlay')

# ################################################################################################################################
# ################################################################################################################################
