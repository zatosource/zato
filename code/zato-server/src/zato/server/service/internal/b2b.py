# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import AS2, SMTPMessage
from zato.common.as2.alerting import build_digest, collect_findings, record_alerts
from zato.common.audit_log.api import AuditLog
from zato.common.util.api import utcnow
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The service returning our own keystore, whose signing chain the expiry check runs on.
_keystore_service = 'zato.channel.as2.keystore.get'

# ################################################################################################################################
# ################################################################################################################################

class B2BAlerting(AdminService):
    """ Runs one B2B alerting sweep - overdue MDNs, overdue X12 acknowledgments, expiring
    certificates and missing ship notices become alert-raised audit events and one email
    digest per run, sent through the SMTP connection named in the job's extra data.
    """
    name = AS2.Alerting.Service

    def _get_extra(self, key:'str', context:'anydict') -> 'str':
        """ Returns one key of the scheduler job's extra data - the extra is user-editable
        in the scheduler UI, so a missing key simply means the feature it drives is off.
        """
        if key in context:
            out = context[key]
        else:
            out = ''

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

        # Everything the sweep runs on - the partner configuration and our own signing chain.
        configs = list(self.server.config_manager.outconn_as2.values())

        keystore = self.invoke(_keystore_service, skip_response_elem=True)
        own_cert_chain = keystore['as2_signing_cert_chain']

        findings = collect_findings(configs, now, own_cert_chain=own_cert_chain, server_name=self.server.name)

        # A clean sweep raises nothing at all.
        if not findings:
            self.logger.info('B2B alerting sweep found nothing to report')
            return

        # Every finding becomes an alert-raised event first, so the alerting history
        # exists per partner no matter if the digest can go out.
        audit_log = AuditLog(self.server.name)
        record_alerts(audit_log, findings, cid=self.cid)

        self.logger.info('B2B alerting sweep raised %d finding(s)', len(findings))

        # The digest goes out only when the job's extra data names an SMTP connection.
        smtp_conn = self._get_extra(AS2.Alerting.Extra_SMTP_Conn, context)

        if not smtp_conn:
            self.logger.info('No SMTP connection is configured for B2B alerting, skipping the digest')
            return

        # The email component may be disabled in server.conf.
        if not self.email:
            self.logger.warning('Could not send the B2B alerting digest; ' \
                'is component_enabled.email set to True in server.conf?')
            return

        from_ = self._get_extra(AS2.Alerting.Extra_From, context)
        to = self._get_extra(AS2.Alerting.Extra_To, context)
        dashboard_url = self._get_extra(AS2.Alerting.Extra_Dashboard_URL, context)

        subject, body = build_digest(findings, dashboard_url)

        message = SMTPMessage()
        message.from_ = from_
        message.to = to
        message.subject = subject
        message.body = body

        self.email.smtp.get(smtp_conn, True).conn.send(message)

        self.logger.info('B2B alerting digest sent through `%s` to `%s`', smtp_conn, to)

# ################################################################################################################################
# ################################################################################################################################
