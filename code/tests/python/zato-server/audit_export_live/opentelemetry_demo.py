# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A Zato server exporting its audit log straight to Elasticsearch over OTLP, with Kibana to watch the events arrive.
# MCP tool calls, refused callers and REST traffic, some of it failing, keep flowing until Ctrl+C ends everything.

# stdlib
import os
import sys
import tempfile
import time

_this_directory = os.path.dirname(__file__)

sys.path.insert(0, os.path.join(_this_directory, '..', '..', 'zato-common', 'lib'))
sys.path.insert(0, _this_directory)

# requests
import requests  # noqa: E402

# Zato
from zato.common.audit_log.export.config import ModuleCtx as ExportCtx  # noqa: E402
from zato.common.crypto.api import CryptoManager  # noqa: E402

# Live environment
from live_elastic.containers import remove_stack, start_stack  # noqa: E402
from live_environment.parts import Parts, tear_down  # noqa: E402
from live_environment.quickstart import Host, ZatoEnvironment  # noqa: E402

# local
from _common import api_key_caller, wait_for_tools, ModuleCtx as LiveCtx  # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_elastic.containers import ElasticStack
    from zato.common.typing_ import anydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The MCP gateway the agents call and the two API keys they call it with
    Gateway_Name = 'billing'
    Gateway_Path = '/mcp/billing'
    Group_Name   = 'billing.agents'

    Agent_Definition   = 'billing.assistant'
    Partner_Definition = 'partner.portal'

    # The services the gateway offers as tools - one answers, the other always fails
    Echo_Service  = LiveCtx.Echo_Service
    Raise_Service = 'test.raise'

    # The REST channels - orders without their payloads leaving, orders with them, and an inventory that always fails
    Orders_Channel_Name = 'orders'
    Orders_Channel_Path = '/api/orders'

    Orders_Payload_Channel_Name = 'orders.with-payload'
    Orders_Payload_Channel_Path = '/api/orders-with-payload'

    Inventory_Channel_Name = 'inventory'
    Inventory_Channel_Path = '/api/inventory'

    # The environment the records name as their deployment
    Environment = 'demo'

    # How long one round of traffic waits before the next
    Round_Interval = 3

    # Every how many rounds a tool fails, a caller is refused and the inventory is called
    Tool_Failure_Every = 4
    Refusal_Every      = 5
    Inventory_Every    = 3

    # Timeout of the REST calls, in seconds
    HTTP_Timeout = 30

# ################################################################################################################################
# ################################################################################################################################

def build_definitions(agent_key:'str', partner_key:'str') -> 'str':
    """ The two API keys, their group, the gateway and the REST channels, as the YAML a user would import.
    """
    out = f'''\
security:
  - name: {ModuleCtx.Agent_Definition}
    type: apikey
    header: {LiveCtx.Key_Header}
    password: "{agent_key}"
  - name: {ModuleCtx.Partner_Definition}
    type: apikey
    header: {LiveCtx.Key_Header}
    password: "{partner_key}"

groups:
  - name: {ModuleCtx.Group_Name}
    members:
      - {ModuleCtx.Agent_Definition}
      - {ModuleCtx.Partner_Definition}

mcp_gateway:
  - name: {ModuleCtx.Gateway_Name}
    is_active: true
    is_audit_log_active: true
    url_path: {ModuleCtx.Gateway_Path}
    services:
      - {ModuleCtx.Echo_Service}
      - {ModuleCtx.Raise_Service}
    security_groups:
      - {ModuleCtx.Group_Name}

channel_rest:
  - name: {ModuleCtx.Orders_Channel_Name}
    service: {ModuleCtx.Echo_Service}
    url_path: {ModuleCtx.Orders_Channel_Path}
    is_audit_log_active: true
  - name: {ModuleCtx.Orders_Payload_Channel_Name}
    service: {ModuleCtx.Echo_Service}
    url_path: {ModuleCtx.Orders_Payload_Channel_Path}
    is_audit_log_active: true
    is_audit_export_payload_active: true
  - name: {ModuleCtx.Inventory_Channel_Name}
    service: {ModuleCtx.Raise_Service}
    url_path: {ModuleCtx.Inventory_Channel_Path}
    is_audit_log_active: true
'''
    return out

# ################################################################################################################################

