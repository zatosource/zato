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
    from zato.common.typing_ import any_, anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

anydict_list = list['anydict']

# ################################################################################################################################
# ################################################################################################################################

class BasePubSubPushTestCase(unittest.TestCase):
    """ Base test case for pub/sub push delivery tests.
    """

    config = PubSubPushTestConfig

# ################################################################################################################################

    def setUp(self) -> 'None':
        """ Clean up state from prior tests so each test starts fresh.
        """

        # Remove all JSON files from each active endpoint's output directory ..
        for output_directory in self.config.endpoint_output_dirs.values():

            for entry in os.listdir(output_directory):
                if entry.endswith('.json'):
                    file_path = os.path.join(output_directory, entry)
                    os.remove(file_path)

        # .. and drain any messages sitting in the pull queue from prior tests.
        _ = self.pull_messages()

# ################################################################################################################################

    def publish(self, topic_name:'str', data:'any_', expiration:'int'=0) -> 'anydict':
        """ Publish a message to a topic using the publisher credentials.
        If expiration is non-zero, it is included as the message TTL in seconds.
        """

        # Build the URL for the topic ..
        base_url = self.config.base_url
        url = f'{base_url}/pubsub/topic/{topic_name}'

        # .. prepare the payload ..
        payload:'anydict' = {'data': data}

        if expiration:
            payload['expiration'] = expiration

        # .. build the credentials ..
        username = self.config.publisher_username
        password = self.config.publisher_password
        credentials = (username, password)

        # .. send the request ..
        response = requests.post(url, json=payload, auth=credentials)

        # .. and return the result.
        out = response.json()
        out['http_status_code'] = response.status_code

        return out

# ################################################################################################################################

    def poll_for_messages(
        self,
        topic_name:'str',
        expected_count:'int',
        timeout:'int'=30,
        ) -> 'anydict_list':
        """ Poll the output directory for a topic's HTTP receiver until the
        expected number of JSON files appear or the timeout expires.
        """

        # Set up the polling parameters ..
        output_directory = self.config.endpoint_output_dirs[topic_name]
        deadline = time.monotonic() + timeout
        file_names:'strlist' = []

        # .. poll until we have enough files or the deadline passes ..
        while time.monotonic() < deadline:

            file_names = []

            for entry in os.listdir(output_directory):
                if entry.endswith('.json'):
                    file_names.append(entry)

            file_count = len(file_names)

            if file_count >= expected_count:
                break

            time.sleep(0.5)

        # .. read all JSON files from the output directory ..
        messages = []
        file_names.sort()

        for file_name in file_names:
            file_path = os.path.join(output_directory, file_name)

            with open(file_path, 'r') as message_file:
                message = json.load(message_file)
                messages.append(message)

        # .. and return them.
        out = messages
        return out

# ################################################################################################################################

    def pull_messages(self) -> 'anydict':
        """ Retrieve messages using the pull subscription via get-messages.
        """

        # Build the URL ..
        base_url = self.config.base_url
        url = f'{base_url}/pubsub/messages/get'

        # .. build the credentials ..
        username = self.config.puller_username
        password = self.config.puller_password
        credentials = (username, password)

        # .. send the request ..
        response = requests.post(url, auth=credentials)

        # .. and return the result.
        out = response.json()
        out['http_status_code'] = response.status_code

        return out

# ################################################################################################################################

    def count_files_in_output_directory(self, topic_name:'str') -> 'int':
        """ Count JSON files in a topic's output directory without reading them.
        """

        # Look up the output directory ..
        output_directory = self.config.endpoint_output_dirs[topic_name]

        # .. count the JSON files ..
        count = 0

        for entry in os.listdir(output_directory):
            if entry.endswith('.json'):
                count += 1

        # .. and return the total.
        out = count
        return out

# ################################################################################################################################
# ################################################################################################################################
