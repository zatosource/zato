# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.api import Incidents
from zato.common.alerting.engine import defaults_from_dict, dispatch_action, Empty_Explanation
from zato.common.alerting.model import new_finding, new_rule
from zato.common.alerting.names import get_llm_conn_name
from zato.common.alerting.rendering import Template_Dir_Name
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditLog, AuditOutcome
from zato.common.audit_log.common import AuditSource
from zato.common.incidents.explanation import build_prompt, parse_explanation
from zato.common.incidents.evidence import build_evidence, collect_audit_trail
from zato.common.incidents.skill import load_skill
from zato.common.incidents.store import IncidentStore
from zato.common.util.api import utcnow
from zato.server.alerting_transports import build_alert_transports
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The name explanations are stored under - the unique part is the id of the alert
# they explain, so one alert produces one explanation, not one per sweep.
_explanation_name_prefix = 'alert.'

# ################################################################################################################################
# ################################################################################################################################

class Explain(AdminService):
    """ Explains one alert and delivers it - the alerting engine hands over every alert
    of a ruleset whose Use LLM switch is on, before the rule's own action runs. The service
    collects the evidence, has the LLM explain it against the connection's explanation
    skill, stores the explanation next to the alert and then runs the rule's action
    through the engine itself, with the explanation in the notification. An alert the LLM
    cannot explain - no skill for its source, no LLM connection - is delivered all the same,
    without the explanation paragraph.
    """
    name = Incidents.Service_Explain

    def handle(self) -> 'None':

        # The payload arrives from the alerting engine - anything else means a manual
        # invocation with nothing to work from.
        payload = self.request.payload

        if not isinstance(payload, dict):
            self.logger.info('Alert explanation received no alert payload, nothing to do')
            return

        source = payload['source']
        object_name = payload['object_name']

        explanation = self._get_explanation(payload, source, object_name)

        # .. and the rule's own action delivers the alert, explained or not.
        self._deliver(payload, explanation)

# ################################################################################################################################

    def _get_explanation(self, payload:'stranydict', source:'str', object_name:'str') -> 'stranydict':
        """ The explanation of one alert - the stored one when the alert was explained
        before, a new one from the LLM otherwise, and the empty one for a source
        without an explanation skill.
        """

        # Only sources with an explanation skill of their own can be explained ..
        skill = load_skill(source)

        if not skill:
            self.logger.info('No explanation skill exists for source `%s`, delivering `%s` unexplained', source, object_name)
            return Empty_Explanation

        # .. and one alert produces one explanation, not one per sweep - an error alert
        # dispatched again within its dedup window carries the explanation it already has.
        store = IncidentStore(self.odb.session, self.server.cluster_id)
        name = _explanation_name_prefix + str(payload['alert_id'])

        if stored := store.get(name):
            self.logger.info('An explanation already exists for `%s`, delivering `%s` with it', name, object_name)
            return stored

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

        # .. have the LLM explain it ..
        out = self._explain(skill.instructions, evidence)

        # .. store the explanation next to the alert ..
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
            'explanation': out['explanation'],
            'confidence': out['confidence'],
            'remediation': out['remediation'],
            'is_parsed': out['is_parsed'],
            'created_iso': now.isoformat(),
        }

        store.create(name, details)

        # .. and leave a trace in the audit log.
        audit_log = AuditLog(self.server.name)

        _ = audit_log.insert(source, AuditEvent.Alert_Explained, object_name,
            cid=self.cid, outcome=AuditOutcome.OK, data=payload['message'])

        self.logger.info('Alert `%s` explained for `%s` (%s)', name, object_name, payload['rule'])

        return out

# ################################################################################################################################

    def _get_connection_config(self, source:'str', object_name:'str') -> 'anydict':
        """ The connection's configuration for the evidence pack, looked up through
        the facade the alert's source names. Sources without an in-process config
        facade contribute the name alone - the audit trail carries the errors either
        way, which is what the explanation mostly reads.
        """
        if source == AuditSource.REST_Outgoing:
            out = self.out.rest[object_name].config

        elif source == AuditSource.LLM:
            out = self.llm.conn_dict[object_name]

        else:
            out = {'name': object_name}

        return out

# ################################################################################################################################

    def _get_llm_connection(self) -> 'str':
        """ The LLM connection the explanation goes through - the default connection,
        as long as it exists and is active. An empty name means no LLM is available
        and the alert goes out unexplained.
        """

        # The default connection ships inactive with placeholder credentials,
        # so it only answers once a person points it at a real model.
        name = get_llm_conn_name()

        if name not in self.llm.conn_dict:
            return ''

        item = self.llm.conn_dict[name]

        if not item['is_active']:
            return ''

        return name

# ################################################################################################################################

    def _explain(self, instructions:'str', evidence:'stranydict') -> 'stranydict':
        """ Runs the LLM explanation, or produces an empty one when no LLM connection
        is available - the alert still goes out so a person can look at the evidence.
        """
        llm_connection = self._get_llm_connection()

        if not llm_connection:

            self.logger.info('No LLM connection is available, storing the alert without an explanation')

            out:'stranydict' = {
                'explanation': '',
                'confidence': '',
                'remediation': None,
                'is_parsed': False,
            }

            return out

        prompt = build_prompt(instructions, evidence)
        response = self.llm[llm_connection].invoke(prompt)

        out = parse_explanation(response['text'])
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

    def _deliver(self, payload:'stranydict', explanation:'stranydict') -> 'None':
        """ Runs the rule's own action through the alerting engine, the way the sweep
        would have - the same transports, the same templates, the same deployment-level
        targets - with the explanation filled in. The explanation being present is what
        keeps the engine from handing the alert back here.
        """
        rule = new_rule(
            payload['rule'],
            payload['kind'],
            action=payload['action'],
            action_config=payload['action_config'],
            dedup_window_seconds=payload['dedup_window_seconds'],
            explain_with_llm=True,
        )

        finding = new_finding(payload['kind'], payload['source'], payload['object_name'], payload['message'],
            link=payload['link'], severity=payload['severity'])

        defaults = defaults_from_dict(payload['defaults'])
        transports = build_alert_transports(self, defaults.email_from)
        template_dir = self._get_template_dir()

        dispatch_action(rule, finding, payload['alert_id'], payload['count'], transports, defaults, template_dir,
            explanation)

# ################################################################################################################################
# ################################################################################################################################
