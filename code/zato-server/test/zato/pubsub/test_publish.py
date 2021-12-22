# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import datetime, time, timezone
from json import loads
from tempfile import gettempdir
from unittest import main

# ciso8601
from ciso8601 import parse_datetime

# Zato
from zato.common.pubsub import PUBSUB
from zato.common.util.api import new_cid
from zato.common.util.file_system import wait_for_file
from zato.common.util.open_ import open_r
from zato.common.test.rest_client import RESTClientTestCase
from zato.common.util.time_ import local_tz

# ################################################################################################################################
# ################################################################################################################################

_default = PUBSUB.DEFAULT

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestCase(RESTClientTestCase):

    needs_current_app     = False
    payload_only_messages = False

    def setUp(self) -> None:
        super().setUp()
        self.rest_client.init()

# ################################################################################################################################

    def test_self_publish(self):

        random_data = new_cid()

        file_name = 'zato-unittest-pubsub-'+ random_data +'.json'
        file_name = os.path.join(gettempdir(), file_name)

        request = {
            'random_data': random_data,
            'file_name': file_name,
        }

        self.rest_client.api_invoke('helpers.pubsub.source', request)

        # Sleep for a moment until the file appears in the file system
        wait_for_file(file_name)

        # Attempt to read the file now ..
        with open_r(file_name) as f:
            data = f.read()

        # .. load its actual JSON data ..
        data = loads(data)

        # .. and run all the tests now ..

        self.assertEqual(data['data_prefix'], '')
        self.assertEqual(data['data_prefix_short'], '')
        self.assertEqual(data['delivery_count'], 0)
        self.assertEqual(data['delivery_status'], '')
        self.assertEqual(data['expiration'], _default.EXPIRATION)
        self.assertEqual(data['ext_pub_time_iso'], '')
        self.assertEqual(data['mime_type'], _default.MIME_TYPE)
        self.assertEqual(data['priority'], 5)
        self.assertEqual(data['server_name'], '')
        self.assertEqual(data['sub_pattern_matched'], 'sub=/zato/s/to/*')
        self.assertEqual(data['topic_name'], '/zato/s/to/helpers_pubsub_target')
        self.assertEqual(data['zato_ctx']['target_service_name'], 'helpers.pubsub.target')
        self.assertEqual(data['zato_ctx']['zato_mime_type'], 'application/vnd.zato.ps.msg')

        self.assertIsInstance(data['topic_id'],   int)
        self.assertIsInstance(data['cluster_id'], int)
        self.assertIsInstance(data['server_pid'], int)
        self.assertIsInstance(data['published_by_id'], int)

        self.assertDictEqual(data['data'], request)
        self.assertDictEqual(data['pub_pattern_matched'], {})

        self.assertTrue(data['size'] >= 112)
        self.assertTrue(data['has_gd'])
        self.assertTrue(data['pub_msg_id'].startswith('zpsm'))
        self.assertTrue(data['sub_key'].startswith('zpsk.srv'))

        self.assertFalse(data['is_in_sub_queue'])

        self.assertListEqual(data['deliver_to_sk'], [])
        self.assertListEqual(data['reply_to_sk'], [])

        expiration_time     = data['expiration_time']
        expiration_time_iso = data['expiration_time_iso']

        expiration_time     = datetime.fromtimestamp(expiration_time, tz=timezone.utc)
        expiration_time_iso = parse_datetime(expiration_time_iso).astimezone(tz=timezone.utc)

        expiration_time = str(expiration_time)
        expiration_time_iso = str(expiration_time_iso)

        print(111, expiration_time)
        print(222, expiration_time_iso)

        self.assertEqual(expiration_time, expiration_time_iso)


        # "expiration_time": 3787633752.932831,
        # "expiration_time_iso": "2090-01-09T08:29:12.932831",

        '''
        {
            x "cluster_id": 0,
            x "data": {
                "file_name": "/tmp/zato-unittest-pubsub-2d21d577d32af62c6ae54285.json",
                "random_data": "2d21d577d32af62c6ae54285"
            },
            x "data_prefix": "",
            x "data_prefix_short": "",
            x "deliver_to_sk": [],
            x "delivery_count": 0,
            x "delivery_status": "",
            x "expiration": 2147483647000,
            "expiration_time": 3787633752.932831,
            "expiration_time_iso": "2090-01-09T08:29:12.932831",
            x "ext_pub_time_iso": "",
            x "has_gd": true,
            x "is_in_sub_queue": false,
            x "mime_type": "text/plain",
            x "priority": 5,
            x "pub_msg_id": "zpsm80eafdf4a10a76a8a4a3080f",
            x "pub_pattern_matched": {},
            "pub_time": 1640150105.932831,
            "pub_time_iso": "2021-12-22T05:15:05.932831",
            x "published_by_id": 1,
            "recv_time": 1640150106.1367662,
            x "reply_to_sk": [],
            x "server_name": "",
            x "server_pid": 0,
            x "size": 114,
            x "sub_key": "zpsk.srv.ccd1ea",
            x "sub_pattern_matched": "sub=/zato/s/to/*",
            x "topic_id": 0,
            x "topic_name": "/zato/s/to/helpers_pubsub_target",
            x "zato_ctx": {
            x    "target_service_name": "helpers.pubsub.target",
            x    "zato_mime_type": "application/vnd.zato.ps.msg"
            }
        }
        '''

# ################################################################################################################################
# ################################################################################################################################


if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
