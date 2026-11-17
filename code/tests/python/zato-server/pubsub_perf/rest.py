# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from base64 import b64encode
from typing import NamedTuple
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# Zato
from pubsub_perf.config import PerfConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class HTTPResult(NamedTuple):
    """ The status code and the parsed body of one HTTP response.
    """
    status_code: 'int'
    body: 'anydict'

# ################################################################################################################################
# ################################################################################################################################

def post_json(path:'str', username:'str', password:'str', payload:'any_') -> 'HTTPResult':
    """ Sends one request to the REST interface of the server with basic authentication and returns
    its status code and its parsed body.
    """
    url = f'{PerfConfig.base_url}{path}'

    # Serialize the request ..
    serialized = json.dumps(payload)
    body = serialized.encode()

    # .. build the credentials ..
    credentials = f'{username}:{password}'
    credentials = credentials.encode()
    credentials = b64encode(credentials)
    credentials = credentials.decode()

    request = Request(url, data=body, method='POST')
    request.add_header('Authorization', f'Basic {credentials}')
    request.add_header('Content-Type', 'application/json')

    # .. send the request, with an error status read in the same way as a success ..
    try:
        with urlopen(request) as response:
            response_data = response.read()
            status_code = response.status
    except HTTPError as error:
        response_data = error.read()
        status_code = error.code

    # .. and parse the response.
    if response_data:
        response_body = json.loads(response_data)
    else:
        response_body = {}

    out = HTTPResult(status_code, response_body)
    return out

# ################################################################################################################################
# ################################################################################################################################
