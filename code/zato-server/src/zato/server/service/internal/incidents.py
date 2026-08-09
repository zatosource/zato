# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc

# SQLAlchemy
from sqlalchemy import and_, select

# Zato
from zato.common.api import Incidents, SMTPMessage
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome
from zato.common.incidents.diagnosis import build_prompt, parse_diagnosis
from zato.common.incidents.evidence import build_evidence, collect_audit_trail
from zato.common.incidents.skill import load_skill
from zato.common.incidents.store import IncidentStore
from zato.common.json_internal import dumps
from zato.common.util.api import utcnow
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dictlist, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The actor recorded when the system itself acts, e.g. when an incident is raised.
_actor_system = 'zato'

# What each history entry calls its step.
_history_raised      = 'raised'
_history_approved    = 'approved'
_history_rejected    = 'rejected'
_history_resubmitted = 'resubmitted'

# The name incidents are stored under - the unique part is the cid of the diagnosis.
_incident_name_prefix = 'incident.'

# The statuses a resubmission may run from.
_resubmit_statuses = (Incidents.Status.Awaiting_Approval, Incidents.Status.Approved)

# ################################################################################################################################
# ################################################################################################################################

def _new_history_entry(action:'str', actor:'str', note:'str'='') -> 'stranydict':
    """ One step of an incident's history - who did what and when.
    """
    now = utcnow()

    out = {
        'action': action,
        'actor': actor,
        'time_iso': now.isoformat(),
        'note': note,
    }

    return out

# ################################################################################################################################

def _get_failed_cids(incident:'stranydict') -> 'dictlist':
    """ Returns the failed calls recorded in an incident's evidence - each one names
    the cid its request can be read back by.
    """

    # Our response to produce
    out:'dictlist' = []

    audit_trail = incident['evidence']['audit_trail']

    for event in audit_trail:

        if event['event_type'] != AuditEvent.Response_Received:
            continue

        if event['outcome'] != AuditOutcome.Error:
            continue

        out.append(event)

    return out

# ################################################################################################################################

def _load_request(engine:'any_', source:'str', object_name:'str', cid:'str') -> 'stranydict | None':
    """ Reads back the request that a failed call sent - the request-sent event sharing
    the failed response's cid, with the payload in its data and the method in its endpoint.
    """
    statement = select(
        event_table.c.endpoint,
        event_table.c.data,
    ).where(and_(
        event_table.c.source == source,
        event_table.c.object_name == object_name,
        event_table.c.cid == cid,
        event_table.c.event_type == AuditEvent.Request_Sent,
    )).order_by(event_table.c.id.desc())

    with engine.connect() as connection:
        row = connection.execute(statement).first()

    if row is None:
        return None

    endpoint, data = row

    # The endpoint is the method and the address separated by a space.
    method, _, _ = endpoint.partition(' ')

    out = {
        'method': method,
        'data': data,
    }

    return out

# ################################################################################################################################

