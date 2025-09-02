# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    from zato.common.pubsub.perftest.python_.progress_tracker import ProgressTracker

# ################################################################################################################################
# ################################################################################################################################

class Client:
    """ Base class for pub/sub clients.
    """
    def __init__(self,
        progress_tracker:'ProgressTracker',
        client_id:'int'=0,
        reqs_per_second:'float'=1.0,
        max_topics:'int'=3
    ) -> 'None':

        self.client_id = client_id
        self.reqs_per_second = reqs_per_second
        self.max_topics = max_topics
        self.progress_tracker = progress_tracker

# ################################################################################################################################

    def _before_start(self) -> 'None':
        """ Called before starting the invoker.
        """
        pass

# ################################################################################################################################

    def _get_config(self) -> 'anydict':
        """ Get configuration from environment variables.
        """
        base_url = os.environ['Zato_Test_PubSub_OpenAPI_URL']
        username = os.environ['Zato_Test_PubSub_OpenAPI_Username']
        password = os.environ['Zato_Test_PubSub_OpenAPI_Password']
        reqs_per_second = self.reqs_per_second
        max_topics = self.max_topics

        return {
            'base_url': base_url,
            'username': username,
            'password': password,
            'max_topics': max_topics,
            'reqs_per_second': reqs_per_second,
        }

# ################################################################################################################################

    def start(self) -> 'None':
        raise NotImplementedError()

# ################################################################################################################################
