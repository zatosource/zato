# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The default alerting definitions a new environment starts with - the `alerting`
# vocabulary the builder's completion menus speak and one ruleset per connection
# family the sweep matches facts through. Everything is seeded idempotently, each
# definition by its own name: a store that already holds one of them, published
# or not, keeps what it has, so nothing a person edited or archived ever comes
# back on its own, and an environment created before a family existed gains
# only the missing rulesets.

from __future__ import annotations

# stdlib
from logging import getLogger

# Zato
from zato.common.api import Alerting
from zato.common.audit_log.api import AuditSource
from zato.common.rule_engine.document_checks import validate_definition_document
from zato.common.rule_engine.parser import parse_data_details
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset, Definition_Type_Vocabulary, Documents_Key, \
    System_Actor
from zato.common.rule_engine.vocabulary import TermType

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import RuleDefinitionRecord, RuleSQLBackend
    from zato.common.typing_ import anydict
    anydict = anydict
    RuleDefinitionRecord = RuleDefinitionRecord
    RuleSQLBackend = RuleSQLBackend

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The comment the first version of each seeded definition carries.
_seed_comment = 'The alerting definitions a new environment starts with'

# A term that is neither deprecated nor otherwise marked carries no status.
_no_status = ''

# The audit sources a rule may narrow itself to - the value list behind `alert.source`.
_alert_sources = [
    AuditSource.PubSub,
    AuditSource.REST_Channel,
    AuditSource.SOAP_Channel,
    AuditSource.REST_Outgoing,
    AuditSource.SOAP_Outgoing,
    AuditSource.Email_IMAP,
    AuditSource.Email_SMTP,
    AuditSource.File_Outgoing,
    AuditSource.SQL_Outgoing,
    AuditSource.AS2,
    AuditSource.AS4,
    AuditSource.X12,
    AuditSource.MCP,
    AuditSource.MLLP_Channel,
    AuditSource.MLLP_Outgoing,
    AuditSource.FHIR,
    AuditSource.Config,
    AuditSource.Scheduler,
    AuditSource.LLM,
    AuditSource.Odoo,
    AuditSource.Microsoft_Cloud,
    AuditSource.Certificate,
    AuditSource.Microsoft_Health,
    AuditSource.Canary,
]

# The actions an outcome may name - the value list behind `outcome.action`.
_outcome_actions = [
    'incident',
    'email',
    'slack',
    'teams',
    'invoke-service',
    'publish-to-topic',
]

# The severities an outcome may carry - the value list behind `outcome.severity`.
_outcome_severities = [
    'info',
    'warning',
    'critical',
]

# The health states a remote service may report about itself - the value list
# behind `alert.health_state`. The probe normalizes whatever the provider says
# into these two, so the rules never chase provider-specific spellings.
_health_states = [
    'degraded',
    'interruption',
]

# The canary rule ships inactive because the canary writes to remote systems -
# activating the rule together with the canary job is the documented opt-in.
_inactive_rule_full_names = [
    'alerts_file_transfer_Canary_Failing',
]

# ################################################################################################################################
# ################################################################################################################################

# The default alert rules, one ruleset per connection family. Every threshold is
# a named default the user tunes in place, no error-rate rule fires on thin traffic,
# and the numbers follow the cross-platform survey - three consecutive failures
# for down, 10 percent errors over five minutes, 5 seconds for HTTP latency,
# 7 days for certificates, twice the interval for missed scheduled work.

_common_rules = """
rule
    Outstanding_Backlog
docs
    An object with messages still waiting for their follow-up raises an email alert when the count reaches the threshold.
defaults
    outstanding_threshold = 100
when
    alert.outstanding is at least default.outstanding_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Feed_Silent
docs
    A feed that has been silent for two hours or more raises an email alert.
defaults
    silent_threshold_seconds = 7200
when
    alert.silent_seconds is at least default.silent_threshold_seconds
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Certificate_Expiring
docs
    A connection whose TLS certificate expires within a week raises an email alert.
    A days-left value of zero means the certificate was not measured at all, which is why the rule also requires at least one day.
defaults
    cert_warning_days = 7
    min_days_measured = 1
when
    alert.source is 'certificate' and
    alert.cert_days_left is at least default.min_days_measured and
    alert.cert_days_left is less than default.cert_warning_days
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

# ################################################################################################################################

_channels_rules = """
rule
    Channel_Error_Rate
