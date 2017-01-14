# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from httplib import INTERNAL_SERVER_ERROR, responses
from logging import getLogger
from traceback import format_exc

# arrow
from arrow import utcnow

# pytz
from pytz import UTC

# tzlocal
from tzlocal import get_localzone

# Zato
from zato.common import ACCESS_LOG_DT_FORMAT
from zato.common.util import new_cid

logger = getLogger(__name__)

# ################################################################################################################################

class HTTPHandler(object):
    """ Handles incoming HTTP requests.
    """
    def on_wsgi_request(self, wsgi_environ, start_response, _new_cid=new_cid,
        _get_localzone=get_localzone, _utcnow=utcnow,  **kwargs):
        """ Handles incoming HTTP requests.
        """
        cid = kwargs.get('cid', _new_cid())
        now = _utcnow()

        wsgi_environ['zato.local_tz'] = _get_localzone()
        wsgi_environ['zato.request_timestamp_utc'] = now

        local_dt = wsgi_environ['zato.request_timestamp_utc'].replace(tzinfo=UTC).astimezone(wsgi_environ['zato.local_tz'])
        wsgi_environ['zato.request_timestamp'] = wsgi_environ['zato.local_tz'].normalize(local_dt)

        wsgi_environ['zato.http.response.headers'] = {'X-Zato-CID': cid}

        remote_addr = '(None)'
        for name in self.client_address_headers:
            remote_addr = wsgi_environ.get(name)
            if remote_addr:
                break

        wsgi_environ['zato.http.remote_addr'] = remote_addr

        try:
            payload = self.worker_store.request_dispatcher.dispatch(cid, now, wsgi_environ, self.worker_store) or b''

        # Any exception at this point must be our fault
        except Exception, e:
            tb = format_exc(e)
            wsgi_environ['zato.http.response.status'] = b'{} {}'.format(INTERNAL_SERVER_ERROR, responses[INTERNAL_SERVER_ERROR])
            error_msg = b'[{0}] Exception caught [{1}]'.format(cid, tb)
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

        headers = [(k.encode('utf-8'), v.encode('utf-8')) for k, v in wsgi_environ['zato.http.response.headers'].items()]
        start_response(wsgi_environ['zato.http.response.status'], headers)

        if isinstance(payload, unicode):
            payload = payload.encode('utf-8')

        if self.needs_access_log:

            self.access_logger.info('', extra = {
                'remote_ip': wsgi_environ['zato.http.remote_addr'],
                'cid_resp_time': '%s/%s' % (cid, (utcnow() - wsgi_environ['zato.request_timestamp_utc']).total_seconds()),
                'channel_name': channel_name,
                'req_timestamp_utc': wsgi_environ['zato.request_timestamp_utc'].strftime(ACCESS_LOG_DT_FORMAT),
                'req_timestamp': wsgi_environ['zato.request_timestamp'].strftime(ACCESS_LOG_DT_FORMAT),
                'method': wsgi_environ['REQUEST_METHOD'],
                'path': wsgi_environ['PATH_INFO'],
                'http_version': wsgi_environ['SERVER_PROTOCOL'],
                'status_code': wsgi_environ['zato.http.response.status'].split()[0],
                'response_size': len(payload),
                'user_agent': wsgi_environ.get('HTTP_USER_AGENT', '(None)'),
            })

        return [payload]
