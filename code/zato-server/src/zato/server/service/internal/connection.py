# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import HTTP_SOAP, SchedulerLink
from zato.common.util.api import utcnow
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
    the connection. The ping writes its request and response pair to the audit log under the connection's
    health source, which is what the alerting engine reads, so a check's outcome reaches people through
    the connection's alerts. Generic across connection types - outgoing REST, SOAP and FHIR.
    """
    name = _health_check.Dispatch_Service

    def handle(self) -> 'None':

        # The scheduler job carries the connection's identity in its extra data
        context = self.request.payload

        conn_name = context[_health_check.Extra_Conn_Name]
        conn_type = context[_health_check.Extra_Conn_Type]

        # Outgoing REST and SOAP resolve to an HTTPSOAPWrapper and outgoing FHIR to its own wrapper,
        # each of which knows how to ping itself and to write the ping under its health source
        if conn_type == SchedulerLink.ConnType.SOAP_Outgoing:
            wrapper = self.out.soap[conn_name].conn
        elif conn_type == SchedulerLink.ConnType.FHIR_Outgoing:
            wrapper = self._config_manager.outconn_hl7_fhir[conn_name].conn
        else:
            wrapper = self.out.plain_http[conn_name].conn

        # Time the ping - an exception means the connection is down, a non-2xx response means it is unhealthy.
        # The ping is written whether or not the connection's own audit log is on, because a check nobody can see is not a check.
        start = utcnow()
        error = ''

        try:
            response = wrapper.ping(self.cid, return_response=True, needs_audit=True)
            is_ok = response.ok
            if not is_ok:
                error = f'{response.status_code} {response.reason}'
        except Exception as e:
            is_ok = False
            error = str(e)

        response_time_ms = round((utcnow() - start).total_seconds() * 1000, _response_time_precision)

        self.logger.info('Health check of `%s` (%s) -> ok=%s in %s ms%s',
            conn_name, conn_type, is_ok, response_time_ms, f'; error={error}' if error else '')

# ################################################################################################################################
# ################################################################################################################################