def _run_resubmit(service:'AdminService', incident:'stranydict') -> 'stranydict':
    """ Re-sends the failed requests from an incident's evidence through the same connection.
    Each call is attempted on its own, so one failure never stops the others.
    """
    source = incident['source']
    object_name = incident['object_name']

    engine = get_audit_engine()
    conn = service.out.rest[object_name].conn

    failed = _get_failed_cids(incident)

    results:'dictlist' = []
    succeeded_count = 0

    for event in failed:

        cid = event['cid']
        result:'stranydict' = {'cid': cid, 'is_ok': False}

        # The original request may have aged out of the audit log by now ..
        request = _load_request(engine, source, object_name, cid)

        if request is None:
            result['note'] = 'Original request not found in the audit log'
            results.append(result)
            continue

        # .. otherwise, re-send it as a fresh call with its own audit trail.
        try:
            response = conn.http_request(request['method'], service.cid, request['data'])
        except Exception:
            result['note'] = format_exc()
        else:
            result['is_ok'] = response.ok
            result['status_code'] = response.status_code

            if response.ok:
                succeeded_count += 1
            else:
                result['note'] = response.text

        results.append(result)

    attempted_count = len(results)

    # Our response to produce
    out = {
        'is_ok': bool(attempted_count) and succeeded_count == attempted_count,
        'attempted': attempted_count,
        'succeeded': succeeded_count,
        'results': results,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class Diagnose(AdminService):
    """ Turns an alert about a failing connection into an incident - collects the evidence,
    has the LLM diagnose it against the connection's diagnostic skill, stores the incident
    as a generic object and notifies through the default notification connections.
    An alert rule's invoke-service action points here.
    """
    name = Incidents.Service_Diagnose

    def handle(self) -> 'None':

        # The payload arrives from the alerting engine - anything else means a manual
        # invocation with nothing to work from.
        payload = self.request.payload

        if not isinstance(payload, dict):
            self.logger.info('Incident diagnosis received no alert payload, nothing to do')
            return

        source = payload['source']
        object_name = payload['object_name']

        # Only sources with a diagnostic skill of their own can be diagnosed ..
        skill = load_skill(source)

        if not skill:
            self.logger.info('No diagnostic skill exists for source `%s`, skipping `%s`', source, object_name)
            return

        # .. and one failing connection produces one incident, not one per sweep.
        store = IncidentStore(self.odb.session, self.server.cluster_id)

        if store.has_open(object_name):
            self.logger.info('An open incident already exists for `%s`, skipping', object_name)
            return

        # The rule's own configuration - which LLM diagnoses and where notifications deliver.
        action_config = payload['action_config']

        # Collect the evidence pack ..
        conn_config = self.out.rest[object_name].config
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

        # .. store the incident ..
        now = utcnow()
        name = _incident_name_prefix + self.cid

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
            'history': [_new_history_entry(_history_raised, _actor_system)],
        }

        store.create(name, details, Incidents.Status.Awaiting_Approval)

        # .. leave a trace in the audit log ..
        audit_log = AuditLog(self.server.name)

        _ = audit_log.insert(source, AuditEvent.Incident_Raised, object_name,
            cid=self.cid, outcome=AuditOutcome.OK, data=payload['message'])

        self.logger.info('Incident `%s` raised for `%s` (%s)', name, object_name, payload['rule'])

        # .. and tell the people who decide.
        self._notify(name, details, action_config)

# ################################################################################################################################

    def _diagnose(self, instructions:'str', evidence:'stranydict', action_config:'anydict') -> 'stranydict':
        """ Runs the LLM diagnosis, or produces an empty one when no LLM connection
        is configured - the incident is still raised so a person can look at the evidence.
        """

        # The rule's action_config is user-editable - a missing key means no LLM is configured.
        llm_conn = action_config.get(Incidents.Config_LLM_Conn)

        if not llm_conn:

            self.logger.info('No `%s` key in the rule\'s action_config, storing the incident without a diagnosis',
                Incidents.Config_LLM_Conn)

            out:'stranydict' = {
                'diagnosis': '',
                'confidence': '',
                'remediation': None,
                'is_parsed': False,
            }

            return out

        prompt = build_prompt(instructions, evidence)
        response = self.llm[llm_conn].invoke(prompt)

        out = parse_diagnosis(response['text'])
        return out

# ################################################################################################################################

    def _build_notification_text(self, name:'str', details:'stranydict', action_config:'anydict') -> 'str':
        """ The message all the transports carry - what fired, what the diagnosis is
        and where in the Dashboard the decision is made.
        """
        lines = [
            f'Incident on `{details["object_name"]}` - {details["message"]}',
        ]

        if details['diagnosis']:
            lines.append('')
            lines.append(f'Diagnosis ({details["confidence"] or "no confidence given"}): {details["diagnosis"]}')

        # The links point at the incident's Dashboard detail screen - the resubmit one
        # additionally opens the confirmation popup on arrival.
        if dashboard_url := action_config.get(Incidents.Config_Dashboard_URL):

            detail_url = dashboard_url.rstrip('/') + Incidents.Dashboard_Path + name + '/'

            lines.append('')
            lines.append(f'Details: {detail_url}')

            if details['remediation']:
                lines.append(f'Resubmit: {detail_url}?action=resubmit')

        out = '\n'.join(lines)
        return out

