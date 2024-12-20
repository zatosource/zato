# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from copy import deepcopy
from datetime import datetime, timezone
from json import loads
from tempfile import gettempdir
from unittest import main

# ciso8601
try:
    from zato.common.util.api import parse_datetime
except ImportError:
    from dateutil.parser import parse as parse_datetime

# Zato
from zato.common.pubsub import MSG_PREFIX, PUBSUB
from zato.common.util.api import new_cid
from zato.common.util.file_system import wait_for_file
from zato.common.util.open_ import open_r
from zato.common.test.rest_client import RESTClientTestCase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

_default = PUBSUB.DEFAULT

username = _default.PUBAPI_USERNAME
sec_name = _default.PUBAPI_SECDEF_NAME

# ################################################################################################################################
# ################################################################################################################################

class PubSubTestCase(RESTClientTestCase):

    needs_current_app     = False
    payload_only_messages = False

# ################################################################################################################################

    def setUp(self) -> None:
        super().setUp()
        self.rest_client.init(username=username, sec_name=sec_name)

# ################################################################################################################################

    def test_self_publish(self):

        random_data = new_cid()

        file_name_pub_sub = 'zato-unittest-pubsub-'+ random_data +'.json'
        file_name_pub_sub = os.path.join(gettempdir(), file_name_pub_sub)
        file_name_hook = file_name_pub_sub + '.hook-before-publish.json'

        request = {
            'random_data': random_data,
            'file_name': file_name_pub_sub,
        } # type: anydict

        expected_pub_sub_data = deepcopy(request)
        expected_pub_sub_data['target_needs_file'] = True

        expected_hook_data  = deepcopy(request)
        expected_hook_data['target_needs_file'] = False

        self.rest_client.api_invoke('helpers.pubsub.source', request)

        # Sleep for a moment until the files appear in the file system
        wait_for_file(file_name_pub_sub, max_wait=99)
        wait_for_file(file_name_hook, max_wait=99)

        # Attempt to read the files now ..
        with open_r(file_name_pub_sub) as f:
            pub_sub_data = f.read()

        with open_r(file_name_hook) as f:
            hook_data = f.read()

        # .. load actual JSON data ..
        pub_sub_data = loads(pub_sub_data)
        hook_data    = loads(hook_data)

        # .. and run all the tests now ..

        # Check hook data first as the message is much smaller
        self.assertDictEqual(hook_data, expected_hook_data)

        # ##

        expiration_time = pub_sub_data['expiration_time']
        expiration_time = datetime.fromtimestamp(expiration_time, tz=timezone.utc)
        expiration_time = str(expiration_time)

        expiration_time_iso = pub_sub_data['expiration_time_iso']
        expiration_time_iso = parse_datetime(expiration_time_iso).astimezone(tz=timezone.utc)
        expiration_time_iso = str(expiration_time_iso)

        # ##

        pub_time = pub_sub_data['pub_time']
        pub_time = datetime.fromtimestamp(pub_time, tz=timezone.utc)
        pub_time = str(pub_time)

        pub_time_iso = pub_sub_data['pub_time_iso']
        pub_time_iso = parse_datetime(pub_time_iso).astimezone(tz=timezone.utc)
        pub_time_iso = str(pub_time_iso)

        # ##

        recv_time = pub_sub_data['recv_time']
        recv_time = datetime.fromtimestamp(recv_time, tz=timezone.utc)
        recv_time = str(recv_time)

        recv_time_iso = pub_sub_data['recv_time_iso']
        recv_time_iso = parse_datetime(recv_time_iso).astimezone(tz=timezone.utc)
        recv_time_iso = str(recv_time_iso)

        # ##

        self.assertEqual(pub_sub_data['data_prefix'], '')
        self.assertEqual(pub_sub_data['data_prefix_short'], '')
        self.assertEqual(pub_sub_data['delivery_count'], 1)
        self.assertEqual(pub_sub_data['delivery_status'], '')
        self.assertEqual(pub_sub_data['expiration'], _default.LimitMessageExpiry)
        self.assertEqual(pub_sub_data['ext_pub_time_iso'], '')
        self.assertEqual(pub_sub_data['mime_type'], _default.MIME_TYPE)
        self.assertEqual(pub_sub_data['priority'], 5)
        self.assertEqual(pub_sub_data['server_name'], '')
        self.assertEqual(pub_sub_data['sub_pattern_matched'], 'sub=/zato/s/to/*')
        self.assertEqual(pub_sub_data['topic_name'], '/zato/s/to/helpers_pubsub_target')
        self.assertEqual(pub_sub_data['zato_ctx']['target_service_name'], 'helpers.pubsub.target')
        self.assertEqual(pub_sub_data['zato_ctx']['zato_mime_type'], 'application/vnd.zato.ps.msg')

        self.assertIsInstance(pub_sub_data['topic_id'],   int)
        self.assertIsInstance(pub_sub_data['cluster_id'], int)
        self.assertIsInstance(pub_sub_data['server_pid'], int)
        self.assertIsInstance(pub_sub_data['published_by_id'], int)

        self.assertDictEqual(pub_sub_data['data'], expected_pub_sub_data)
        self.assertEqual(pub_sub_data['pub_pattern_matched'], '')

        self.assertTrue(pub_sub_data['size'] >= 100)
        self.assertTrue(pub_sub_data['has_gd'])
        self.assertTrue(pub_sub_data['pub_msg_id'].startswith(MSG_PREFIX.MSG_ID))
        self.assertTrue(pub_sub_data['sub_key'].startswith('zpsk.srv'))

        self.assertFalse(pub_sub_data['is_in_sub_queue'])

        self.assertListEqual(pub_sub_data['deliver_to_sk'], [])
        self.assertListEqual(pub_sub_data['reply_to_sk'], [])

        # This waits until datetime_from_ms is changed so as not to require the "* 1000" multiplication,
        # i.e. until it uses datetime.fromtimestamp(ms, tz=timezone.utc)
        """
        now = datetime.now(tz=timezone.utc).isoformat()

        self.assertEqual(expiration_time, expiration_time_iso)
        self.assertEqual(pub_time, pub_time_iso)
        self.assertEqual(recv_time, recv_time_iso)

        self.assertLess(now, expiration_time_iso)
        self.assertGreater(now, pub_time_iso)
        self.assertGreater(now, recv_time_iso)
        """

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
