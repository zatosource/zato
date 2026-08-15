# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
from concurrent.futures import ThreadPoolExecutor
from http.client import NOT_FOUND, OK
from statistics import median

# local
import _audit
import _constants
import _enmasse
import _helpers

# Zato
from zato.common.audit_log.api import AuditEvent

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strnone

# ################################################################################################################################
# ################################################################################################################################

# How long to wait until the idle TTL has passed, in seconds
_past_ttl_seconds = _constants.Session_TTL_Seconds + 1

# How long to wait until the reaper has provably swept, in seconds
_past_sweep_seconds = _constants.Session_TTL_Seconds + _constants.Reaper_Interval_Seconds + 2

# What the server logs when the reaper removes expired sessions
_reaper_log_marker = 'Reaper removed'

# How many times the expiry test fills the whole session cap and lets it expire
_expiry_waves = 5

# How many threads create sessions at once in the expiry test
_session_create_workers = 20

# How many threads write in the sustained-traffic test and how many calls each makes
_sustained_threads = 20
_sustained_calls_per_thread = 60

# The page size the sustained-traffic test reads the audit database with
_audit_page_size = 100

# How many tools the catalog gateway serves - more than one tools/list page
_catalog_tool_count = 150

# The catalog gateway the pagination test creates and deletes
_catalog_gateway = 'test.llm.catalog'
_catalog_path    = '/mcp/llm/catalog'

# The module the catalog services hot-deploy as and the item id the catalog call asks for
_catalog_module_name = 'crm_catalog.py'
_catalog_item_id     = 'ITEM-0001'

# How many gateways the fleet test imports at once
_fleet_gateway_count = 24

# The name and path prefixes of the fleet gateways
_fleet_gateway_prefix = 'test.llm.fleet'
_fleet_path_prefix    = '/mcp/llm/fleet'

# How many sequential calls the one-session marathon makes
_marathon_call_count = 250

# How many calls each end of the marathon is measured over and the growth
# ratio the two ends must stay within - a generous bound, so only a real
# per-call slowdown can breach it
_marathon_sample_size = 25
_marathon_ratio_bound = 5

# ################################################################################################################################
# ################################################################################################################################

class TestResourceGrowth:
    """ Resources over time - expired sessions, the audit database under sustained
    traffic, hundreds of tools, dozens of gateways and one very long session.
    """

# ################################################################################################################################

    def test_expired_sessions_leave_no_residue(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_TTL)

        def one_initialize(_:'int') -> 'strnone':
            response = _helpers.initialize_response(client)
            out = response.headers.get('Mcp-Session-Id')
            return out

        # Wave after wave fills the whole cap and is left to expire ..
        first_wave_ids = []

        for wave_index in range(_expiry_waves):

            with ThreadPoolExecutor(max_workers=_session_create_workers) as executor:
                session_ids = list(executor.map(one_initialize, range(_constants.Session_Cap)))

            # .. every creation succeeded - the previous wave's expired sessions
            # took no slots even before the reaper swept them ..
            for session_id in session_ids:
                assert session_id, (wave_index, session_ids.count(None))

            if wave_index == 0:
                first_wave_ids = session_ids

            time.sleep(_past_ttl_seconds)

        # .. the reaper's sweep removes what expired and the server says so ..
        server_log_path = zato_server['server_log_path']
        log_offset = os.path.getsize(server_log_path)

        time.sleep(_past_sweep_seconds)

        with open(server_log_path) as server_log:
            _ = server_log.seek(log_offset)
            new_log_text = server_log.read()

        assert _reaper_log_marker in new_log_text, new_log_text
        assert _constants.Gateway_TTL in new_log_text, new_log_text

        # .. a session of the first wave is gone from the store entirely ..
        delete_response = client.delete_session(first_wave_ids[0])
        assert delete_response.status_code == NOT_FOUND, delete_response.text

        # .. and creation still works as if nothing had ever filled the cap.
        session_id = _helpers.open_session(client)
        _ = client.delete_session(session_id)

