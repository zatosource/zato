# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import time
import unittest

# requests
import requests

# local
from config import PubSubPushTestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class BasePubSubPushTestCase(unittest.TestCase):
    """ Base test case for pub/sub push delivery tests.
    """

    config = PubSubPushTestConfig

# ################################################################################################################################

    def publish(self, topic_name:'str', data:'any_') -> 'anydict':
        """ Publish a message to a topic using the publisher credentials.
        """
        url = f'{self.config.base_url}/pubsub/topic/{topic_name}'
        payload = {'data': data}
        auth = (self.config.publisher_username, self.config.publisher_password)

        response = requests.post(url, json=payload, auth=auth)

        result = response.json()
        result['http_status_code'] = response.status_code

        return result

# ################################################################################################################################

    def poll_for_messages(
        self,
        topic_name:'str',
        expected_count:'int',
        timeout:'int'=30,
        ) -> 'list[anydict]':
        """ Poll the output directory for a topic's HTTP receiver until the
        expected number of JSON files appear or the timeout expires.
        """
        output_directory = self.config.endpoint_output_dirs[topic_name]
        deadline = time.monotonic() + timeout
        file_names:'list[str]' = []

        while time.monotonic() < deadline:

            file_names = []

            for entry in os.listdir(output_directory):
                if entry.endswith('.json'):
                    file_names.append(entry)

            file_count = len(file_names)

            if file_count >= expected_count:
                break

            time.sleep(0.5)

        # Read all JSON files from the output directory
        messages = []
        file_names.sort()

        for file_name in file_names:
            file_path = os.path.join(output_directory, file_name)

            with open(file_path, 'r') as message_file:
                message = json.load(message_file)
                messages.append(message)

        return messages

# ################################################################################################################################

    def pull_messages(self) -> 'anydict':
        """ Retrieve messages using the pull subscription via get-messages.
        """
        url = f'{self.config.base_url}/pubsub/messages/get'
        auth = (self.config.puller_username, self.config.puller_password)

        response = requests.post(url, auth=auth)
        result = response.json()
        result['http_status_code'] = response.status_code

        return result

# ################################################################################################################################

    def count_files_in_output_directory(self, topic_name:'str') -> 'int':
        """ Count JSON files in a topic's output directory without reading them.
        """
        output_directory = self.config.endpoint_output_dirs[topic_name]

        count = 0

        for entry in os.listdir(output_directory):
            if entry.endswith('.json'):
                count += 1

        return count

# ################################################################################################################################
# ################################################################################################################################
