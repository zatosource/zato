# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import tempfile
import time
from collections.abc import Generator
from http import HTTPStatus
from json import loads

# Requests
import requests

# pytest
import pytest

# Zato
from zato.common.test.service_entry_points.models import ServiceName

# Live environment
from live_environment.haproxy import Loopback_Address, start_haproxy
from live_environment.quickstart import Host, ZatoEnvironment
from live_environment.redis_process import ModuleCtx as RedisCtx, RedisProcess

# Live HL7
from live_hl7.sender import send

# Service entry points
from service_entry_points.compare import publish_through_driver, invoke_through_driver, parse_soap_response, take_reference
from service_entry_points.requests import All_Targets, Caller, get_soap_headers, HL7, HL7_Target, Module, new_caller_password, \
    new_request, render_definitions, Source, SOAPVersion, to_json, to_soap_envelope

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from service_entry_points.compare import references_dict
    from service_entry_points.requests import Target
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import any_, anydict, callable_, strdict

    AdminClient = AdminClient

# ################################################################################################################################
# ################################################################################################################################

class SuiteCtx:
    Directory_Prefix = 'zato_pubsub_services_entry_points_'
    Password_Prefix  = 'test.pubsub.services.entry-points'
    Definitions_File = 'service-entry-points.yaml'
    Client_Timeout   = 60
    HTTP_Timeout     = 60
    Ready_Timeout    = 120
    Poll_Interval    = 0.5

# The answers of a channel that the server has not received yet, or whose security definition it has not received yet
_not_ready_statuses = (HTTPStatus.NOT_FOUND, HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)

# ################################################################################################################################
# ################################################################################################################################

def _wait_until(condition:'callable_', description:'str') -> 'None':
    """ Waits until a condition is true, or raises an exception that names it.
    """
    deadline = time.monotonic() + SuiteCtx.Ready_Timeout

    while time.monotonic() < deadline:
        if condition():
            return
        time.sleep(SuiteCtx.Poll_Interval)

    raise Exception(f'{description} did not happen within {SuiteCtx.Ready_Timeout}s')

# ################################################################################################################################
# ################################################################################################################################

class Suite:
    """ A live server with the services under test, their channels, topics and subscriptions, and HAProxy in front
    of its MLLP listener. Every entry point takes the canonical request of a service under the request ID given.
    """
    def __init__(self, environment:'ZatoEnvironment', mllp_port:'int', caller_password:'str') -> 'None':
        self.environment = environment
        self.mllp_port = mllp_port
        self.caller_password = caller_password
        self.client:'AdminClient' = environment.client(SuiteCtx.Client_Timeout)
        self.base_url = f'http://{Host}:{environment.server_port}'

    def is_deployed(self, service_name:'str') -> 'bool':
        """ Whether the server has a service of the name deployed.
        """
        try:
            response = self.client.invoke('zato.service.get-by-name', {'name': service_name})

        # The server refuses the request for a service that it does not have
        except Exception:
            return False

        out = response['name'] == service_name
        return out

# ################################################################################################################################

    def invoke(self, target:'Target', request_id:'str') -> 'any_':
        """ Invokes a service with self.invoke through the driver and returns its response.
        """
        payload = new_request(target, request_id)

        out = invoke_through_driver(self.client, target.service_name, payload)
        return out

# ################################################################################################################################

    def publish_to_topic(self, target:'Target', request_id:'str', *, should_publish_model:'bool'=False) -> 'None':
        """ Publishes a request with self.pubsub to the topic of a service, which a push subscription delivers.
        """
        payload = new_request(target, request_id)
        publish_through_driver(self.client, target.topic_name, payload, should_publish_model=should_publish_model)

# ################################################################################################################################

    def publish_to_service(self, target:'Target', request_id:'str', *, should_publish_model:'bool'=False) -> 'None':
        """ Publishes a request with self.pubsub to a service by its name.
        """
        payload = new_request(target, request_id)
        publish_through_driver(self.client, target.service_name, payload, should_publish_model=should_publish_model)

# ################################################################################################################################

    def _post(self, url_path:'str', body:'str', headers:'strdict') -> 'Response':
        """ Posts a body to a channel, waiting for as long as the server has not yet received the channel
        or its security definition from the import of the definitions.
        """
        url = self.base_url + url_path
        auth = (Caller.Username, self.caller_password)
        deadline = time.monotonic() + SuiteCtx.Ready_Timeout

        while True:
            response = requests.post(url, data=body.encode('utf8'), headers=headers, auth=auth, timeout=SuiteCtx.HTTP_Timeout)

            if response.status_code not in _not_ready_statuses:
                break

            if time.monotonic() >= deadline:
                break

            time.sleep(SuiteCtx.Poll_Interval)

        assert response.status_code == HTTPStatus.OK, f'{url_path} answered {response.status_code} -> {response.text}'

        return response