def build_export_environment(stack:'ElasticStack') -> 'strstrdict':
    """ The variables that point the server's export at Elasticsearch, every source included.
    """
    out = {
        ExportCtx.Env_Endpoint: stack.otlp_logs_endpoint,
        ExportCtx.Env_Protocol: ExportCtx.Protocol_HTTP,
        ExportCtx.Env_Headers: f'Authorization=ApiKey {stack.api_key}',
        ExportCtx.Env_Environment: ModuleCtx.Environment,
        ExportCtx.Env_Resource_Attributes: f'data_stream.dataset={stack.dataset}',
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

def _new_order(round_number:'int') -> 'anydict':
    """ One order, different in each round, so the records are told apart.
    """
    out = {
        'order_id': f'ORD-{10_000 + round_number}',
        'customer': f'customer.{round_number % 7}@example.com',
        'amount': 25 * (round_number % 9 + 1),
        'currency': 'EUR',
    }

    return out

# ################################################################################################################################

def run_round(server_address:'str', agent_key:'str', partner_key:'str', round_number:'int') -> 'int':
    """ One round of traffic, answering with how many requests it sent.
    """
    gateway_url = server_address + ModuleCtx.Gateway_Path
    order = _new_order(round_number)

    request_count = 0

    # The assistant opens a session, lists the tools and calls one ..
    agent = api_key_caller(gateway_url, agent_key)

    initialized = agent.initialize()
    _ = agent.tools_list(initialized.session_id)
    _ = agent.tools_call(initialized.session_id, ModuleCtx.Echo_Service, order)
    request_count += 3

    # .. now and then it calls the tool that fails ..
    if round_number % ModuleCtx.Tool_Failure_Every == 0:
        _ = agent.tools_call(initialized.session_id, ModuleCtx.Raise_Service, {'order_id': order['order_id']})
        request_count += 1

    # .. the partner portal calls without a session ..
    partner = api_key_caller(gateway_url, partner_key)
    _ = partner.tools_call_stateless(ModuleCtx.Echo_Service, order)
    request_count += 1

    # .. now and then a caller with a key nobody issued is refused ..
    if round_number % ModuleCtx.Refusal_Every == 0:
        stranger = api_key_caller(gateway_url, 'unknown.' + CryptoManager.generate_hex_string())
        _ = stranger.tools_list_stateless()
        request_count += 1

    # .. the orders arrive over REST, once without their payload leaving and once with it ..
    _ = requests.post(server_address + ModuleCtx.Orders_Channel_Path, json=order, timeout=ModuleCtx.HTTP_Timeout)
    _ = requests.post(server_address + ModuleCtx.Orders_Payload_Channel_Path, json=order, timeout=ModuleCtx.HTTP_Timeout)
    request_count += 2

    # .. and now and then the inventory is asked, which always fails.
    if round_number % ModuleCtx.Inventory_Every == 0:
        stock_request = {'sku': f'SKU-{round_number % 11}'}
        _ = requests.post(server_address + ModuleCtx.Inventory_Channel_Path, json=stock_request, timeout=ModuleCtx.HTTP_Timeout)
        request_count += 1

    return request_count

# ################################################################################################################################

def _print_banner(stack:'ElasticStack', server_address:'str') -> 'None':
    lines = [
        '',
        '#' * 80,
        '',
        f'Kibana   -> {stack.kibana_url}',
        f'Username -> {stack.username}',
        f'Password -> {stack.password}',
        '',
        f'Discover -> {stack.discover_url}',
        '',
        f'Zato     -> {server_address}, exporting to {stack.otlp_logs_endpoint}',
        '',
        'Traffic runs until Ctrl+C, which removes the server and both containers.',
        '',
        '#' * 80,
        '',
    ]

    print('\n'.join(lines), flush=True)

# ################################################################################################################################

def main() -> 'None':

    parts = Parts()

    try:

        # Elasticsearch and Kibana come up first, the server needs the API key to export with ..
        parts.add('Elasticsearch and Kibana', remove_stack)
        stack = start_stack()

        # .. then the server, exporting from its very start ..
        directory = tempfile.mkdtemp(prefix='zato_opentelemetry_demo_')
        zato = ZatoEnvironment(directory, password_prefix='opentelemetry.demo')
        parts.add('zato environment', zato.stop)

        zato.create()
        zato.start(build_export_environment(stack))

        server_address = f'http://{Host}:{zato.server_port}'

        # .. everything the traffic needs is imported the way a user would ..
        agent_key = 'billing.assistant.' + CryptoManager.generate_hex_string()
        partner_key = 'partner.portal.' + CryptoManager.generate_hex_string()

        _ = zato.import_yaml('opentelemetry_demo.yaml', build_definitions(agent_key, partner_key))
        wait_for_tools(server_address + ModuleCtx.Gateway_Path, agent_key)

        _print_banner(stack, server_address)

        # .. and the traffic flows until the person watching it is done.
        round_number = 0
        total = 0

        while True:
            round_number += 1
            total += run_round(server_address, agent_key, partner_key, round_number)

            print(f'[TRAFFIC] Round {round_number}, {total} requests sent so far', flush=True)
            time.sleep(ModuleCtx.Round_Interval)

    except KeyboardInterrupt:
        print('\nStopping the demo', flush=True)

    finally:
        tear_down(parts)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