# ################################################################################################################################

    def test_the_audit_database_under_sustained_traffic(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        min_id = _audit.last_event_id(audit_db_path)

        client = _helpers.make_client(zato_server, _constants.Path_Main)

        # Thousands of events go in from parallel writers ..
        def one_writer(writer_index:'int') -> 'None':

            session_id = _helpers.open_session(client)

            for call_index in range(_sustained_calls_per_thread):

                order_id = f'{_constants.Order_ID}-s{writer_index}-n{call_index}'
                body = _helpers.call_tool(client, session_id, _constants.Service_Order_Status, {'order_id': order_id})

                data = _helpers.get_result_data(body)
                assert data['order_id'] == order_id, body

            _ = client.delete_session(session_id)

        with ThreadPoolExecutor(max_workers=_sustained_threads) as executor:
            futures = []

            for writer_index in range(_sustained_threads):
                futures.append(executor.submit(one_writer, writer_index))

            for future in futures:
                future.result()

        # .. every insert succeeded and none was duplicated ..
        total_calls = _sustained_threads * _sustained_calls_per_thread

        _ = _audit.wait_for_events(
            audit_db_path, total_calls,
            object_name=_constants.Gateway_Main,
            event_type=AuditEvent.MCP_Tools_Call,
            min_id=min_id)

        events = _audit.read_events(
            audit_db_path, object_name=_constants.Gateway_Main, event_type=AuditEvent.MCP_Tools_Call, min_id=min_id)

        assert len(events) == total_calls, len(events)

        all_ids = []

        for event in events:
            all_ids.append(event['id'])

        assert len(set(all_ids)) == total_calls, len(set(all_ids))

        # .. and paging through the gateway's whole event set newest-first stays exact
        # at every offset - the pages tile with no overlap and no gap, in strictly
        # falling id order. The pages carry every event type, the way listings do,
        # so the expected set is read without the tools-call filter.
        gateway_events = _audit.read_events(audit_db_path, object_name=_constants.Gateway_Main, min_id=min_id)

        gateway_ids = []

        for event in gateway_events:
            gateway_ids.append(event['id'])

        paged_ids = []
        offset = 0

        while True:

            page = _audit.read_events_page(
                audit_db_path, _constants.Gateway_Main, _audit_page_size, offset, min_id=min_id)

            if not page:
                break

            for event in page:
                paged_ids.append(event['id'])

            offset += _audit_page_size

        for index in range(1, len(paged_ids)):
            assert paged_ids[index] < paged_ids[index - 1], (index, paged_ids[index - 1], paged_ids[index])

        assert sorted(paged_ids) == gateway_ids, (len(paged_ids), len(gateway_ids))

# ################################################################################################################################

    def test_hundreds_of_tools_on_one_gateway(self, zato_server:'anydict') -> 'None':

        server_directory = zato_server['server_directory']

        # The whole catalog goes out as one hot-deployed module ..
        service_names = []
        source_parts = [
            '# -*- coding: utf-8 -*-\n',
            'from zato.server.service import Service\n',
        ]

        for item_index in range(1, _catalog_tool_count + 1):

            service_name = f'crm.catalog.item-{item_index:04d}'
            service_names.append(service_name)

            source_parts.append(f'''
class CatalogItem{item_index:04d}(Service):
    """ Returns the details of one catalog item - pass the item id.
    """
    name = '{service_name}'
    input = 'item_id'

    def handle(self):
        self.response.payload = {{'item': '{service_name}', 'item_id': self.request.input.item_id}}
''')

        pickup_path = os.path.join(zato_server['pickup_directory'], _catalog_module_name)

        with open(pickup_path, 'w') as pickup_file:
            _ = pickup_file.write(''.join(source_parts))

        # .. the import may only run once every service is deployed,
        # or the gateway's tool registry could not resolve them ..
        last_service_name = service_names[-1]

        def catalog_is_deployed() -> 'bool':
            try:
                _ = _helpers.admin_invoke(zato_server, 'zato.service.get-by-name',
                    {'cluster_id': 1, 'name': last_service_name})
            except Exception:
                out = False
            else:
                out = True
            return out

        _helpers.wait_until(catalog_is_deployed, 'the catalog services are deployed')

        try:
            # .. one gateway serves the whole catalog ..
            config = _enmasse.build_suite_config()
            config['mcp_gateway'].append({
                'name': _catalog_gateway,
                'is_active': True,
                'url_path': _catalog_path,
                'services': service_names,
                'security_groups': [_constants.Group_Main],
                'is_audit_log_active': True,
            })
            _enmasse.run_import(server_directory, config)

            client = _helpers.make_client(zato_server, _catalog_path)

            def gateway_serves() -> 'bool':
                response = _helpers.initialize_response(client)
                out = response.status_code == OK
                return out

            _helpers.wait_until(gateway_serves, 'the catalog gateway serves')

            session_id = _helpers.open_session(client)

            # .. pagination walks the full set with no duplicates and no gaps ..
            listed_names = []
            cursor = None
            page_count = 0

            while True:

                if cursor is None:
                    params = {}
                else:
                    params = {'cursor': cursor}

                response = client.jsonrpc('tools/list', params=params, session_id=session_id)
                result = response.json()['result']

                listed_names.extend(_helpers.get_tool_names(result['tools']))
                page_count += 1

                # The last page's cursor is final
                if 'nextCursor' not in result:
                    break

                cursor = result['nextCursor']

            assert page_count > 1, page_count
            assert len(listed_names) == _catalog_tool_count, len(listed_names)
            assert sorted(set(listed_names)) == sorted(service_names), len(set(listed_names))

            # .. and the last-listed tool answers a call like any other.
            last_listed = listed_names[-1]
            body = _helpers.call_tool(client, session_id, last_listed, {'item_id': _catalog_item_id})

            data = _helpers.get_result_data(body)
            assert data['item'] == last_listed, body
            assert data['item_id'] == _catalog_item_id, body

        finally:
            # The catalog gateway is removed again - the suite's own gateways stay as they were.
            config = _enmasse.build_suite_config()
            config['mcp_gateway'].append({'name': _catalog_gateway, 'should_delete': True})
            _enmasse.run_import(server_directory, config)

# ################################################################################################################################

    def test_dozens_of_gateways_on_one_server(self, zato_server:'anydict') -> 'None':

        audit_db_path = zato_server['audit_db_path']
        server_directory = zato_server['server_directory']

        # Each fleet gateway serves exactly one service, rotating through the CRM set
        fleet = []

        for fleet_index in range(1, _fleet_gateway_count + 1):

            service_name = _constants.Service_List_CRM[fleet_index % len(_constants.Service_List_CRM)]

            fleet.append({
                'name': f'{_fleet_gateway_prefix}.{fleet_index:04d}',
                'url_path': f'{_fleet_path_prefix}-{fleet_index:04d}',
                'service': service_name,
            })

        try:
            # One import lands them all at once ..
            config = _enmasse.build_suite_config()

            for entry in fleet:
                config['mcp_gateway'].append({
                    'name': entry['name'],
                    'is_active': True,
                    'url_path': entry['url_path'],
                    'services': [entry['service']],
                    'security_groups': [_constants.Group_Main],
                    'is_audit_log_active': True,
                })

            _enmasse.run_import(server_directory, config)

            last_client = _helpers.make_client(zato_server, fleet[-1]['url_path'])

            def fleet_serves() -> 'bool':
                response = _helpers.initialize_response(last_client)
                out = response.status_code == OK
                return out

            _helpers.wait_until(fleet_serves, 'the whole fleet serves')

            min_id = _audit.last_event_id(audit_db_path)

            # .. every gateway serves only its own tool and every call routes to its own path ..
            for entry in fleet:

                client = _helpers.make_client(zato_server, entry['url_path'])
                session_id = _helpers.open_session(client)

                tools = _helpers.list_tools(client, session_id)
                tool_names = _helpers.get_tool_names(tools)
                assert tool_names == [entry['service']], (entry['name'], tool_names)

                body = _helpers.call_tool(client, session_id, entry['service'], {})
                assert 'result' in body, (entry['name'], body)

                _ = client.delete_session(session_id)

            # .. and each gateway's audit log holds exactly its own one call, nothing else's.
            for entry in fleet:

                events = _audit.wait_for_events(
                    audit_db_path, 1,
                    object_name=entry['name'],
                    event_type=AuditEvent.MCP_Tools_Call,
                    min_id=min_id)

                tool_call_events = []

                for event in events:
                    if event['event_type'] == AuditEvent.MCP_Tools_Call:
                        tool_call_events.append(event)

                assert len(tool_call_events) == 1, (entry['name'], tool_call_events)
                assert tool_call_events[0]['endpoint'] == entry['service'], (entry['name'], tool_call_events)

        finally:
            # The whole fleet is removed again in one import.
            config = _enmasse.build_suite_config()

            for entry in fleet:
                config['mcp_gateway'].append({'name': entry['name'], 'should_delete': True})

            _enmasse.run_import(server_directory, config)

# ################################################################################################################################

    def test_one_session_across_many_calls(self, zato_server:'anydict') -> 'None':

        client = _helpers.make_client(zato_server, _constants.Path_Main)
        session_id = _helpers.open_session(client)

        arguments = {'order_id': _constants.Order_ID}

        # Hundreds of sequential calls on the one session, each timed ..
        durations = []
        bodies = []

        for _ in range(_marathon_call_count):

            start_time = time.monotonic()
            body = _helpers.call_tool(client, session_id, _constants.Service_Order_Status, arguments)
            durations.append(time.monotonic() - start_time)

            bodies.append(body)

        # .. the last call behaves exactly as the first ..
        first_data = _helpers.get_result_data(bodies[0])
        last_data = _helpers.get_result_data(bodies[-1])

        assert first_data == last_data, (first_data, last_data)

        for body in bodies:
            data = _helpers.get_result_data(body)
            assert data['status'] == _constants.Order_Status, body

        # .. and the session does not slow down as it ages - the last stretch
        # stays within a generous ratio of the first one.
        first_median = median(durations[:_marathon_sample_size])
        last_median = median(durations[-_marathon_sample_size:])

        assert last_median <= first_median * _marathon_ratio_bound, (first_median, last_median)

        _ = client.delete_session(session_id)

# ################################################################################################################################
# ################################################################################################################################
