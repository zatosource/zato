# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Requests
from requests.sessions import Session

# Zato
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

class Client:
    def __init__(self):
        self.address = ''
        self.username = ''
        self.password = ''
        self.auth = None # type: tuple
        self.session = None # type: Session

# ################################################################################################################################

    def init(self):
        self.auth = (self.username, self.password)
        self.session = Session()

# ################################################################################################################################

    def push(self, data):
        # type: (dict) -> None
        data = dumps(data)
        self.session.post(self.address, data, auth=self.auth)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    address = 'http://localhost:44011/api'
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

    n = 400_000
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
            print('TOTAL', total)

# ################################################################################################################################
# ################################################################################################################################
