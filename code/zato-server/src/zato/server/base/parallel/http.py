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

# prometheus_client
from prometheus_client import Counter, Histogram

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, list_, stranydict
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
    def on_wsgi_request(
        self:'ParallelServer', # type: ignore
        wsgi_environ,     # type: stranydict
        start_response,   # type: callable_
        _new_cid=new_cid_server, # type: callable_
        _local_zone=get_localzone(), # type: ignore
        _utcnow=datetime.utcnow, # type: ignore
        _INFO=INFO, # type: int
        _UTC=UTC,   # type: any_
        _Access_Log_Date_Time_Format=Access_Log_Date_Time_Format, # type: str
        _no_remote_address=NO_REMOTE_ADDRESS, # type: str
        _cid_components_no=4,
        **kwargs:'any_'
    ) -> 'list_[bytes]':
        """ Handles incoming HTTP requests.
        """

        # This is reusable
        user_agent = wsgi_environ.get('HTTP_USER_AGENT', '(None)')

        # We need a correlation ID first ..
        cid = kwargs.get('cid', _new_cid())

        # .. this is a timestamp of when the request was received ..
        request_ts_utc = _utcnow()

        # .. basic context details ..
        wsgi_environ['zato.local_tz'] = _local_zone
        wsgi_environ['zato.request_timestamp_utc'] = request_ts_utc
        wsgi_environ['zato.request_timestamp'] = request_ts_local = request_ts_utc.replace(tzinfo=_UTC).astimezone(_local_zone)

        # .. this is always needed ..
        wsgi_environ['zato.http.response.headers'] = {}

        # .. but returning X-Zato-CID is optional ..
        if self.needs_x_zato_cid:

            # .. and also note, we don't return the instance name at all ..
            pub_cid = make_cid_public(cid)
            wsgi_environ['zato.http.response.headers']['X-Zato-CID'] = pub_cid

        # .. try to extract a remote address ..
        remote_addr = _no_remote_address
        for name in self.client_address_headers:
            remote_addr = wsgi_environ.get(name)
            if remote_addr:
                break

        # .. do assign the potentially extracted address for later use ..
        wsgi_environ['zato.http.remote_addr'] = remote_addr

        # .. try to handle the request now ..
        try:

            logger.info('*' * 80)
            logger.info('HTTP DISPATCHER %s', hex(id(self.worker_store.request_dispatcher)))
            logger.info('*' * 80)

            # .. this is the call that obtains a response ..
            payload = self.worker_store.request_dispatcher.dispatch(
                cid,
                request_ts_utc,
                wsgi_environ,
                self.worker_store,
                user_agent,
                remote_addr,
            ) or b''

        # .. any exception at this point must be a server-side error ..
        except Exception:
            error_msg = '`%s` Exception caught `%s`' % (cid, format_exc())
            logger.error(error_msg)
            wsgi_environ['zato.http.response.status'] = b'500 Internal Server Error'
            payload = error_msg if self.return_tracebacks else self.default_error_message
            raise

        channel_item = wsgi_environ.get('zato.channel_item')

        if channel_item:
            # For access log
            channel_name = channel_item.get('name', '-')
        else:
            # 404 because we could not find the channel, or
            # 405 because this was an invalid HTTP method
            channel_name = '-'

        start_response(wsgi_environ['zato.http.response.status'], wsgi_environ['zato.http.response.headers'].items())

        if isinstance(payload, str):
            payload = payload.encode('utf-8')

        # .. this is reusable ..
        status_code = wsgi_environ['zato.http.response.status'].split()[0]
        response_size = len(payload)

        # .. this goes to the access log ..
        if self.needs_access_log:

            # .. either log all HTTP requests or make sure that current path ..
            # .. is not in a list of paths to ignore ..
            if self.needs_all_access_log or wsgi_environ['PATH_INFO'] not in self.access_log_ignore:

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
                        'method': wsgi_environ['REQUEST_METHOD'],
                        'path': wsgi_environ['PATH_INFO'],
                        'http_version': wsgi_environ['SERVER_PROTOCOL'],
                        'status_code': status_code,
                        'response_size': response_size,
                        'user_agent': user_agent,
                })

        # .. how long it took to produce the response ..
        delta = _utcnow() - request_ts_utc
        response_time = delta.total_seconds()

        # Update metrics
        _ = zato_http_requests_total.labels(channel_name=channel_name, status_code=status_code).inc()
        _ = zato_http_request_duration_seconds.labels(channel_name=channel_name).observe(response_time)

        # .. this goes to the server log ..
        if _has_log_info:
            if not wsgi_environ['PATH_INFO'] in self.rest_log_ignore:
                # .. log information about what we are returning ..
                msg = f'REST cha ← cid={cid}; {status_code} time={delta}; len={response_size}'
                logger.info(msg)

        # Now, return the response to our caller.
        return [payload]

# ################################################################################################################################
# ################################################################################################################################