# ################################################################################################################################

    def _notify(self, name:'str', details:'stranydict', action_config:'anydict') -> 'None':
        """ Sends the incident through every notification connection that is configured
        and active. A transport that is not set up is skipped with a log line -
        an unconfigured notification never breaks the diagnosis.
        """
        text = self._build_notification_text(name, details, action_config)
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
                transport(conn_name, text, action_config)
            except Exception:
                self.logger.warning('Could not send an incident notification through %s; e:`%s`', label, format_exc())

# ################################################################################################################################

    def _notify_slack(self, conn_name:'str', text:'str', action_config:'anydict') -> 'None':

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

        _ = self.slack.send(conn_name, channel, text)

# ################################################################################################################################

    def _notify_teams(self, conn_name:'str', text:'str', action_config:'anydict') -> 'None':

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
        html = text.replace('\n', '<br/>')
        _ = self.microsoft.teams.send(conn_name, to, html)

# ################################################################################################################################

    def _notify_email(self, conn_name:'str', text:'str', action_config:'anydict') -> 'None':

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
        message.subject = text.split('\n')[0]
        message.body = text

        smtp_item.conn.send(message)

# ################################################################################################################################
# ################################################################################################################################

class GetList(AdminService):
    """ Returns incident summaries, optionally only the ones in a given status, newest first.
    """
    name = 'zato.incidents.get-list'
    input = '-status'
    output = 'response_data'

    def handle(self) -> 'None':

        status = self.request.input.status or None

        store = IncidentStore(self.odb.session, self.server.cluster_id)
        incidents = store.get_list(status)

        items:'dictlist' = []

        for incident in incidents:
            items.append({
                'name': incident['name'],
                'status': incident['status'],
                'object_name': incident['object_name'],
                'source': incident['source'],
                'rule': incident['rule'],
                'severity': incident['severity'],
                'message': incident['message'],
                'confidence': incident['confidence'],
                'has_remediation': bool(incident['remediation']),
                'created_iso': incident['created_iso'],
            })

        self.response.payload.response_data = dumps({'items': items})

# ################################################################################################################################
# ################################################################################################################################

class Get(AdminService):
    """ Returns one incident in full, its evidence and history included.
    """
    name = 'zato.incidents.get'
    input = 'name'
    output = 'response_data'

    def handle(self) -> 'None':

        store = IncidentStore(self.odb.session, self.server.cluster_id)
        incident = store.get(self.request.input.name)

        self.response.payload.response_data = dumps({'incident': incident})

# ################################################################################################################################
# ################################################################################################################################

class _DecisionService(AdminService):
    """ What the approve, reject and resubmit services share - loading the incident,
    appending to its history and recording the decision in the audit log.
    """

    def _get_incident(self, store:'IncidentStore') -> 'stranydict | None':
        """ Returns the incident named on input, with an error response already set when there is none.
        """
        incident = store.get(self.request.input.name)

        if not incident:
            self.response.payload.response_data = dumps({'error': f'No such incident: `{self.request.input.name}`'})

        return incident

# ################################################################################################################################

    def _get_actor(self) -> 'str':
        """ Who is making the decision - the Dashboard sends the user's name.
        """
        out = self.request.input.actor or _actor_system
        return out

# ################################################################################################################################

    def _record_decision(
        self,
        store:'IncidentStore',
        incident:'stranydict',
        status:'str',
        event_type:'str',
        history_action:'str',
        actor:'str',
        note:'str'='',
        ) -> 'None':
        """ Moves the incident to its new status, extends its history and leaves an audit trace.
        """
        incident['history'].append(_new_history_entry(history_action, actor, note))

        # The id and status live outside the opaque document - everything else is the details.
        details:'stranydict' = {}

        for key, value in incident.items():
            if key not in ('id', 'name', 'status'):
                details[key] = value

        store.update(incident['name'], details, status)

        audit_log = AuditLog(self.server.name)

        _ = audit_log.insert(incident['source'], event_type, incident['object_name'],
            cid=self.cid, outcome=AuditOutcome.OK, endpoint=actor, data=note)

