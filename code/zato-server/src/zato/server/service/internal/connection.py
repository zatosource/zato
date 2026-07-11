# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import HTTP_SOAP, SchedulerLink
from zato.common.util.api import utcnow
from zato.server.connection.http_soap.invocation import deliver_to_callback
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

_health_check = HTTP_SOAP.HealthCheck

# How many decimal places a response time is rounded to
_response_time_precision = 2

# ################################################################################################################################
# ################################################################################################################################

class HealthCheckRun(AdminService):
    """ Invoked by the scheduler on behalf of any connection with a health check configured - pings
    the connection and delivers the outcome to the configured callback. Generic across connection
    types, starting with outgoing REST and SOAP.
    """
    name = _health_check.Dispatch_Service

    def handle(self) -> 'None':

        # The scheduler job carries the connection's identity and callback config in its extra data
        context = self.request.payload

        conn_name = context[_health_check.Extra_Conn_Name]
        conn_type = context[_health_check.Extra_Conn_Type]

        callback_type = context[_health_check.Field_Callback_Type]
        callback_name = context[_health_check.Field_Callback_Name]
        notify_on = context[_health_check.Field_Notify_On]

        # Both outgoing REST and SOAP resolve to an HTTPSOAPWrapper, which knows how to ping itself
        if conn_type == SchedulerLink.ConnType.SOAP_Outgoing:
            wrapper = self.out.soap[conn_name].conn
        else:
            wrapper = self.out.plain_http[conn_name].conn

        # Time the ping - an exception means the connection is down, a non-2xx response means it is unhealthy
        start = utcnow()
        error = ''

        try:
            response = wrapper.ping(self.cid, return_response=True)
            is_ok = response.ok
            if not is_ok:
                error = f'{response.status_code} {response.reason}'
        except Exception as e:
            is_ok = False
            error = str(e)

        response_time_ms = round((utcnow() - start).total_seconds() * 1000, _response_time_precision)

        self.logger.info('Health check of `%s` (%s) -> ok=%s in %s ms%s',
            conn_name, conn_type, is_ok, response_time_ms, f'; error={error}' if error else '')

        # A failures-only health check keeps quiet about a healthy connection
        if notify_on == _health_check.NotifyOn.Failures and is_ok:
            return

        # Nothing to deliver to without a fully configured callback
        if not callback_type:
            return
        if not callback_name:
            return

        outcome = {
            'conn_name': conn_name,
            'conn_type': conn_type,
            'is_ok': is_ok,
            'response_time_ms': response_time_ms,
            'error': error,
        }

        deliver_to_callback(self.server, self.cid, callback_type, callback_name, outcome)

# ################################################################################################################################
# ################################################################################################################################
