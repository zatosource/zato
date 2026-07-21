# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

# The topology of the system-level performance test - 1,000 push queues spread
# over 200 topics, delivering into 500 distinct target services, each service
# being the push target of two subscriptions.

Topic_Count = 200
Subs_Per_Topic = 5
Sub_Count = Topic_Count * Subs_Per_Topic
Service_Count = 500

# How many messages the publishers pump in total - each publish fans out
# to Subs_Per_Topic deliveries, so the expected delivery total is five times this.
Message_Count = 6_000
Expected_Deliveries = Message_Count * Subs_Per_Topic

# How many concurrent publisher threads pump the messages.
Publisher_Thread_Count = 30

# Every n-th publish of each thread goes through the service facade
# (self.pubsub.publish) instead of the REST channel.
Facade_Publish_Every = 10

# ################################################################################################################################

# Name templates shared by the enmasse generator, the deployed services and the test.

Topic_Name_Template = 'system.perf.topic.{:04d}'
Sub_Security_Template = 'test.system.perf.sub.{:04d}'
Service_Name_Template = 'test.system.perf.recv-{:04d}'

Publisher_Username = 'test.system.perf.publisher'

# A topic with no subscribers, used to measure publish latency during the drain
# without changing the expected delivery total.
Latency_Topic_Name = 'system.perf.latency'

# ################################################################################################################################
# ################################################################################################################################

class TestConfig:

    base_url:'str' = ''
    invoke_password:'str' = ''

    publisher_username:'str' = ''
    publisher_password:'str' = ''

    server_directory:'str' = ''

# ################################################################################################################################
# ################################################################################################################################
