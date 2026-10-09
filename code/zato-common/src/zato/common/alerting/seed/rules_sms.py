# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The default alert rules of outgoing SMS connections - the two queue delivery rules of rules_queue.py over
# the sms-outgoing source.

# Zato
from zato.common.alerting.seed.rules_queue import build_queue_rules

sms_outgoing_rules = build_queue_rules('sms-outgoing', 'An outgoing SMS connection')
