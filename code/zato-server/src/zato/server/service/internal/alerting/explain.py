# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.alerting.collectors.evidence import collect_baseline, collect_measure_rows
from zato.common.alerting.engine import Empty_Explanation
from zato.common.alerting.explain.evidence import build_evidence_document, build_prompt, group_failures
from zato.common.alerting.explain.explanation import parse_explanation
from zato.common.alerting.explain.skill import get_skill_source, load_skill, Skills_Dir_Name
from zato.common.alerting.explain.store import ExplanationStore
from zato.common.alerting.object_config import LLM_Connection_Config_Key
from zato.common.audit_log.api import get_audit_engine, AuditEvent, AuditLog, AuditOutcome
from zato.common.util.api import utcnow
from zato.server.service.internal.alerting.object_info import get_object_info

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.alerting.explain.skill import Skill
    from zato.common.typing_ import stranydict
    from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

# The name explanations are stored under - the unique part is the id of the alert
# they explain, so one alert produces one explanation, not one per sweep.
_explanation_name_prefix = 'explanation.'

# ################################################################################################################################
# ################################################################################################################################

def get_explanation(service:'AdminService', payload:'stranydict') -> 'stranydict':
    """ The explanation of one alert - the stored one when the alert was explained
    before, a new one from the LLM otherwise, and the empty one for a source
    without an explanation skill.
    """
    source = payload['source']
    object_name = payload['object_name']

    # Only sources with an explanation skill of their own can be explained ..
    skill = _get_skill(service, source)

    if not skill:
        service.logger.info('No explanation skill exists for source `%s`, delivering `%s` unexplained', source, object_name)
        return Empty_Explanation

    # .. and one alert produces one explanation, not one per sweep - an error alert
    # dispatched again within its dedup window carries the explanation it already has.
    store = ExplanationStore(service.odb.session, service.server.cluster_id)
    name = _explanation_name_prefix + str(payload['alert_id'])

    if stored := store.get(name):
        service.logger.info('An explanation already exists for `%s`, delivering `%s` with it', name, object_name)
        return stored

    # Collect the evidence - the rows the measures were counted from, grouped and fitted
    # to the budget, the object's definition and the baseline around the failures ..
    now = utcnow()
    engine = get_audit_engine()
    fact = payload['fact']

    object_info, baseline_object_name, test_transfers_on = get_object_info(service, source, object_name)

    rows = collect_measure_rows(engine, fact, payload['measures'], now)
    groups = group_failures(rows, source)

    baseline = collect_baseline(engine, fact, now, baseline_object_name=baseline_object_name,
        test_transfers_on=test_transfers_on)

    alert = {
        'rule': payload['rule'],
        'severity': payload['severity'],
        'source': source,
        'object_name': object_name,
        'message': payload['message'],
        'fact': fact,
        'thresholds': payload['thresholds'],
        'measures': payload['measures'],
    }

    document = build_evidence_document(alert, object_info, groups, baseline, now)

    # .. have the LLM explain it ..
    out = _explain(service, payload, skill, document)

    # .. store the explanation next to the alert, the document with it so a person can read what the LLM read ..
    details = {
        'object_name': object_name,
        'source': source,
        'rule': payload['rule'],
        'alert_id': payload['alert_id'],
        'count': payload['count'],
        'severity': payload['severity'],
        'message': payload['message'],
        'link': payload['link'],
        'evidence': document,
        'explanation': out['explanation'],
        'confidence': out['confidence'],
        'remediation': out['remediation'],
        'is_parsed': out['is_parsed'],
        'created_iso': now.isoformat(),
    }

    store.create(name, details)

    # .. and leave a trace in the audit log.
    audit_log = AuditLog(service.server.name)

    _ = audit_log.insert(source, AuditEvent.Alert_Explained, object_name,
        cid=service.cid, outcome=AuditOutcome.OK, data=payload['message'])

    service.logger.info('Alert `%s` explained for `%s` (%s)', name, object_name, payload['rule'])

    return out

# ################################################################################################################################

def _get_skills_dir(service:'AdminService') -> 'str':
    """ The server's own skills directory - the shipped skills answer
    until an environment created before the directory existed is recreated.
    """
    out = os.path.join(service.server.repo_location, Skills_Dir_Name)

    if not os.path.isdir(out):
        out = ''

    return out

# ################################################################################################################################

def _get_skill(service:'AdminService', source:'str') -> 'Skill | None':
    """ The skill explaining the alerts of a source - a probe's or a health check's alerts
    are explained with the skill of the connection they check.
    """
    out = load_skill(get_skill_source(source), _get_skills_dir(service))
    return out

# ################################################################################################################################

def _get_llm_connection(service:'AdminService', payload:'stranydict') -> 'str':
    """ The LLM connection the explanation goes through - the object's own when its Alerts tab
    names one, the deployment's default otherwise, as long as it exists and is active.
    An empty name means no LLM is available and the alert goes out unexplained.
    """
    action_config = payload['action_config']

    if LLM_Connection_Config_Key in action_config:
        name = action_config[LLM_Connection_Config_Key]
    else:
        name = payload['defaults']['llm_connection']

    if not name:
        return ''

    if name not in service.llm.conn_dict:
        service.logger.info('LLM connection `%s` does not exist, storing the alert without an explanation', name)
        return ''

    item = service.llm.conn_dict[name]

    if not item['is_active']:
        service.logger.info('LLM connection `%s` is inactive, storing the alert without an explanation', name)
        return ''

    return name

# ################################################################################################################################

def _explain(service:'AdminService', payload:'stranydict', skill:'Skill', document:'str') -> 'stranydict':
    """ Runs the LLM explanation, or produces an empty one when no LLM connection
    is available - the alert still goes out so a person can look at the evidence.
    """
    llm_connection = _get_llm_connection(service, payload)

    if not llm_connection:

        service.logger.info('No LLM connection is available, storing the alert without an explanation')

        out:'stranydict' = {
            'explanation': '',
            'confidence': '',
            'remediation': None,
            'is_parsed': False,
        }

        return out

    prompt = build_prompt(skill.instructions, document)
    response = service.llm[llm_connection].invoke(prompt)

    out = parse_explanation(response['text'], skill.remediations)
    return out

# ################################################################################################################################
# ################################################################################################################################
