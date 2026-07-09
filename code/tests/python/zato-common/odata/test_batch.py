# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import CREATED, NO_CONTENT, OK

# Zato
from zato.common.odata.batch import BatchRequest, build_json, build_multipart, parse_multipart
from zato.common.odata.client import ODataClient
from zato.common.odata.common import ODataVersion

# ################################################################################################################################
# ################################################################################################################################

def _read_request(url):
    """ One GET request for a batch.
    """
    out = BatchRequest()
    out.method = 'GET'
    out.url = url
    return out

# ################################################################################################################################

def _write_request(method, url, body):
    """ One modifying request for a batch.
    """
    out = BatchRequest()
    out.method = method
    out.url = url
    out.body = body
    return out

# ################################################################################################################################

def _seed(server):
    """ Loads a predictable set of Business Central customers.
    """
    server.reset()
    server.add_entities('customers', 'id', [
        {'id': 'aaaa0001-0000-0000-0000-000000000001', 'displayName': 'Adatum'},
        {'id': 'aaaa0002-0000-0000-0000-000000000002', 'displayName': 'Trey Research'},
    ])

# ################################################################################################################################

def _bc_client(server):
    config = {
        'address': server.service_root + '/',
        'odata_version': ODataVersion.V4,
        'auth_type': 'none',
    }
    out = ODataClient(config)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestBuildMultipart:
    """ The multipart bodies the client builds - offline, against the wire format itself.
    """

    def test_reads_are_individual_parts(self):
        body, content_type = build_multipart([_read_request('customers'), _read_request('vendors')])
        text = body.decode('utf8')

        assert content_type.startswith('multipart/mixed; boundary=batch_')

        # Two read parts, no changeset anywhere.
        assert text.count('GET customers HTTP/1.1') == 1
        assert text.count('GET vendors HTTP/1.1') == 1
        assert 'changeset' not in text

    def test_writes_group_into_changeset(self):
        requests = [
            _read_request('customers'),
            _write_request('POST', 'customers', {'displayName': 'One'}),
            _write_request('PATCH', "customers('a1')", {'displayName': 'Two'}),
        ]
        body, _ = build_multipart(requests)
        text = body.decode('utf8')

        # The consecutive writes share one changeset with per-request Content-IDs.
        assert text.count('boundary=changeset_') == 1
        assert 'Content-ID: 2' in text
        assert 'Content-ID: 3' in text

        # The read arrived before the changeset and stayed outside of it.
        changeset_start = text.index('changeset_')
        assert text.index('GET customers') < changeset_start

    def test_two_write_runs_are_two_changesets(self):
        requests = [
            _write_request('POST', 'customers', {'displayName': 'One'}),
            _read_request('customers'),
            _write_request('POST', 'customers', {'displayName': 'Two'}),
        ]
        body, _ = build_multipart(requests)
        text = body.decode('utf8')

        # The read in the middle split the writes into two separate changesets.
        assert text.count('boundary=changeset_') == 2

# ################################################################################################################################
# ################################################################################################################################

class TestBuildJSON:
    """ The V4 JSON batch bodies the client builds.
    """

    def test_ids_are_sequential(self):
        data = build_json([_read_request('customers'), _read_request('vendors')])

        assert data['requests'][0]['id'] == '1'
        assert data['requests'][1]['id'] == '2'

    def test_writes_share_an_atomicity_group(self):
        requests = [
            _read_request('customers'),
            _write_request('POST', 'customers', {'displayName': 'One'}),
            _write_request('POST', 'customers', {'displayName': 'Two'}),
        ]
        data = build_json(requests)

        # The read carries no group, the writes share one.
        assert 'atomicityGroup' not in data['requests'][0]
        assert data['requests'][1]['atomicityGroup'] == 'group1'
        assert data['requests'][2]['atomicityGroup'] == 'group1'

    def test_separate_write_runs_get_separate_groups(self):
        requests = [
            _write_request('POST', 'customers', {'displayName': 'One'}),
            _read_request('customers'),
            _write_request('POST', 'customers', {'displayName': 'Two'}),
        ]
        data = build_json(requests)

        assert data['requests'][0]['atomicityGroup'] == 'group1'
        assert data['requests'][2]['atomicityGroup'] == 'group2'

# ################################################################################################################################
# ################################################################################################################################