docs
    An inbound channel whose error share reaches a tenth of its recent traffic raises an email alert.
    The rule waits for at least ten events in the window, so one failure out of two calls never wakes anyone up.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source in ['rest-channel', 'soap-channel', 'mllp-channel'] and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

# ################################################################################################################################

_rest_rules = """
rule
    Connection_Down
docs
    A REST or SOAP outgoing connection that failed three consecutive times is considered down and raises a critical email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source in ['rest-outgoing', 'soap-outgoing'] and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Slow_Responses
docs
    A REST or SOAP outgoing connection whose average response time within the window exceeds five seconds raises an email alert.
defaults
    max_avg_duration_ms = 5000
when
    alert.source in ['rest-outgoing', 'soap-outgoing'] and
    alert.avg_duration_ms is at least default.max_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate
docs
    A REST or SOAP outgoing connection whose error share reaches a tenth of its recent traffic raises an email alert.
    This is the early warning below the incident rule's quarter threshold.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source in ['rest-outgoing', 'soap-outgoing'] and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate_Incident
docs
    A REST outgoing connection whose error share reached a quarter of its recent traffic is diagnosed as an incident.
defaults
    error_rate_threshold = 0.25
    min_events = 10
when
    alert.source is 'rest-outgoing' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'incident'
    outcome.severity = 'critical'
""".strip()

# ################################################################################################################################

_sql_rules = """
rule
    Connection_Down
docs
    A database connection that failed three consecutive times is down - the top of the severity ladder,
    because everything else rests on the database being there.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'sql-outgoing' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Slow_Queries
docs
    A database connection whose average query round-trip within the window exceeds five seconds raises an email alert.
defaults
    max_avg_duration_ms = 5000
when
    alert.source is 'sql-outgoing' and
    alert.avg_duration_ms is at least default.max_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate
docs
    A database connection whose failed-query share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source is 'sql-outgoing' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

# ################################################################################################################################

_llm_rules = """
rule
    Connection_Down
docs
    An LLM connection that failed three consecutive times is considered down and raises a critical email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'llm' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Slow_Completions
docs
    An LLM connection whose average completion time within the window exceeds ten seconds raises a warning email alert.
    Above fifteen seconds the critical rule takes over, which is why this one is bounded from above.
defaults
    warning_avg_duration_ms = 10000
    critical_avg_duration_ms = 15000
when
    alert.source is 'llm' and
    alert.avg_duration_ms is at least default.warning_avg_duration_ms and
    alert.avg_duration_ms is less than default.critical_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Slow_Completions_Critical
docs
    An LLM connection whose average completion time within the window exceeds fifteen seconds raises a critical email alert.
defaults
    critical_avg_duration_ms = 15000
when
    alert.source is 'llm' and
    alert.avg_duration_ms is at least default.critical_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Error_Rate
docs
    An LLM connection whose failed-completion share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source is 'llm' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

# ################################################################################################################################

_mcp_rules = """
rule
    Server_Down
docs
    An MCP connection that failed three consecutive times is considered down and raises a critical email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'mcp' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Slow_Tool_Calls
docs
    An MCP connection whose average tool-call time within the window exceeds five seconds raises an email alert.
defaults
    max_avg_duration_ms = 5000
when
    alert.source is 'mcp' and
    alert.avg_duration_ms is at least default.max_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate
docs
    An MCP connection whose failed-call share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source is 'mcp' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

# ################################################################################################################################

_microsoft_rules = """
rule
    Connection_Down
docs
    A Microsoft cloud connection that failed three consecutive times is considered down and raises a critical email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'microsoft-cloud' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Slow_API_Calls
docs
    A Microsoft cloud connection whose average call time within the window exceeds two seconds raises an email alert.
defaults
    max_avg_duration_ms = 2000
when
    alert.source is 'microsoft-cloud' and
    alert.avg_duration_ms is at least default.max_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate
docs
    A Microsoft cloud connection whose failed-call share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source is 'microsoft-cloud' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Service_Degraded
docs
    A Microsoft service reporting a degraded health state about itself raises an email alert at once, no window.
when
    alert.source is 'microsoft-health' and
    alert.health_state is 'degraded'
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Service_Interrupted
docs
    A Microsoft service reporting a service interruption about itself raises a critical email alert at once, no window.
