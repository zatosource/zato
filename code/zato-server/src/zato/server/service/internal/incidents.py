# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from traceback import format_exc

# Zato
from zato.common.api import Incidents, SMTPMessage
from zato.common.alerting.rendering import render_alert_template, Template_Dir_Name, Template_Email_Body, \
    Template_Email_Subject, Template_Slack, Template_Teams
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditLog, AuditOutcome
from zato.common.audit_log.common import AuditSource
from zato.common.incidents.diagnosis import build_prompt, parse_diagnosis
from zato.common.incidents.evidence import build_evidence, collect_audit_trail
from zato.common.incidents.skill import load_skill
from zato.common.incidents.store import IncidentStore
from zato.common.util.api import utcnow
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The name diagnoses are stored under - the unique part is the id of the alert
# they explain, so one alert produces one diagnosis, not one per sweep.
_diagnosis_name_prefix = 'alert.'

# ################################################################################################################################
# ################################################################################################################################

class Diagnose(AdminService):
    """ Turns an alert about a failing connection into a diagnosed alert - collects
    the evidence, has the LLM diagnose it against the connection's diagnostic skill,
    stores the diagnosis next to the alert and notifies through the default
    notification connections. A rule outcome whose action says diagnose points here.
    """
    name = Incidents.Service_Diagnose

    def handle(self) -> 'None':

        # The payload arrives from the alerting engine - anything else means a manual
        # invocation with nothing to work from.
        payload = self.request.payload

        if not isinstance(payload, dict):
            self.logger.info('Alert diagnosis received no alert payload, nothing to do')
            return

        source = payload['source']
        object_name = payload['object_name']

        # Only sources with a diagnostic skill of their own can be diagnosed ..
        skill = load_skill(source)

        if not skill:
            self.logger.info('No diagnostic skill exists for source `%s`, skipping `%s`', source, object_name)
            return

        # .. and one alert produces one diagnosis, not one per sweep.
        store = IncidentStore(self.odb.session, self.server.cluster_id)
        name = _diagnosis_name_prefix + str(payload['alert_id'])

        if store.exists(name):
            self.logger.info('A diagnosis already exists for `%s`, skipping `%s`', name, object_name)
            return

        # The rule's own configuration - which LLM diagnoses and where notifications deliver.
        action_config = payload['action_config']

        # Collect the evidence pack ..
        conn_config = self._get_connection_config(source, object_name)
        engine = get_audit_engine()

        audit_trail = collect_audit_trail(engine, source, object_name, Incidents.Evidence_Max_Events)

        alert = {
            'rule': payload['rule'],
            'kind': payload['kind'],
            'message': payload['message'],
            'severity': payload['severity'],
            'count': payload['count'],
        }

        evidence = build_evidence(alert, conn_config, audit_trail)

        # .. have the LLM diagnose it ..
        diagnosis = self._diagnose(skill.instructions, evidence, action_config)

        # .. store the diagnosis next to the alert ..
        now = utcnow()

        details = {
            'object_name': object_name,
            'source': source,
            'rule': payload['rule'],
            'alert_id': payload['alert_id'],
            'count': payload['count'],
            'severity': payload['severity'],
            'message': payload['message'],
            'link': payload['link'],
            'evidence': evidence,
            'diagnosis': diagnosis['diagnosis'],
            'confidence': diagnosis['confidence'],
            'remediation': diagnosis['remediation'],
            'is_parsed': diagnosis['is_parsed'],
            'created_iso': now.isoformat(),
        }

        store.create(name, details)

        # .. leave a trace in the audit log ..
        audit_log = AuditLog(self.server.name)

        _ = audit_log.insert(source, AuditEvent.Alert_Diagnosed, object_name,
            cid=self.cid, outcome=AuditOutcome.OK, data=payload['message'])

        self.logger.info('Alert `%s` diagnosed for `%s` (%s)', name, object_name, payload['rule'])

        # .. and tell the people the alert goes to.
        self._notify(details, action_config)

# ################################################################################################################################

    def _get_connection_config(self, source:'str', object_name:'str') -> 'anydict':
        """ The connection's configuration for the evidence pack, looked up through
        the facade the alert's source names. Sources without an in-process config
        facade contribute the name alone - the audit trail carries the errors either
        way, which is what the diagnosis mostly reads.
        """
        if source == AuditSource.REST_Outgoing:
            out = self.out.rest[object_name].config

        elif source == AuditSource.LLM:
            out = self.llm.conn_dict[object_name]

        else:
            out = {'name': object_name}

        return out

# ################################################################################################################################

    def _get_llm_connection(self, action_config:'anydict') -> 'str':
        """ The LLM connection the diagnosis goes through - the rule's own when it names
        one, otherwise the default connection, as long as it exists and is active.
        An empty name means no LLM is available and the alert goes out undiagnosed.
        """

        # The rule's action_config is user-editable - a missing key means the rule
        # names no connection of its own.
        if llm_connection := action_config.get(Incidents.Config_LLM_Connection):
            return llm_connection

        # The default connection ships inactive with placeholder credentials,
        # so it only answers once a person points it at a real model.
        default_name = Incidents.LLM_Connection_Name

        if default_name not in self.llm.conn_dict:
            return ''

        item = self.llm.conn_dict[default_name]

        if not item['is_active']:
            return ''

        return default_name

