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
from zato.common.broker_message import SERVER_IPC

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

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

    def invoke(self, service:'str', data:'any_', url_path:'str', timeout:'int'=90) -> 'anydict':

        # This is where we can find the IPC server to invoke ..
        url = f'http://{self.host}:{self.port}/{url_path}'

        # .. prepare the full request ..
        data = dumps({
            'action':   SERVER_IPC.INVOKE.value,
            'username': self.username,
            'password': self.password,
            'service':  service,
            'data': data,
        })

        # .. invoke the server ..
        response = requests_post(url, data)

        # .. de-serialize the response ..
        response = loads(response.text)

        # .. and return its response.
        return response

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
