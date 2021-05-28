# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import socket

# Requests
from requests.sessions import Session

# Zato
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

class Client:
    def __init__(self):
        self.address = None # type: tuple
        self.username = ''
        self.password = ''
        self.auth = None # type: tuple

# ################################################################################################################################

    def init(self):
        self.socket = socket.socket(type=socket.SOCK_STREAM)
        self.socket.connect(self.address)

# ################################################################################################################################

    def push(self, data):
        # type: (dict) -> None
        data = dumps(data)
        self.socket.send(data.encode('utf8') + b'\n')

    def close(self):
        self.socket.close()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    address = ('127.0.0.1', 44011)
    username = 'aaa'
    password = 'bbb'

    client = Client()
    client.address = address
    client.username = username
    client.password = password
    client.init()

    data = {
        'action': '107400',
        'data': {}
    }

    n = 60_000
    total = 0

    from datetime import datetime
    utcnow = datetime.utcnow

    for x in range(1):

        for idx in range(n):
            elem = str(idx)
            event = {
                'action': '107400',
                'data': {
                    'id': elem + utcnow().isoformat(),
                    'cid': 'cid.' + elem,
                    'timestamp': '2021-05-12T07:07:01.4841' + elem,

                    'source_type': 'zato.server' + elem,
                    'source_id': 'server1' + elem,

                    'object_type': elem,
                    'object_id': elem,

                    'source_type': elem,
                    'source_id': elem,

                    'recipient_type': elem,
                    'recipient_id': elem,

                    'total_time_ms': x,
                }
            }
            client.push(event)
            total += 1
            #print('TOTAL', total)

    client.close()

    import time
    time.sleep(0.1)

# ################################################################################################################################
# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

# stdlib
from datetime import datetime

# Amazon Ion
import amazon.ion.simpleion as ion

# gevent
from gevent import spawn, socket

# geventhttpclient
from geventhttpclient import HTTPClient
from geventhttpclient.url import URL

# Requests
from requests import post
from requests.sessions import Session

# Zato
from zato.common.json_internal import dumps
from zato.common.util import spawn_greenlet
from zato.server.service import Service

address = ('127.0.0.1', 44011)

socket = socket.socket(type=socket.SOCK_STREAM)
socket.connect(address)

utcnow = datetime.utcnow

'''
# ################################################################################################################################
# ################################################################################################################################

class _Session(Session):
    def merge_environment_settings(self, *ignored_args, **ignored_kwargs):
        return {'verify': None, 'proxies': None, 'stream': None,
                'cert': None}

# ################################################################################################################################
# ################################################################################################################################

#session = _Session()

url = URL('http://localhost:44011')
client = HTTPClient(url.host, concurrency=1500)
'''

# ################################################################################################################################
# ################################################################################################################################

class PasswordResetCreateToken(Service):
    def handle(self):

        current_app = 'CRM'
        remote_addr = '127.0.0.1'
        user_agent = self.request.http.user_agent

        # This can be either username or email,
        # in this particular case it is a username.
        credential = 'my.username'

        # This will never return an explicit indication
        # whether the credential was valid or not.
        self.sso.password_reset.create_token(
            self.cid, credential, current_app, remote_addr, user_agent)

# ################################################################################################################################
# ################################################################################################################################

class PasswordResetAccessToken(Service):
    def handle(self):

        elem = '111'
        x = 111

        data = {
            'action': '107400',
            'data': {
                'id': elem + utcnow().isoformat(),
                'cid': 'cid.' + elem,
                'timestamp': '2021-05-12T07:07:01.4841' + elem,

                'source_type': 'zato.server' + elem,
                'source_id': 'server1' + elem,

                'object_type': elem,
                'object_id': elem,

                'source_type': elem,
                'source_id': elem,

                'recipient_type': elem,
                'recipient_id': elem,

                'total_time_ms': x,
            }
        }

        data = 'aaa' * 50 #dumps(data)

        with self.server.user_ctx_lock:
            socket.send(data.encode('utf8') + b'\n')

        #self.logger.warn('QQQ %s', self.server.pid)

        #spawn(session.post, 'http://localhost:44011', '', auth=('aaa', 'bbb'))

        #spawn(client.post, '/', '{}')

        #response = client.post('/', '{}')

        #print(111, response.get_code())

        #self.logger.warn('QQQ %s', client)

        '''
        current_app = 'CRM'
        remote_addr = '127.0.0.1'
        user_agent = self.request.http.user_agent

        # Frontend reads it from the link that the user clicked
        token = '5k339rv63q82er5wq9qgfw9xkd'

        # The reset key, along with the initial token, can be used
        # to change the password.
        reset_key = self.sso.password_reset.access_token(
            self.cid, token, current_app, remote_addr, user_agent)

        # Return the reset key to our caller
        self.response.payload = {'reset_key': reset_key}
        '''

# ################################################################################################################################
# ################################################################################################################################
'''
