# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from io import StringIO
from logging import DEBUG

# Zato
from zato.common.exception import Forbidden
from zato.server.service import AsIs, Service
from zato.server.service.internal.service import Invoke

# ################################################################################################################################

default_services_allowed = (
    'zato.pubsub.pubapi.publish-message',
    'zato.pubsub.pubapi.subscribe-wsx',
    'zato.pubsub.pubapi.unsubscribe',
    'zato.pubsub.resume-wsx-subscription',
)

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

class PubInputLogger(InputLogger):
    """ Same as InputLogger but has a publicly available name
    """
    name = 'pub.helpers.input-logger'

# ################################################################################################################################

class RawRequestLogger(Service):
    """ Writes out self.request.raw_request to server logs.
    """
    name = 'pub.helpers.raw-request-logger'

    def handle(self):
        self.logger.info('Received request: `%s`', self.request.raw_request)

# ################################################################################################################################

class IBMMQLogger(Service):
    """ Writes out self.request.raw_request to server logs.
    """
    name = 'pub.helpers.ibm-mq-logger'

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

    def before_handle(self):

        # Configure Django if this service is used - not that we are not doing it
        # globally for the module because the configuration takes some milliseconds
        # the first time around (but later on it is not significant).

        # Django
        import django
        from django.conf import settings

        # Configure Django settings when the module is picked up
        if not settings.configured:
            settings.configure()
            django.setup()

    def set_html_payload(self, ctx, template):

        # Django
        from django.template import Context, Template

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
    services_allowed = []

    class SimpleIO:
        input_required = 'service',
        input_optional = AsIs('request'),
        output_optional = 'sub_key',
        skip_empty_keys = True

    def handle(self, _pubsub_prefix='zato.pubsub.pubapi', _default_allowed=default_services_allowed):

        # Local aliases
        input = self.request.input
        service = input.service

        if service \
           and service not in _default_allowed \
           and service not in self.services_allowed:
                self.logger.warn('Service `%s` is not among %s', service, self.services_allowed)
                raise Forbidden(self.cid)

        # We need to special-pub/sub subscriptions
        # because they will require calling self.pubsub on behalf of the current WSX connection.
        if service == 'zato.pubsub.pubapi.subscribe-wsx':
            topic_name = input.request['topic_name']
            unsub_on_wsx_close = input.request.get('unsub_on_wsx_close', True)
            sub_key = self.pubsub.subscribe(
                topic_name, use_current_wsx=True, unsub_on_wsx_close=unsub_on_wsx_close, service=self)
            self.response.payload.sub_key = sub_key

        else:
            self.wsgi_environ['zato.orig_channel'] = self.channel
            response = self.invoke(service, self.request.input.request, wsgi_environ=self.wsgi_environ)
            self.response.payload = response

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

# ################################################################################################################################
