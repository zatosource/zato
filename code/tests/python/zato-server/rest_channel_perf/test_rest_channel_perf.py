# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import base64
import json
from urllib.request import urlopen

# Zato
from request_driver import build_request, measure_scenarios, new_scenario
from zato.common.test.perf_report import report_result, start_measurement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_tokens import IdentityProvider
    from request_driver import Scenario
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict, strdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the server is left to finish the imports that it runs in the background after it starts, in seconds
    Settle_Seconds = 30

    # The connections of each scenario other than the concurrent one
    Connections = 4
    Concurrent_Connections = 50

    Subject = 'mary.johnson'

    Status_OK = 200
    Status_Unauthorized = 401
    Status_Not_Found = 404

    Nanoseconds_Per_Microsecond = 1000

# ################################################################################################################################
# ################################################################################################################################

def _get_basic(username:'str', password:'str') -> 'str':
    credentials = f'{username}:{password}'.encode('utf-8')

    out = 'Basic ' + base64.b64encode(credentials).decode('ascii')
    return out

# ################################################################################################################################

def _build_scenarios(provider:'IdentityProvider', credentials:'strdict') -> 'list[Scenario]':
    """ Returns the scenarios in the order they run.
    """
    basic_valid = _get_basic(credentials['basic_username'], credentials['basic_password'])
    basic_invalid = _get_basic(credentials['basic_username'], 'Invalid.Password')

    token = provider.new_token(ModuleCtx.Subject)

    json_body = json.dumps({'customer_id': 123, 'name': 'John Smith', 'segment': 'retail'}).encode('utf-8')
    model_body = json.dumps({'customer_id': 123, 'name': 'John Smith'}).encode('utf-8')

    soap_body = (
        '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
        '<soap:Body><GetCustomer xmlns="urn:customers"><customer_id>123</customer_id><name>John Smith</name>'
        '</GetCustomer></soap:Body></soap:Envelope>'
    ).encode('utf-8')

    json_headers = {'Content-Type': 'application/json'}
    soap_headers = {'Content-Type': 'text/xml; charset=utf-8', 'SOAPAction': '"urn:customers:GetCustomer"'}

    ok = ModuleCtx.Status_OK
    connections = ModuleCtx.Connections

    out = [
        new_scenario('get-no-security', 'GET without security',
            build_request('GET', '/test/perf/ping', {}, b''), ok, connections),
        new_scenario('get-basic-auth', 'GET with Basic Auth',
            build_request('GET', '/test/perf/basic', {'Authorization': basic_valid}, b''), ok, connections),
        new_scenario('get-api-key', 'GET with an API key',
            build_request('GET', '/test/perf/apikey', {'X-API-Key': credentials['api_key']}, b''), ok, connections),
        new_scenario('get-static-bearer', 'GET with a static bearer token',
            build_request('GET', '/test/perf/bearer-static', {'Authorization': f'Bearer {credentials["static_token"]}'}, b''),
            ok, connections),
        new_scenario('get-jwt', 'GET with a JWT verified against a cached JWKS document',
            build_request('GET', '/test/perf/jwt', {'Authorization': f'Bearer {token}'}, b''), ok, connections),
        new_scenario('get-path-params', 'GET with path parameters',
            build_request('GET', '/test/perf/customers/123/orders/456', {}, b''), ok, connections),
        new_scenario('post-json-input', 'POST with a JSON body and declared input',
            build_request('POST', '/test/perf/input', json_headers, json_body), ok, connections),
        new_scenario('post-model', 'POST with a dataclass model',
            build_request('POST', '/test/perf/model', json_headers, model_body), ok, connections),
        new_scenario('soap-11', 'SOAP 1.1 request',
            build_request('POST', '/test/perf/soap', soap_headers, soap_body), ok, connections),
        new_scenario('rejected-401', 'Request rejected with 401',
            build_request('GET', '/test/perf/basic', {'Authorization': basic_invalid}, b''),
            ModuleCtx.Status_Unauthorized, connections),
        new_scenario('not-found-404', 'Request answered with 404',
            build_request('GET', '/test/perf/missing', {}, b''), ModuleCtx.Status_Not_Found, connections),
        new_scenario('audit-log', 'Channel with the audit log active',
            build_request('GET', '/test/perf/audit', {}, b''), ok, connections),
        new_scenario('concurrent-50', '50 concurrent keep-alive connections',
            build_request('GET', '/test/perf/ping', {}, b''), ok, ModuleCtx.Concurrent_Connections),
    ]

    return out

# ################################################################################################################################

def _get_handle_microseconds(host:'str', port:'int') -> 'float':
    """ Returns the time that the handle method of the ping service takes on its own, in microseconds.
    """
    with urlopen(f'http://{host}:{port}/test/perf/handle-cost') as response:
        data = json.loads(response.read())

    out = data['nanoseconds_per_call'] / ModuleCtx.Nanoseconds_Per_Microsecond
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_rest_channel_cpu_per_request(
    zato_server:'anydict',
    zato_client:'AdminClient',
    load_client:'str',
    identity_provider:'IdentityProvider',
    credentials:'strdict',
    data_dir:'str',
    ) -> 'None':
    """ Each scenario of REST and SOAP channels is answered with the status it expects, and its CPU time
    per request and requests per second are recorded with the settings of the server.
    """
    measurement = start_measurement(zato_client, zato_server['database'])

    scenarios = _build_scenarios(identity_provider, credentials)

    figures = measure_scenarios(
        load_client,
        data_dir,
        zato_server['port'],
        scenarios,
        zato_server['processes'],
        ModuleCtx.Settle_Seconds,
    )

    figures['handle_microseconds'] = _get_handle_microseconds(zato_server['host'], zato_server['port'])

    _ = report_result(measurement, 'rest-channel', figures)

# ################################################################################################################################
# ################################################################################################################################
