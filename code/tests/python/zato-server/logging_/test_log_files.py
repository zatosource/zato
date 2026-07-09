# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import OK
from urllib.request import Request, urlopen

# Zato - conftest
import conftest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class TestLogFiles:
    """ The log files the documentation describes must exist and the access log
    must record requests in the Apache-style format.
    """

    def test_log_files_exist(self, zato_server:'anydict') -> 'None':

        logs_dir = os.path.join(zato_server['server_dir'], 'logs')

        for file_name in ('server.log', 'access.log', 'rest.log', 'audit-pii.log'):
            log_path = os.path.join(logs_dir, file_name)
            assert os.path.isfile(log_path), f'Expected log file not found: {log_path}'

# ################################################################################################################################

    def test_ping_appears_in_access_log(self, zato_server:'anydict') -> 'None':

        # Make one more ping request so there is guaranteed fresh content to look for ..
        host = zato_server['host']
        server_port = zato_server['server_port']

        request = Request(f'http://{host}:{server_port}/zato/ping', method='GET')
        with urlopen(request, timeout=5) as response:
            assert response.status == OK

        # .. the request must appear in the access log in the Apache-style format,
        # .. with the method, path, protocol and status code all present.
        contents = conftest.wait_for_log_content(
            zato_server['server_dir'], 'access.log', '"GET /zato/ping HTTP/1.1" 200')

        # .. and the line must name the channel that served the request.
        for line in contents.splitlines():
            if '"GET /zato/ping HTTP/1.1" 200' in line:
                assert '"zato.ping"' in line, f'Expected the channel name in: {line}'
                break

# ################################################################################################################################
# ################################################################################################################################