when
    alert.source is 'microsoft-health' and
    alert.health_state is 'interruption'
then
    outcome.action = 'email'
    outcome.severity = 'critical'
""".strip()

# ################################################################################################################################

_email_rules = """
rule
    Connection_Down
docs
    An email connection that failed three consecutive times is considered down and raises a critical email alert,
    dispatched through the remaining notification connections when the failing one is itself the email connection.
defaults
    max_consecutive_failures = 3
when
    alert.source in ['email-smtp', 'email-imap'] and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Auth_Failures
docs
    An email connection with three or more authentication failures within the window raises an email alert.
    Authentication failing is its own signal, distinct from unreachable, because the remedy is credentials, not networking.
defaults
    auth_failure_threshold = 3
when
    alert.source in ['email-smtp', 'email-imap'] and
    alert.auth_failure_count is at least default.auth_failure_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate
docs
    An email connection whose failed-send or failed-fetch share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source in ['email-smtp', 'email-imap'] and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

# ################################################################################################################################

_odoo_rules = """
rule
    Connection_Down
docs
    An Odoo connection that failed three consecutive times is considered down and raises a critical email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'odoo' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Auth_Failures
docs
    An Odoo connection with three or more failed logins within the window raises an email alert.
defaults
    auth_failure_threshold = 3
when
    alert.source is 'odoo' and
    alert.auth_failure_count is at least default.auth_failure_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Slow_Calls
docs
    An Odoo connection whose average call time within the window exceeds two seconds raises an email alert.
defaults
    max_avg_duration_ms = 2000
when
    alert.source is 'odoo' and
    alert.avg_duration_ms is at least default.max_avg_duration_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Error_Rate
docs
    An Odoo connection whose failed-call share reaches a tenth of its recent traffic raises an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source is 'odoo' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

# ################################################################################################################################

_file_transfer_rules = """
rule
    Connection_Down
docs
    A file transfer connection that failed three consecutive times is considered down and raises a critical email alert.
defaults
    max_consecutive_failures = 3
when
    alert.source is 'file-outgoing' and
    alert.consecutive_failures is at least default.max_consecutive_failures
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Transfer_Failures
docs
    A file transfer connection with ten or more failed transfers within its window raises a warning email alert.
    This family measures over ten minutes because transfers are burstier than API calls.
    At twenty failures the critical rule takes over, which is why this one is bounded from above.
defaults
    warning_failure_count = 10
    critical_failure_count = 20
when
    alert.source is 'file-outgoing' and
    alert.error_count is at least default.warning_failure_count and
    alert.error_count is less than default.critical_failure_count
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Transfer_Failures_Critical
docs
    A file transfer connection with twenty or more failed transfers within its window raises a critical email alert.
defaults
    critical_failure_count = 20
when
    alert.source is 'file-outgoing' and
    alert.error_count is at least default.critical_failure_count
then
    outcome.action = 'email'
    outcome.severity = 'critical'

rule
    Canary_Failing
docs
    A failing canary check raises a critical email alert at once - the canary uploads, downloads and removes
    a small test file, so its newest outcome speaks for the whole transfer path.
    Ships inactive, like the canary job itself, because the canary writes to the remote system - activating both is the opt-in.
when
    alert.source is 'canary' and
    alert.canary_failed is 1
then
    outcome.action = 'email'
    outcome.severity = 'critical'
""".strip()

# ################################################################################################################################

_scheduler_rules = """
rule
    Job_Error_Rate
docs
    Scheduled jobs whose error share reaches a tenth of their recent runs raise an email alert.
defaults
    error_rate_threshold = 0.1
    min_events = 10
when
    alert.source is 'scheduler' and
    alert.total_count is at least default.min_events and
    alert.error_rate is at least default.error_rate_threshold
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Missed_Run
docs
    A job that has not run for longer than twice its own interval raises an email alert.
    The measure is a ratio of time since the newest run to the job's interval, so it sizes itself to each job.
defaults
    overdue_multiplier = 2
when
    alert.source is 'scheduler' and
    alert.overdue_ratio is at least default.overdue_multiplier
then
    outcome.action = 'email'
    outcome.severity = 'warning'

rule
    Start_Delay
docs
    A job whose delay between planned and actual fire time exceeds five seconds raises an email alert.
