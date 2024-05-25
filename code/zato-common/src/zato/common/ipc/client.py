# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps, loads

# requests
from requests import post as requests_post

# Zato
from zato.common.api import IPC as Common_IPC
from zato.common.broker_message import SERVER_IPC
from zato.common.util.config import get_url_protocol_from_config_item
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
        use_tls:  'bool',
        host:     'str',
        port:     'int',
        username: 'str',
        password: 'str',
    ) -> 'None':

        self.api_protocol = get_url_protocol_from_config_item(use_tls)
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
        source_server_name, # type: str
        source_server_pid,  # type: int
    ) -> 'IPCResponse':

        # This is where we can find the IPC server to invoke ..
        url = f'{self.api_protocol}://{self.host}:{self.port}/{url_path}'

        # .. prepare the full request ..
        dict_data = {
            'source_server_name': source_server_name,
            'source_server_pid':  source_server_pid,
            'action':   SERVER_IPC.INVOKE.value,
            'service':  service,
            'data': request,
        }

        # .. serialize it into JSON ..
        data = dumps(dict_data)

        # .. build query string parameters to be used in the call ..
        params = {
            '_source_server_name': source_server_name,
            '_source_server_pid':  source_server_pid,
        }

        # .. append the business data too but skip selected ones ..
        for key, value in (request or {}).items():

            # .. skip selected keys ..
            for name in ['password', 'secret', 'token']:
                if name in key:
                    include_value = False
                    break
            else:
                include_value = True

            # .. append the keys with values depending on whether we want to pass them on or not ..
            value = value if include_value else '******'

            # .. make sure there is not too much information to keep the query string short ..
            if isinstance(value, str):
                value = value[:30]

            # .. now, do append the new item ..
            if False:
                params[key] = value

        # .. build our credentials ..
        auth = (self.username, self.password)

        # .. invoke the server ..
        response = requests_post(url, data, params=params, auth=auth)

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

    client = IPCClient(False, host, port, username, password)
    response = client.invoke(service, request)

    logger.info('Response -> %s', response)

# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
