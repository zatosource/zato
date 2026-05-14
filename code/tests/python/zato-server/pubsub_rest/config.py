# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# ################################################################################################################################
# ################################################################################################################################

class TestConfig:

    base_url = os.environ.get('Zato_PubSub_Base_Url', 'http://localhost:17010')

    user1_username = os.environ.get('Zato_PubSub_User1', 'user.1')
    user1_password = os.environ.get('Zato_PubSub_User1_Password', 'password.1')

    user2_username = os.environ.get('Zato_PubSub_User2', 'user.2')
    user2_password = os.environ.get('Zato_PubSub_User2_Password', 'password.2')

    # user.3 has valid credentials but no subscriptions
    user3_username = os.environ.get('Zato_PubSub_User3', 'user.3')
    user3_password = os.environ.get('Zato_PubSub_User3_Password', 'password.3')

    topic_allowed = os.environ.get('Zato_PubSub_Topic_Allowed', 'demo.1')
    topic_forbidden = os.environ.get('Zato_PubSub_Topic_Forbidden', 'forbidden.topic')

# ################################################################################################################################
# ################################################################################################################################
