# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from io import StringIO
from logging import DEBUG

# Django
import django
from django.conf import settings
from django.template import Context, Template

# Zato
from zato.common.exception import Forbidden
from zato.server.service import AsIs, Service
from zato.server.service.internal.service import Invoke

# Configure Django settings when the module is picked up
if not settings.configured:
    settings.configure()
    django.setup()

# ################################################################################################################################

class Echo(Service):
    """ Copies request over to response.
    """
    def handle(self):
        self.response.payload = self.request.raw_request

# ################################################################################################################################

class InputLogger(Service):
    """ Writes out all input data to server logs.
    """
    def handle(self):
        pass

    def finalize_handle(self):
        self.log_input()

# ################################################################################################################################

class RawRequestLogger(Service):
    """ Writes out self.request.raw_request to server logs.
    """
    name = 'helpers.raw-request-logger'

    def handle(self):
        self.logger.info('Received request: `%s`', self.request.raw_request)

# ################################################################################################################################

class IBMMQLogger(Service):
    """ Writes out self.request.raw_request to server logs.
    """
    name = 'helpers.ibm-mq-logger'

    def handle(self):
        template = """
***********************
IBM MQ message received
***********************
MsgId: `{msg_id}`
CorrelId: `{correlation_id}`
Timestamp: `{timestamp}`
PutDate: `{put_date}`
PutTime: `{put_time}`
ReplyTo: `{reply_to}`
MQMD: `{mqmd!r}`
-----------------------
Data: `{data}`
***********************
"""

        mq = self.request.ibm_mq
        na = 'n/a'

        try:
            msg_id = mq.msg_id.decode('ascii')
        except UnicodeDecodeError:
            msg_id = repr(mq.msg_id)

        if mq.correlation_id:
            try:
                correlation_id = mq.correlation_id.decode('ascii')
            except UnicodeDecodeError:
                correlation_id = repr(mq.correlation_id)
        else:
            correlation_id = na

        info = {
            'msg_id': msg_id,
            'correlation_id': correlation_id,
            'timestamp': mq.timestamp,
            'put_date': mq.put_date,
            'put_time': mq.put_time,
            'reply_to': mq.reply_to or na,
            'mqmd': str(mq.mqmd).splitlines(),
            'data': self.request.raw_request,
        }

        msg = template.format(**info)
        msg_out = msg.decode('utf8')

        self.logger.info(msg_out)

# ################################################################################################################################

class JSONRawRequestLogger(RawRequestLogger):
    """ Same as RawRequestLogger but returns a JSON response.
    """
    def handle(self):
        super(JSONRawRequestLogger, self).handle()
        self.response.payload = {'status': 'OK'}

# ################################################################################################################################

class SIOInputLogger(Service):
    """ Writes out all SIO input parameters to server logs.
    """
    def handle(self):
        self.logger.info('%r', self.request.input)

# ################################################################################################################################

class HTMLService(Service):
    def set_html_payload(self, ctx, template):

        # Generate HTML and return response
        c = Context(ctx)
        t = Template(template)
        payload = t.render(c).encode('utf-8')

        self.logger.debug('Ctx:[%s]', ctx)
        self.logger.debug('Payload:[%s]', payload)

        if self.logger.isEnabledFor(DEBUG):
            buff = StringIO()
            self.logger.debug(buff.getvalue())
            buff.close()

        self.response.payload = payload
        self.response.content_type = 'text/html; charset=utf-8'

# ################################################################################################################################

class TLSLogger(Service):
    """ Logs details of client TLS certificates.
    """
    def handle(self):
        has_tls = False
        for k, v in sorted(self.wsgi_environ.items()):
            if k.startswith('HTTP_X_ZATO_TLS_'):
                has_tls = True
                self.logger.info('%r: %r', k, v)

        if not has_tls:
            self.logger.warn('No HTTP_X_ZATO_TLS_* headers found')

# ################################################################################################################################

class WebSocketsGateway(Service):
    """ Dispatches incoming WebSocket requests to target services.
    """
    name = 'helpers.web-sockets-gateway'

    class SimpleIO:
        input_required = ('service',)
        input_optional = (AsIs('request'),)

    def handle(self):
        self.wsgi_environ['zato.orig_channel'] = self.channel
        self.response.payload = self.invoke(self.request.input.service, self.request.input.request,
            wsgi_environ=self.wsgi_environ)

# ################################################################################################################################

class WebSocketsPubSubGateway(Service):
    """ Dispatches incoming WebSocket publish/subscribe requests to target services.
    """
    name = 'helpers.web-sockets-pub-sub-gateway'

    class SimpleIO:
        input_required = ('service',)
        input_optional = (AsIs('request'),)

    def handle(self):

        # Make sure this is one of allowed services that we are to invoke
        if self.request.input.service not in self.server.fs_server_config.pubsub.wsx_gateway_service_allowed:
            raise Forbidden(self.cid)

        # All good, we can invoke this service
        else:
            self.response.payload = self.invoke(self.request.input.service, self.request.input.request,
                wsgi_environ=self.wsgi_environ)

# ################################################################################################################################

class ServiceGateway(Invoke):
    """ Service to invoke other services through.
    """
    name = 'helpers.service-gateway'
