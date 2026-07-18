# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# requests
import requests

# Zato
from zato.common.api import Alerting, SMTPMessage
from zato.common.alerting.engine import AlertTransports
from zato.common.alerting.sweep import load_rules, run_sweep
from zato.common.audit_log.api import get_audit_engine, AuditLog
from zato.common.util.api import utcnow
from zato.server.generic.api.channel_hl7_mllp import get_current_metrics
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# How long a webhook post may take before it is abandoned, in seconds.
_webhook_timeout = 10

# ################################################################################################################################
# ################################################################################################################################

class AlertingRun(AdminService):
    """ Runs one alerting sweep - the scheduler invokes this service on its interval.
    Each configured rule's collector runs over the audit database and the live channel
    metrics, and the findings are deduplicated and dispatched through each rule's action.
    Email goes out through the SMTP connection named in the job's extra data.
    """
    name = Alerting.Service

    def _get_extra(self, key:'str', context:'anydict') -> 'str':
        """ Returns one key of the scheduler job's extra data - the extra is user-editable
        in the scheduler UI, so a missing key simply means the feature it drives is off.
        """
        if value := context.get(key):
            out = value
        else:
            out = ''

        return out

# ################################################################################################################################

    def _build_transports(self, context:'anydict') -> 'AlertTransports':
        """ Wires the real delivery callables the engine dispatches through -
        SMTP for email, the server's own invoker, pub/sub and HTTP for webhooks.
        """
        smtp_conn = self._get_extra(Alerting.Extra_SMTP_Conn, context)
        from_ = self._get_extra(Alerting.Extra_From, context)

        def send_email(addresses:'strlist', subject:'str', body:'str') -> 'None':

            # Email is off until the job's extra data names an SMTP connection
            if not smtp_conn:
                self.logger.info('No SMTP connection is configured for alerting, skipping an email to `%s`', addresses)
                return

            # The email component may be disabled in server.conf
            if not self.email:
                self.logger.warning(
                    'Could not send an alerting email; is component_enabled.email set to True in server.conf?')
                return

            message = SMTPMessage()
            message.from_ = from_
            message.to = addresses
            message.subject = subject
            message.body = body

            smtp_item = self.email.smtp.get(smtp_conn, True)
            smtp_item.conn.send(message)

        def invoke_service(service_name:'str', payload:'stranydict') -> 'None':
            _ = self.server.invoke(service_name, payload)

        def publish(topic_name:'str', payload:'stranydict') -> 'None':
            _ = self.server.pubsub_redis.publish(topic_name, payload, cid=self.cid, correl_id=self.cid)

        def http_post(url:'str', payload:'stranydict') -> 'None':
            response = requests.post(url, json=payload, timeout=_webhook_timeout)
            if not response.ok:
                self.logger.warning('Alert webhook `%s` returned %s - %s', url, response.status_code, response.text)

        # Our response to produce
        out = AlertTransports()

        out.send_email = send_email
        out.invoke_service = invoke_service
        out.publish = publish
        out.http_post = http_post

        return out

# ################################################################################################################################

    def handle(self) -> 'None':

        # The job's extra data arrives as a dict - an empty extra arrives as something else,
        # e.g. an empty string or bytes, which means nothing was configured.
        context = self.request.payload

        if not isinstance(context, dict):
            context = {}

        # One reference moment for the whole sweep
        now = utcnow()

        # The rules live as generic objects in the ODB - the same rows enmasse manages
        with closing(self.odb.session()) as session:
            rules = load_rules(session, self.server.cluster_id)

        # With nothing configured there is nothing to collect
        if not rules:
            self.logger.info('Alerting sweep found no rules configured')
            return

        # The live channel metrics the feed-silent collector runs over
        metrics_by_name = get_current_metrics()

        # Where the catch-all digest goes and where the links point to
        default_to = self._get_extra(Alerting.Extra_Default_To, context)
        dashboard_url = self._get_extra(Alerting.Extra_Dashboard_URL, context)

        if default_to:
            default_email = [item.strip() for item in default_to.split(',')]
        else:
            default_email = None

        transports = self._build_transports(context)
        audit_log = AuditLog(self.server.name)
        engine = get_audit_engine()

        result = run_sweep(engine, rules, metrics_by_name, transports, audit_log, self.cid, now,
            default_email=default_email, dashboard_url=dashboard_url)

        self.logger.info('Alerting sweep ran %d rule(s) - %d finding(s), %d raised, %d deduplicated, %d dispatched',
            result.rule_count, result.finding_count, result.raised_count, result.deduplicated_count,
            len(result.dispatched))

# ################################################################################################################################
# ################################################################################################################################
