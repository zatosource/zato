# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads

# requests
from requests import post as requests_post

# Zato
from zato.common.api import IPC as Common_IPC
from zato.common.broker_message import SERVER_IPC
from zato.common.typing_ import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class IPCResponseMeta:

    cid:   'str'
    is_ok: 'bool'

    service: 'str'
    request: 'any_'

    cluster_name: 'str'
    server_name:  'str'
    server_pid:   'int'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class IPCResponse:
    data: 'anydict | anylist | None'
    meta: 'IPCResponseMeta'

# ################################################################################################################################
# ################################################################################################################################

class IPCClient:

    def __init__(
        self,
        host,     # type: str
        port,     # type: int
        username, # type: str
        password, # type: str
    ) -> 'None':

        self.host = host
        self.port = port
        self.username = username
        self.password = password

# ################################################################################################################################

    def invoke(
        self,
        service,    # type: str
        request,    # type: any_
        url_path,   # type: str
        *,
        cluster_name, # type: str
        server_name,  # type: str
        server_pid,   # type: int
        timeout=90,   # type: int
    ) -> 'IPCResponse':

        # This is where we can find the IPC server to invoke ..
        url = f'http://{self.host}:{self.port}/{url_path}'

        # .. prepare the full request ..
        data = dumps({
            'action':   SERVER_IPC.INVOKE.value,
            'username': self.username,
            'password': self.password,
            'service':  service,
            'data': request,
        })

        # .. invoke the server ..
        response = requests_post(url, data)

        # .. de-serialize the response ..
        response = loads(response.text)

        ipc_response = IPCResponse()
        ipc_response.data = response['response'] or None
        ipc_response.meta = IPCResponseMeta()
        ipc_response.meta.cid = response['cid']
        ipc_response.meta.is_ok = response['status'] == Common_IPC.Status_OK
        ipc_response.meta.cluster_name = cluster_name
        ipc_response.meta.server_name = server_name
        ipc_response.meta.server_pid = server_pid

        # .. and return its response.
        return ipc_response

# ################################################################################################################################

def main():

    # stdlib
    import logging

    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    logger = logging.getLogger(__name__)

    host = '127.0.0.1'
    port = 17050
    username = 'test.username'
    password = 'test.password'

    service = 'pub.zato.ping'
    request = {'Hello': 'World'}

    client = IPCClient(host, port, username, password)
    response = client.invoke(service, request)

    logger.info('Response -> %s', response)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
