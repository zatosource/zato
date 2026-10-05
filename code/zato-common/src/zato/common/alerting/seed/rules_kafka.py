# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The default alert rules of outgoing Kafka connections - the queue delivery pair alone, built from rules_queue.py over
# the kafka-outgoing source. Whether a send went through is what Kafka's own confirmations say, so there is no error
# rate or latency to read off the audit log, and the two depths are read off the connection itself.

# Zato
from zato.common.alerting.seed.rules_queue import build_queue_rules

kafka_outgoing_rules = build_queue_rules('kafka-outgoing', 'An outgoing Kafka connection')