defaults
    max_start_delay_ms = 5000
when
    alert.source is 'scheduler' and
    alert.start_delay_ms is at least default.max_start_delay_ms
then
    outcome.action = 'email'
    outcome.severity = 'warning'
""".strip()

# ################################################################################################################################
# ################################################################################################################################

# The seed table - every default ruleset by name, seeded in one loop with the same
# idempotent per-name existence check. An environment that already customized one
# of them gains only the missing ones. The legacy single `alerts` ruleset is not
# here on purpose - environments that hold it keep it, and the sweep's prefix
# matching runs it alongside these.
default_rulesets = [
    ('alerts_common',        _common_rules),
    ('alerts_channels',      _channels_rules),
    ('alerts_rest',          _rest_rules),
    ('alerts_sql',           _sql_rules),
    ('alerts_llm',           _llm_rules),
    ('alerts_mcp',           _mcp_rules),
    ('alerts_microsoft',     _microsoft_rules),
    ('alerts_email',         _email_rules),
    ('alerts_odoo',          _odoo_rules),
    ('alerts_file_transfer', _file_transfer_rules),
    ('alerts_scheduler',     _scheduler_rules),
]

# ################################################################################################################################
# ################################################################################################################################

def _term(name:'str', type_:'str', phrase:'str', *, values:'list[str] | None'=None) -> 'anydict':
    """ One vocabulary attribute - the name rules use, the type that decides which comparators fit
    and the phrase every screen speaks it with. A choice term also carries its legal values.
    """
    out = {'name': name, 'type': type_, 'phrase': phrase, 'status': _no_status}

    if values is not None:
        out['values'] = values

    return out

# ################################################################################################################################

def alerting_vocabulary() -> 'anydict':
    """ The terms the alert rules are written in - what the collectors measure about an object
    and what a matching rule decides about it.
    """
    alert_terms = [
        _term('source',                 TermType.Choice, 'the kind of object the measures are about', values=_alert_sources),
        _term('object_name',            TermType.Text,   'the name of the object the measures are about'),
        _term('error_rate',             TermType.Number, 'the share of error outcomes within the window'),
        _term('error_count',            TermType.Number, 'how many error outcomes the window holds'),
        _term('total_count',            TermType.Number, 'how many events the window holds in total'),
        _term('window_seconds',         TermType.Number, 'how many seconds the error measures cover'),
        _term('outstanding',            TermType.Number, 'how many messages still wait for their follow-up'),
        _term('oldest_waiting_seconds', TermType.Number, 'how long the oldest waiting message has been waiting'),
        _term('silent_seconds',         TermType.Number, 'how long the feed has been silent'),
        _term('consecutive_failures',   TermType.Number, 'how many of the newest outcomes are errors, without a break'),
        _term('avg_duration_ms',        TermType.Number, 'the average duration of completed calls within the window'),
        _term('auth_failure_count',     TermType.Number, 'how many authentication failures the window holds'),
        _term('cert_days_left',         TermType.Number, 'how many days the TLS certificate has left, zero when unmeasured'),
        _term('health_state',           TermType.Choice, 'the health state the remote service reports about itself',
            values=_health_states),
        _term('canary_failed',          TermType.Number, 'whether the newest canary check failed'),
        _term('overdue_ratio',          TermType.Number, 'time since the newest run as a multiple of the job interval'),
        _term('start_delay_ms',         TermType.Number, 'the worst delay between planned and actual fire time in the window'),
    ]

    outcome_terms = [
        _term('action',               TermType.Choice, 'what happens when the rule fires', values=_outcome_actions),
        _term('severity',             TermType.Choice, 'how severe the alert is', values=_outcome_severities),
        _term('llm_conn',             TermType.Text,   'the LLM connection an incident diagnosis goes through'),
        _term('dashboard_url',        TermType.Text,   'the dashboard address notification links point to'),
        _term('addresses',            TermType.Text,   'the comma-separated addresses an email alert goes to'),
        _term('service',              TermType.Text,   'the service an invoke-service action calls'),
        _term('topic',                TermType.Text,   'the topic a publish-to-topic action publishes to'),
        _term('webhook_url',          TermType.Text,   'the webhook a Slack or Teams alert posts to'),
        _term('link',                 TermType.Text,   'the dashboard path the alert message links to'),
        _term('dedup_window_seconds', TermType.Number, 'how long repeated matches increment the alert instead of raising anew'),
    ]

    entities = [
        {'name': 'alert', 'attributes': alert_terms},
        {'name': 'outcome', 'attributes': outcome_terms},
    ]

    out = {'name': Alerting.Vocabulary_Name, 'entities': entities}
    return out

# ################################################################################################################################

def build_ruleset_document(ruleset_name:'str', zrules_contents:'str') -> 'anydict':
    """ One default ruleset as the canonical documents the store keeps,
    parsed from the same text form the builder produces.
    """
    documents, errors = parse_data_details(zrules_contents, ruleset_name)

    if errors:
        raise Exception(f'The default alert rules of `{ruleset_name}` do not parse -> {errors}')

    # The rules that ship turned off are marked so before they ever reach the store
    for full_name in _inactive_rule_full_names:
        if full_name in documents:
            documents[full_name]['is_active'] = False

    out = {Documents_Key: documents}
    return out

# ################################################################################################################################
# ################################################################################################################################

def _exists(backend:'RuleSQLBackend', name:'str', object_type:'str') -> 'bool':
    """ Whether the store already holds one seeded definition, under the name and the kind
    it is created with. Archived ones count too - what was put aside on purpose stays that way.
    """
    candidates = backend.definitions.list(object_type=object_type, include_inactive=True, search_text=name)

    for candidate in candidates:
        if candidate.name == name:
            out = True
            break
    else:
        out = False

    return out

# ################################################################################################################################

def _create_definition(
    backend:'RuleSQLBackend',
    *,
    name:'str',
    object_type:'str',
    document:'anydict',
    ) -> 'RuleDefinitionRecord':
    """ Stores one seeded definition together with its first version, after the same validation the screens run.
    """
    errors = validate_definition_document(object_type, document)

    if errors:
        raise Exception(f'The default alerting {object_type} does not validate -> {errors}')

    out = backend.definitions.create(
        name=name,
        object_type=object_type,
        document=document,
        author=System_Actor,
        comment=_seed_comment,
    )

    logger.info('Created the default alerting %s `%s` (id=%s)', object_type, name, out.id)
    return out

# ################################################################################################################################

def _seed_vocabulary(backend:'RuleSQLBackend') -> 'bool':
    """ The vocabulary comes first, because the rulesets speak its terms.
    """
    if _exists(backend, Alerting.Vocabulary_Name, Definition_Type_Vocabulary):
        return False

    vocabulary = _create_definition(
        backend,
        name=Alerting.Vocabulary_Name,
        object_type=Definition_Type_Vocabulary,
        document=alerting_vocabulary(),
    )
    _ = backend.versions.publish(definition_id=vocabulary.id, version=vocabulary.current_version, actor=System_Actor)

    return True

# ################################################################################################################################

def _seed_ruleset(backend:'RuleSQLBackend', ruleset_name:'str', zrules_contents:'str') -> 'bool':
    """ One default ruleset goes live in the same call, so the very first sweep already has it.
    """
    if _exists(backend, ruleset_name, Definition_Type_Ruleset):
        return False

    document = build_ruleset_document(ruleset_name, zrules_contents)
    ruleset = _create_definition(
        backend,
        name=ruleset_name,
        object_type=Definition_Type_Ruleset,
        document=document,
    )

    documents = document[Documents_Key]
    _ = backend.references.rebuild(definition_id=ruleset.id, documents=documents)
    _ = backend.versions.publish(definition_id=ruleset.id, version=ruleset.current_version, actor=System_Actor)

    return True

# ################################################################################################################################
# ################################################################################################################################

def ensure_alerting_definitions(backend:'RuleSQLBackend') -> 'None':
    """ Gives an environment the alerting vocabulary and the default alert rulesets.

    Each one is looked up by its own name and kind, so a store that already holds
    some of them gains only what is missing, and anything a person edited themselves
    is never touched.
    """
    created_any = _seed_vocabulary(backend)

    for ruleset_name, zrules_contents in default_rulesets:
        created_ruleset = _seed_ruleset(backend, ruleset_name, zrules_contents)
        created_any = created_any or created_ruleset

    if created_any:
        logger.info('Default alerting definitions seeded')

# ################################################################################################################################
# ################################################################################################################################