class TestParseMultipart:
    """ Multipart response parsing - offline, against a canned wire payload.
    """

    def test_plain_parts(self):
        boundary = 'batchresponse_abc'
        payload = (
            f'--{boundary}\r\n'
            'Content-Type: application/http\r\n'
            'Content-Transfer-Encoding: binary\r\n'
            '\r\n'
            'HTTP/1.1 200 OK\r\n'
            'Content-Type: application/json\r\n'
            '\r\n'
            '{"value": []}\r\n'
            f'--{boundary}\r\n'
            'Content-Type: application/http\r\n'
            'Content-Transfer-Encoding: binary\r\n'
            '\r\n'
            'HTTP/1.1 404 Not Found\r\n'
            'Content-Type: application/json\r\n'
            '\r\n'
            '{"error": {"code": "NotFound", "message": "No"}}\r\n'
            f'--{boundary}--\r\n'
        )

        responses = parse_multipart(payload.encode('utf8'), f'multipart/mixed; boundary={boundary}')

        assert len(responses) == 2

        assert responses[0].status_code == OK
        assert responses[0].body == {'value': []}
        assert responses[0].headers['Content-Type'] == 'application/json'

        assert responses[1].status_code == 404
        assert responses[1].body == {'error': {'code': 'NotFound', 'message': 'No'}}

    def test_changeset_parts_are_unwrapped(self):
        changeset = 'changesetresponse_xyz'
        boundary = 'batchresponse_abc'
        payload = (
            f'--{boundary}\r\n'
            f'Content-Type: multipart/mixed; boundary={changeset}\r\n'
            '\r\n'
            f'--{changeset}\r\n'
            'Content-Type: application/http\r\n'
            'Content-Transfer-Encoding: binary\r\n'
            '\r\n'
            'HTTP/1.1 201 Created\r\n'
            'Content-Type: application/json\r\n'
            '\r\n'
            '{"id": "new-1"}\r\n'
            f'--{changeset}--\r\n'
            f'--{boundary}--\r\n'
        )

        responses = parse_multipart(payload.encode('utf8'), f'multipart/mixed; boundary={boundary}')

        assert len(responses) == 1
        assert responses[0].status_code == CREATED
        assert responses[0].body == {'id': 'new-1'}

# ################################################################################################################################
# ################################################################################################################################

class TestBatchLive:
    """ Batches against the live test server, in both formats and both versions.
    """

    def test_multipart_reads_v4(self, business_central_server):
        _seed(business_central_server)

        client = _bc_client(business_central_server)
        responses = client.batch([_read_request('customers'), _read_request("customers('aaaa0001-0000-0000-0000-000000000001')")])
        client.close()

        assert len(responses) == 2

        assert responses[0].status_code == OK
        assert len(responses[0].body['value']) == 2

        assert responses[1].status_code == OK
        assert responses[1].body['displayName'] == 'Adatum'

    def test_multipart_changeset_v4(self, business_central_server):
        _seed(business_central_server)

        requests = [
            _read_request('customers'),
            _write_request('POST', 'customers', {'displayName': 'Batch Co'}),
        ]

        client = _bc_client(business_central_server)
        responses = client.batch(requests)
        client.close()

        assert responses[0].status_code == OK
        assert responses[1].status_code == CREATED
        assert responses[1].body['displayName'] == 'Batch Co'

        # The server recorded the batch's inner requests separately.
        batch_requests = business_central_server.last_request['batch_requests']
        assert batch_requests[0]['method'] == 'GET'
        assert batch_requests[1]['method'] == 'POST'
        assert batch_requests[1]['json'] == {'displayName': 'Batch Co'}

    def test_json_batch_v4(self, business_central_server):
        _seed(business_central_server)

        requests = [
            _read_request('customers'),
            _write_request('POST', 'customers', {'displayName': 'JSON Co'}),
        ]

        client = _bc_client(business_central_server)
        responses = client.batch(requests, format='json')
        client.close()

        assert responses[0].status_code == OK
        assert responses[1].status_code == CREATED
        assert responses[1].body['displayName'] == 'JSON Co'

    def test_multipart_v2(self, s4hana_server):
        s4hana_server.reset()
        s4hana_server.add_entities('A_SalesOrder', 'SalesOrder', [
            {'SalesOrder': '1', 'SalesOrderType': 'OR'},
        ])

        config = {
            'address': s4hana_server.service_root + '/',
            'odata_version': ODataVersion.V2,
            'auth_type': 'none',

            # SAP demands the CSRF token on the $batch POST itself too.
            'needs_csrf_token': True,
        }
        client = ODataClient(config)
        responses = client.batch([
            _read_request('A_SalesOrder'),
            _write_request('MERGE', "A_SalesOrder('1')", {'SalesOrderType': 'RE'}),
        ])
        client.close()

        assert responses[0].status_code == OK
        assert responses[0].body['d']['results'][0]['SalesOrder'] == '1'

        assert responses[1].status_code == NO_CONTENT
        assert s4hana_server.entities['A_SalesOrder']['1']['SalesOrderType'] == 'RE'

# ################################################################################################################################
# ################################################################################################################################