# ################################################################################################################################
# ################################################################################################################################

class Approve(_DecisionService):
    """ Approves an incident - when its diagnosis proposes a remediation, the remediation runs
    and a fully successful run resolves the incident. Without one, the incident is only
    marked approved and the follow-up stays with the person who approved it.
    """
    name = 'zato.incidents.approve'
    input = 'name', '-actor'
    output = 'response_data'

    def handle(self) -> 'None':

        store = IncidentStore(self.odb.session, self.server.cluster_id)
        incident = self._get_incident(store)

        if not incident:
            return

        if incident['status'] != Incidents.Status.Awaiting_Approval:
            self.response.payload.response_data = dumps({'error': f'Incident is not awaiting approval: `{incident["status"]}`'})
            return

        actor = self._get_actor()

        # An approved remediation runs at once ..
        if incident['remediation']:

            report = _run_resubmit(self, incident)
            note = f'Resubmitted {report["succeeded"]} of {report["attempted"]} request(s)'

            # .. and only a fully successful run closes the incident.
            if report['is_ok']:
                status = Incidents.Status.Resolved
                event_type = AuditEvent.Incident_Resolved
            else:
                status = Incidents.Status.Approved
                event_type = AuditEvent.Incident_Approved

        # .. with nothing to run, approval is a decision and nothing else.
        else:
            report = {'is_ok': True, 'attempted': 0, 'succeeded': 0, 'results': []}
            note = 'Approved with no remediation to run'
            status = Incidents.Status.Approved
            event_type = AuditEvent.Incident_Approved

        self._record_decision(store, incident, status, event_type, _history_approved, actor, note)

        self.response.payload.response_data = dumps({'status': status, 'report': report})

# ################################################################################################################################
# ################################################################################################################################

class Reject(_DecisionService):
    """ Rejects an incident - nothing runs and the incident is closed with the reason given.
    """
    name = 'zato.incidents.reject'
    input = 'name', '-actor', '-reason'
    output = 'response_data'

    def handle(self) -> 'None':

        store = IncidentStore(self.odb.session, self.server.cluster_id)
        incident = self._get_incident(store)

        if not incident:
            return

        if incident['status'] != Incidents.Status.Awaiting_Approval:
            self.response.payload.response_data = dumps({'error': f'Incident is not awaiting approval: `{incident["status"]}`'})
            return

        actor = self._get_actor()
        reason = self.request.input.reason or ''

        self._record_decision(
            store, incident, Incidents.Status.Rejected, AuditEvent.Incident_Rejected,
            _history_rejected, actor, reason)

        self.response.payload.response_data = dumps({'status': Incidents.Status.Rejected})

# ################################################################################################################################
# ################################################################################################################################

class Resubmit(_DecisionService):
    """ Re-sends the failed requests from an incident's evidence through the same connection,
    directly, without going through the approve step - the person clicking is the approval.
    """
    name = 'zato.incidents.resubmit'
    input = 'name', '-actor'
    output = 'response_data'

    def handle(self) -> 'None':

        store = IncidentStore(self.odb.session, self.server.cluster_id)
        incident = self._get_incident(store)

        if not incident:
            return

        if incident['status'] not in _resubmit_statuses:
            self.response.payload.response_data = dumps({'error': f'Incident cannot be resubmitted: `{incident["status"]}`'})
            return

        actor = self._get_actor()

        report = _run_resubmit(self, incident)
        note = f'Resubmitted {report["succeeded"]} of {report["attempted"]} request(s)'

        # Only a fully successful run closes the incident - anything else keeps it open
        # so it can be resubmitted again or rejected.
        if report['is_ok']:
            status = Incidents.Status.Resolved
            event_type = AuditEvent.Incident_Resolved
        else:
            status = incident['status']
            event_type = AuditEvent.Incident_Resubmitted

        self._record_decision(store, incident, status, event_type, _history_resubmitted, actor, note)

        self.response.payload.response_data = dumps({'status': status, 'report': report})

# ################################################################################################################################
# ################################################################################################################################