# ################################################################################################################################

    def post_rest(self, target:'Target', request_id:'str') -> 'anydict':
        """ Posts the JSON body of a request to the REST channel of a service and returns the parsed response.
        """
        body = to_json(new_request(target, request_id))
        headers = {'Content-Type': 'application/json'}

        response = self._post(target.rest_path, body, headers)

        out = loads(response.text)
        return out

# ################################################################################################################################

    def post_rest_hl7(self, request_id:'str') -> 'str':
        """ Posts the ER7 text of a request to the REST channel of the HL7 service and returns the acknowledgment.
        """
        body = new_request(HL7_Target, request_id)
        headers = {'Content-Type': HL7.Content_Type}

        response = self._post(HL7_Target.rest_path, body, headers)

        out = response.text
        return out

# ################################################################################################################################

    def post_soap(self, target:'Target', request_id:'str', soap_version:'str') -> 'anydict':
        """ Posts the SOAP envelope of a request to the SOAP channel of a service in the given SOAP version
        and returns the response element as a dict.
        """
        body = to_soap_envelope(new_request(target, request_id), soap_version)
        headers = get_soap_headers(soap_version)

        if soap_version == SOAPVersion.V11:
            url_path = target.soap_11_path
        else:
            url_path = target.soap_12_path

        response = self._post(url_path, body, headers)

        out = parse_soap_response(response.content)
        return out

# ################################################################################################################################

    def send_mllp(self, request_id:'str') -> 'str':
        """ Sends the ER7 text of a request over MLLP through HAProxy and returns the acknowledgment, waiting for
        as long as the server has not yet started the MLLP channel from the import of the definitions.
        """
        message = new_request(HL7_Target, request_id)
        deadline = time.monotonic() + SuiteCtx.Ready_Timeout

        while True:
            try:
                result = send(Host, self.mllp_port, message)

            except Exception:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(SuiteCtx.Poll_Interval)

            else:
                break

        assert result.is_accepted, f'MLLP rejected request `{request_id}` -> {result}'

        out = result.ack_text
        return out

# ################################################################################################################################
# ################################################################################################################################

def _copy_module(environment:'ZatoEnvironment', file_name:'str', source_path:'str') -> 'None':
    """ Places a module into the pickup directory before the server starts, which deploys it during its startup.
    """
    os.makedirs(environment.pickup_directory, exist_ok=True)

    target = os.path.join(environment.pickup_directory, file_name)
    _ = shutil.copyfile(source_path, target)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='package')
def suite() -> 'Generator[Suite, None, None]':
    """ The server with the services under test deployed and their definitions imported.
    """
    directory = tempfile.mkdtemp(prefix=SuiteCtx.Directory_Prefix)
    environment = ZatoEnvironment(directory, password_prefix=SuiteCtx.Password_Prefix)
    caller_password = new_caller_password()
    haproxy = None

    # The streams of the scheduler and of the queue bridge have the same keys in every Redis,
    # so the server receives a Redis of its own that no other server on this machine uses
    redis = RedisProcess()

    try:
        redis.start()
        environment.create(redis_port=redis.port)

        _copy_module(environment, Module.File_Name, Source.Services)

        server_environment = redis.server_environment()
        server_environment.update({
            'Zato_Queue_Bridge_Redis_Host': RedisCtx.Host,
            'Zato_Queue_Bridge_Redis_Port': str(redis.port),
            'Zato_Queue_Bridge_Redis_Password': '',
        })

        environment.start(server_environment)

        haproxy = start_haproxy(directory, environment.mllp_internal_port, bind_address=Loopback_Address)

        suite = Suite(environment, haproxy.ports.mllp_plain, caller_password)

        def _is_ready() -> 'bool':
            out = suite.is_deployed(ServiceName.Read)
            return out

        _wait_until(_is_ready, f'The deployment of service {ServiceName.Read}')

        definitions = render_definitions(caller_password)
        _ = environment.import_yaml(SuiteCtx.Definitions_File, definitions)

        yield suite

    finally:
        if haproxy is not None:
            haproxy.stop()
        environment.stop()
        redis.cleanup()

# ################################################################################################################################

@pytest.fixture(scope='package')
def references(suite:'Suite') -> 'references_dict':
    """ The record and the response of each service under test invoked through self.invoke, keyed by its kind.
    """
    out:'references_dict' = {}

    for target in All_Targets:
        out[target.kind] = take_reference(suite.client, target)

    return out

# ################################################################################################################################
# ################################################################################################################################
