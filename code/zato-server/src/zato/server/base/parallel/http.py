# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
from logging import getLogger

# tzlocal
from tzlocal import get_localzone

# Zato
from zato.common.util.api import make_cid_public, new_cid_server

# prometheus_client
from prometheus_client import Counter, Histogram

# Rust
from zato_server_core import handle_http_request

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato_rest')

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

_local_tz_offset_secs = int(datetime.now(timezone.utc).astimezone(get_localzone()).utcoffset().total_seconds())

# ################################################################################################################################
# ################################################################################################################################

class HTTPHandler:
    """ Handles incoming HTTP requests.
    """

    _make_cid_public = staticmethod(make_cid_public)

    def on_http_request(
        self:'ParallelServer', # type: ignore
        http_environ,     # type: stranydict
        **kwargs:'any_'
    ) -> 'tuple':
        return handle_http_request(self, http_environ, new_cid_server, _local_tz_offset_secs, **kwargs)

# ################################################################################################################################
# ################################################################################################################################
