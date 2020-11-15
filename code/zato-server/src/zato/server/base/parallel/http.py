# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from http.client import INTERNAL_SERVER_ERROR, responses
from logging import getLogger, INFO
from traceback import format_exc

# pytz
from pytz import UTC

# tzlocal
from tzlocal import get_localzone

# Python 2/3 compatibility
from future.utils import iteritems
from past.builtins import unicode

# Zato
from zato.common.api import NO_REMOTE_ADDRESS
from zato.common.util.api import new_cid

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

ACCESS_LOG_DT_FORMAT = '%d/%b/%Y:%H:%M:%S %z'

# ################################################################################################################################

class HTTPHandler(object):
    """ Handles incoming HTTP requests.
    """
    def on_wsgi_request(self, wsgi_environ, start_response, _new_cid=new_cid, _local_zone=get_localzone(),
        _utcnow=datetime.utcnow, _INFO=INFO, _UTC=UTC, _ACCESS_LOG_DT_FORMAT=ACCESS_LOG_DT_FORMAT,
        _no_remote_address=NO_REMOTE_ADDRESS, **kwargs):
        """ Handles incoming HTTP requests.
        """
        cid = kwargs.get('cid', _new_cid())
        request_ts_utc = _utcnow()
        wsgi_environ['zato.local_tz'] = _local_zone
        wsgi_environ['zato.request_timestamp_utc'] = request_ts_utc
        wsgi_environ['zato.request_timestamp'] = request_ts_local = request_ts_utc.replace(tzinfo=_UTC).astimezone(_local_zone)

        wsgi_environ['zato.http.response.headers'] = {'X-Zato-CID': cid}

        remote_addr = _no_remote_address
        for name in self.client_address_headers:
            remote_addr = wsgi_environ.get(name)
            if remote_addr:
                break

        wsgi_environ['zato.http.remote_addr'] = remote_addr

        try:
            payload = self.request_dispatcher_dispatch(cid, request_ts_utc, wsgi_environ, self.worker_store) or b''

        # Any exception at this point must be a server-side error
        except Exception:
            tb = format_exc()
            wsgi_environ['zato.http.response.status'] = b'%s %s' % (INTERNAL_SERVER_ERROR, str(responses[INTERNAL_SERVER_ERROR]))
            error_msg = b'`%s` Exception caught `%s`' % (cid, tb)
            logger.error(error_msg)
            payload = error_msg if self.return_tracebacks else self.default_error_message
            raise

        channel_item = wsgi_environ.get('zato.channel_item')

        if channel_item:
            # For access log
            channel_name = channel_item.get('name', '-')
        else:
            # 404 because could not find the channel, or
            # 405 because this was an invalid HTTP method
            channel_name = '-'

        start_response(wsgi_environ['zato.http.response.status'], iteritems(wsgi_environ['zato.http.response.headers']))

        if isinstance(payload, unicode):
            payload = payload.encode('utf-8')

        if self.needs_access_log:

            # Either log all HTTP requests or make sure that current path
            # is not in a list of paths to ignore.
            if self.needs_all_access_log or wsgi_environ['PATH_INFO'] not in self.access_log_ignore:

                self.access_logger_log(_INFO, '', None, None, {
                    'remote_ip': remote_addr,
                    'cid_resp_time': '%s/%s' % (cid, (_utcnow() - request_ts_utc).total_seconds()),
                    'channel_name': channel_name,
                    'req_timestamp_utc': request_ts_utc.strftime(_ACCESS_LOG_DT_FORMAT),
                    'req_timestamp': request_ts_local.strftime(_ACCESS_LOG_DT_FORMAT),
                    'method': wsgi_environ['REQUEST_METHOD'],
                    'path': wsgi_environ['PATH_INFO'],
                    'http_version': wsgi_environ['SERVER_PROTOCOL'],
                    'status_code': wsgi_environ['zato.http.response.status'].split()[0],
                    'response_size': len(payload),
                    'user_agent': wsgi_environ.get('HTTP_USER_AGENT', '(None)'),
                })

        return [payload]