# ################################################################################################################################

    def _diagnose(self, instructions:'str', evidence:'stranydict', action_config:'anydict') -> 'stranydict':
        """ Runs the LLM diagnosis, or produces an empty one when no LLM connection
        is available - the alert still goes out so a person can look at the evidence.
        """
        llm_connection = self._get_llm_connection(action_config)

        if not llm_connection:

            self.logger.info('No LLM connection is available, storing the alert without a diagnosis')

            out:'stranydict' = {
                'diagnosis': '',
                'confidence': '',
                'remediation': None,
                'is_parsed': False,
            }

            return out

        prompt = build_prompt(instructions, evidence)
        response = self.llm[llm_connection].invoke(prompt)

        out = parse_diagnosis(response['text'])
        return out

# ################################################################################################################################

    def _build_template_context(self, details:'stranydict', action_config:'anydict') -> 'stranydict':
        """ The context the notification templates render with - the same shape the
        alerting engine builds, with the diagnosis keys filled in and the link
        prefixed with the dashboard's address when one is configured.
        """
        link = details['link']

        # A link the sweep already made absolute stays as it is - only a bare
        # dashboard path still needs the dashboard's own address in front of it.
        if link.startswith('/'):
            if dashboard_url := action_config.get(Incidents.Config_Dashboard_URL):
                link = dashboard_url.rstrip('/') + link

        out = {
            'alert_id': details['alert_id'],
            'rule': details['rule'],
            'kind': '',
            'source': details['source'],
            'object_name': details['object_name'],
            'message': details['message'],
            'link': link,
            'severity': details['severity'],
            'count': details['count'],
            'action_config': action_config,
            'diagnosis': details['diagnosis'],
            'confidence': details['confidence'],
            'remediation': details['remediation'],
        }

        return out

# ################################################################################################################################

    def _get_template_dir(self) -> 'str':
        """ The server's own template directory - the bundled defaults answer
        until an environment created before the templates existed is recreated.
        """
        out = os.path.join(self.server.repo_location, Template_Dir_Name)

        if not os.path.isdir(out):
            out = ''

        return out

# ################################################################################################################################

    def _notify(self, details:'stranydict', action_config:'anydict') -> 'None':
        """ Sends the diagnosed alert through every notification connection that is
        configured and active. A transport that is not set up is skipped with
        a log line - an unconfigured notification never breaks the diagnosis.
        """
        context = self._build_template_context(details, action_config)
        template_dir = self._get_template_dir()
        conn_name = Incidents.Notification_Conn_Name

        transports = (
            ('Slack', self._notify_slack),
            ('Microsoft Teams', self._notify_teams),
            ('email', self._notify_email),
        )

        for label, transport in transports:

            # The default connections start out inactive with placeholder details,
            # so any of them may fail until a person fills them in.
            try:
                transport(conn_name, context, template_dir, action_config)
            except Exception:
                self.logger.warning('Could not send an alert notification through %s; e:`%s`', label, format_exc())

# ################################################################################################################################

    def _notify_slack(self, conn_name:'str', context:'stranydict', template_dir:'str', action_config:'anydict') -> 'None':

        # Without a channel in the rule's action_config, Slack notifications are off.
        channel = action_config.get(Incidents.Config_Slack_Channel)

        if not channel:
            return

        # A connection that does not exist or is inactive sends nothing.
        if conn_name not in self.slack.conn_dict:
            self.logger.info('No Slack connection `%s` exists, skipping the notification', conn_name)
            return

        item = self.slack.conn_dict[conn_name]

        if not item['is_active']:
            self.logger.info('Slack connection `%s` is inactive, skipping the notification', conn_name)
            return

        text = render_alert_template(Template_Slack, context, template_dir)
        _ = self.slack.send(conn_name, channel, text)

# ################################################################################################################################

    def _notify_teams(self, conn_name:'str', context:'stranydict', template_dir:'str', action_config:'anydict') -> 'None':

        # Without a target in the rule's action_config, Teams notifications are off.
        to = action_config.get(Incidents.Config_Teams_To)

        if not to:
            return

        # A connection that does not exist or is inactive sends nothing.
        if conn_name not in self.microsoft.teams.conn_dict:
            self.logger.info('No Microsoft Teams connection `%s` exists, skipping the notification', conn_name)
            return

        item = self.microsoft.teams.conn_dict[conn_name]

        if not item['is_active']:
            self.logger.info('Microsoft Teams connection `%s` is inactive, skipping the notification', conn_name)
            return

        # Teams messages are HTML.
        text = render_alert_template(Template_Teams, context, template_dir)
        html = text.replace('\n', '<br/>')
        _ = self.microsoft.teams.send(conn_name, to, html)

# ################################################################################################################################

    def _notify_email(self, conn_name:'str', context:'stranydict', template_dir:'str', action_config:'anydict') -> 'None':

        # Without recipients in the rule's action_config, email notifications are off.
        email_to = action_config.get(Incidents.Config_Email_To)

        if not email_to:
            return

        # The email component may be disabled in server.conf.
        if not self.email:
            self.logger.info('The email component is not enabled, skipping the notification')
            return

        smtp_item = self.email.smtp.get(conn_name, True)

        if not smtp_item.config['is_active']:
            self.logger.info('SMTP connection `%s` is inactive, skipping the notification', conn_name)
            return

        addresses = []

        for address in email_to.split(','):
            addresses.append(address.strip())

        message = SMTPMessage()
        message.from_ = action_config.get(Incidents.Config_Email_From)
        message.to = addresses
        message.subject = render_alert_template(Template_Email_Subject, context, template_dir)
        message.body = render_alert_template(Template_Email_Body, context, template_dir)

        smtp_item.conn.send(message)

# ################################################################################################################################
# ################################################################################################################################
