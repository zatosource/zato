# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime
from logging import getLogger, INFO
from traceback import format_exc

# pytz
from pytz import UTC

# tzlocal
from tzlocal import get_localzone

# Zato
from zato.common.api import NO_REMOTE_ADDRESS
from zato.common.util.api import make_cid_public, new_cid_server
from zato.common.util.time_ import utcnow

# prometheus_client
from prometheus_client import Counter, Histogram

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, stranydict
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

Access_Log_Date_Time_Format = '%d/%b/%Y:%H:%M:%S %z'
_has_log_info = logger.isEnabledFor(INFO)

# ################################################################################################################################
# ################################################################################################################################

class HTTPHandler:
    """ Handles incoming HTTP requests.
    """

    def on_http_request(
        self:'ParallelServer', # type: ignore
        http_environ,     # type: stranydict
        _new_cid=new_cid_server, # type: callable_
        _local_zone=get_localzone(), # type: ignore
        _utcnow=utcnow, # type: ignore
        _INFO=INFO, # type: int
        _UTC=UTC,   # type: any_
        _Access_Log_Date_Time_Format=Access_Log_Date_Time_Format, # type: str
        _no_remote_address=NO_REMOTE_ADDRESS, # type: str
        _cid_components_no=4,
        **kwargs:'any_'
    ) -> 'tuple':
        """ Handles incoming HTTP requests.
        Returns (status_str, headers_dict, body_bytes).
        """

        user_agent = http_environ.get('HTTP_USER_AGENT', '(None)')
        cid = kwargs.get('cid', _new_cid())

        request_ts_utc = _utcnow()

        http_environ['zato.local_tz'] = _local_zone
        http_environ['zato.request_timestamp_utc'] = request_ts_utc
        http_environ['zato.request_timestamp'] = request_ts_local = request_ts_utc.replace(tzinfo=_UTC).astimezone(_local_zone)

        http_environ['zato.http.response.headers'] = {}

        if self.needs_x_zato_cid:
            pub_cid = make_cid_public(cid)
            http_environ['zato.http.response.headers']['X-Zato-CID'] = pub_cid

        remote_addr = _no_remote_address
        for name in self.client_address_headers:
            remote_addr = http_environ.get(name)
            if remote_addr:
                break

        http_environ['zato.http.remote_addr'] = remote_addr

        try:
            payload = self.worker_store.request_dispatcher.dispatch(
                cid,
                request_ts_utc,
                http_environ,
                self.worker_store,
                user_agent,
                remote_addr,
            ) or b''

        except Exception:
            error_msg = '`%s` Exception caught `%s`' % (cid, format_exc())
            logger.error(error_msg)
            http_environ['zato.http.response.status'] = '500 Internal Server Error'
            payload = error_msg if self.return_tracebacks else self.default_error_message

        channel_item = http_environ.get('zato.channel_item')

        if channel_item:
            channel_name = channel_item.get('name', '-')
        else:
            channel_name = '-'

        if isinstance(payload, str):
            payload = payload.encode('utf-8')

        status = http_environ.get('zato.http.response.status', '200 OK')
        response_headers = {k: str(v) for k, v in http_environ['zato.http.response.headers'].items()}

        status_code = status.split()[0]
        response_size = len(payload)

        if self.needs_access_log:
            if self.needs_all_access_log or http_environ['PATH_INFO'] not in self.access_log_ignore:

                self.access_logger_log(
                    _INFO,
                    '',
                    None, # type: ignore
                    None,
                    {
                        'remote_ip': remote_addr,
                        'cid_resp_time': '%s/%s' % (cid, (_utcnow() - request_ts_utc).total_seconds()),
                        'channel_name': channel_name,
                        'req_timestamp_utc': request_ts_utc.strftime(_Access_Log_Date_Time_Format),
                        'req_timestamp': request_ts_local.strftime(_Access_Log_Date_Time_Format),
                        'method': http_environ['REQUEST_METHOD'],
                        'path': http_environ['PATH_INFO'],
                        'http_version': http_environ['SERVER_PROTOCOL'],
                        'status_code': status_code,
                        'response_size': response_size,
                        'user_agent': user_agent,
                })

        delta = _utcnow() - request_ts_utc
        response_time = delta.total_seconds()

        _ = zato_http_requests_total.labels(channel_name=channel_name, status_code=status_code).inc()
        _ = zato_http_request_duration_seconds.labels(channel_name=channel_name).observe(response_time)

        if _has_log_info:
            if not any(http_environ['PATH_INFO'].startswith(p) for p in self.rest_log_ignore):
                msg = f'REST cha ← cid={cid}; {status_code} time={delta}; len={response_size}'
                logger.info(msg)

        return (status, response_headers, payload)

# ################################################################################################################################
# ################################################################################################################################
