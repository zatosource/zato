# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The lines the server logs for each request - the incoming request line, the REST summary and the access log.

# stdlib
import re
from http.client import OK

# Zato
from channel_definitions import Channels, Paths, Services
from channel_suite import wait_for_log_lines

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from channel_suite import Suite
    from zato.common.typing_ import strdict

# ################################################################################################################################
# ################################################################################################################################

_user_agent = 'CustomerPortal/2.1'
_request_body = b'{"customer_id": 123}'

# ################################################################################################################################
# ################################################################################################################################

def _send(suite:'Suite') -> 'strdict':
    """ Sends a request and returns its CID along with the length of its response.
    """
    headers = {'Content-Type': 'application/json', 'User-Agent': _user_agent}
    response = suite.client.request('POST', Paths.Echo + '?customer_id=123', headers=headers, body=_request_body)

    assert response.status == OK

    out = {'cid': response.json()['cid'], 'length': str(len(response.body))}
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_incoming_request_line(suite:'Suite') -> 'None':
    request = _send(suite)
    cid = request['cid']

    lines = wait_for_log_lines(suite.environment.get_log_path('server.log'), f'REST cha \u2192 cid={cid};')
    line = lines[0]

    request_part = f'REST cha \u2192 cid={cid}; POST {Paths.Echo}?customer_id=123 name={Channels.Echo}; '
    client_part = f'service={Services.Echo}; len={len(_request_body)}; agent={_user_agent}; remote-addr=127.0.0.1:'
    expected = request_part + client_part

    assert expected in line, line
    assert re.search(r'remote-addr=127\.0\.0\.1:\d+$', line), line
    assert ' - INFO - ' in line

# ################################################################################################################################

def test_rest_summary_line(suite:'Suite') -> 'None':
    request = _send(suite)
    cid = request['cid']
    length = request['length']

    lines = wait_for_log_lines(suite.environment.get_log_path('rest.log'), f'cid={cid};')
    line = lines[0]

    pattern = re.compile(r' - INFO - \d+:Dummy - zato_rest:0 - REST cha \u2190 cid=' + re.escape(cid) +
        r'; 200 time=0:\d{2}\.\d{6}; len=' + length + '$')

    assert pattern.search(line), line

# ################################################################################################################################

def test_access_log_line(suite:'Suite') -> 'None':
    request = _send(suite)
    cid = request['cid']
    length = request['length']

    lines = wait_for_log_lines(suite.environment.get_log_path('access.log'), f' {cid}/')
    line = lines[0]

    pattern = re.compile(r' - INFO - \d+:Dummy - zato_access_log:0 - 127\.0\.0\.1 ' + re.escape(cid) +
        r'/\d+\.\d{6} "' + re.escape(Channels.Echo) + r'" \[\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4}\] "POST ' +
        re.escape(Paths.Echo) + r' HTTP/1\.1" 200 ' + length + r' "-" "' + re.escape(_user_agent) + '"$')

    assert pattern.search(line), line

# ################################################################################################################################

def test_not_found_lines(suite:'Suite') -> 'None':
    response = suite.client.get('/test/channel/no-such-path')
    text = response.text
    cid = text[text.index('CID:') + len('CID:'):-1]

    lines = wait_for_log_lines(suite.environment.get_log_path('rest.log'), f'cid={cid};')
    assert '; 404 time=' in lines[0], lines[0]

# ################################################################################################################################
# ################################################################################################################################
