# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from httplib import INTERNAL_SERVER_ERROR, responses
from logging import getLogger, INFO
from traceback import format_exc

# pytz
from pytz import UTC

# tzlocal
from tzlocal import get_localzone

# Zato
from zato.common.util import new_cid

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

ACCESS_LOG_DT_FORMAT = '%d/%b/%Y:%H:%M:%S %z'

# ################################################################################################################################

class HTTPHandler(object):
    """ Handles incoming HTTP requests.
    """
    def on_wsgi_request(self, wsgi_environ, start_response, _new_cid=new_cid, _local_zone=get_localzone(),
        _utcnow=datetime.utcnow, _INFO=INFO, _UTC=UTC, _ACCESS_LOG_DT_FORMAT=ACCESS_LOG_DT_FORMAT, **kwargs):
        """ Handles incoming HTTP requests.
        """
        cid = kwargs.get('cid', _new_cid())
        request_ts_utc = _utcnow()
        wsgi_environ['zato.local_tz'] = _local_zone
        wsgi_environ['zato.request_timestamp_utc'] = request_ts_utc
        wsgi_environ['zato.request_timestamp'] = request_ts_local = request_ts_utc.replace(tzinfo=_UTC).astimezone(_local_zone)

        wsgi_environ['zato.http.response.headers'] = {'X-Zato-CID': cid}

        remote_addr = '(None)'
        for name in self.client_address_headers:
            remote_addr = wsgi_environ.get(name)
            if remote_addr:
                break

        wsgi_environ['zato.http.remote_addr'] = remote_addr

        try:
            payload = self.request_dispatcher_dispatch(cid, request_ts_utc, wsgi_environ, self.worker_store) or b''

        # Any exception at this point must be our fault
        except Exception, e:
            tb = format_exc(e)
            wsgi_environ['zato.http.response.status'] = b'%s %s' % (INTERNAL_SERVER_ERROR, responses[INTERNAL_SERVER_ERROR])
            error_msg = b'`%s` Exception caught `%s`' % (cid, tb)
            logger.error(error_msg)
            payload = error_msg if self.return_tracebacks else self.default_error_message
            raise

        channel_item = wsgi_environ['zato.http.channel_item']

        if channel_item:

            # For access log
            channel_name = channel_item.get('name', '-')

            # Note that this call is asynchronous and we do it the last possible moment.
            if wsgi_environ['zato.http.channel_item'].get('audit_enabled'):
                self.worker_store.request_dispatcher.url_data.audit_set_response(cid, payload, wsgi_environ)

        else:
            # 404 Not Found since we cannot find the channel
            channel_name = '-'

        start_response(wsgi_environ['zato.http.response.status'],
            ((k.encode('utf-8'), v.encode('utf-8')) for k, v in wsgi_environ['zato.http.response.headers'].iteritems()))

        if isinstance(payload, unicode):
            payload = payload.encode('utf-8')

        if self.needs_access_log:

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
