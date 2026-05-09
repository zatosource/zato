# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# prometheus_client
from prometheus_client import Counter, Histogram

# ################################################################################################################################
# ################################################################################################################################

# Metrics
try:
    zato_http_requests_total = Counter(
        'zato_http_requests_total', 'Total HTTP requests', ['channel_name', 'status_code'])
    zato_http_request_duration_seconds = Histogram(
        'zato_http_request_duration_seconds', 'HTTP request duration', ['channel_name'])
except ValueError:
    from prometheus_client import REGISTRY
    zato_http_requests_total = REGISTRY._names_to_collectors['zato_http_requests_total']
    zato_http_request_duration_seconds = REGISTRY._names_to_collectors['zato_http_request_duration_seconds']

# ################################################################################################################################
# ################################################################################################################################
