// Alert rules - the rows screen.
//
// One slim full-width row per rule type. Every row says whether its
// type is active and shows the values its rules are driven by, in
// columns aligned across all the rows. Clicking a value opens the row's
// popover editor - the wizard kit's own micro-form - on that very field.
// The values come from the live rule documents through the Django view
// and every change goes back the same way - the popover's OK posts the
// row's values, the badge posts the type's active state, and the row
// answers with its Running badge while the request is on its way.
//
// This file holds what the screen is configured with and the lookups every
// other file of the screen shares - units.js the durations, amounts and sizes,
// save.js the requests, editor.js the popover, cards.js the rows and
// init.js the wiring once the page is there.

$.fn.zato.alerting_config = {};

// ////////////////////////////////////////////////////////////////////////

(function($) {

var screen = $.fn.zato.alerting_config;

var config = {};
screen.config = config;

// ////////////////////////////////////////////////////////////////////////

// Where a change is posted - the endpoints the template names, one for
// the type rows and one for the notifications row below them, read off
// the page by init.js once it is there
config.saveUrl = '';
config.notificationsSaveUrl = '';

// The one fixed row that is not a rule type - the notification targets
config.notificationsName = 'notifications';

// What a request that never reached its endpoint reports
config.applyErrorText = 'The change could not be applied';

// How long a finished change's confirmation stays on screen
config.okVisibleMs = 1500;

// What a finished change confirms itself with
config.okLabel = 'OK';

// What a row's badge says about its type
config.statusOnLabel = 'Active';
config.statusOffLabel = 'Inactive';

// What the badge offers on a hover - clicking it flips the type
config.toggleHintLabel = 'Click to toggle';

// What a checkbox value reads as in its cell
config.checkboxOnLabel = 'On';
config.checkboxOffLabel = 'Off';

// What a notification cell without a value reads as
config.notSetLabel = 'Not set';

// Every element the popover makes is named after this
config.idPrefix = 'alert-rules-row';

// How wide a row's popover editor stands, and how wide one with chips does - room for a handful
// of codes on one line and for the chips to wrap
config.popupWidth = '290px';
config.chipsPopupWidth = '420px';

// The class the popover editors wear, under which index.css sizes their switches
config.popupClass = 'alert-rules-micro-form';

// Where the hand-picked row order is kept between visits
config.orderStorageKey = 'zato.alert-rules.order';

// What a row's element ids open with - the card, its status badge and its confirmation
config.cardIdPrefix = 'alert-rules-card-';
config.statusIdPrefix = 'alert-rules-status-';
config.okIdPrefix = 'alert-rules-ok-';

// What the hidden state field of a type is named after, and what its row header help is keyed by
config.fieldIdPrefix = 'id_alert_rules_';

// ////////////////////////////////////////////////////////////////////////

// Every value the rows carry, each named once - the label is what the
// popover calls the field, with the unit the cell says through its suffix
config.fields = {
    consecutive_failures: {label: 'Consecutive failures', kind: 'number'},
    error_rate: {label: 'Error rate (%)', kind: 'number'},
    max_latency: {label: 'Max latency (ms)', kind: 'number'},
    max_query_time: {label: 'Max query time (ms)', kind: 'number'},
    warning_latency: {label: 'Warning latency (s)', kind: 'seconds'},
    error_latency: {label: 'Error latency (s)', kind: 'seconds'},
    truncations: {label: 'Truncated completions', kind: 'number'},
    refusals: {label: 'Refusals', kind: 'number'},
    token_budget: {label: 'Token budget', kind: 'amount'},
    invalid_calls: {label: 'Invalid tool calls', kind: 'number'},
    rejections: {label: 'Rejected responses', kind: 'number'},
    throttled_calls: {label: 'Throttled calls', kind: 'number'},
    repeat_calls: {label: 'Repeated calls', kind: 'number'},
    volume_budget: {label: 'Response volume', kind: 'size'},
    max_tools: {label: 'Max tools', kind: 'number'},
    health_alerts: {label: 'Health alerts', kind: 'checkbox'},
    max_call_time: {label: 'Max call time (ms)', kind: 'number'},
    auth_failures: {label: 'Auth failures', kind: 'number'},
    warning_failures: {label: 'Warning failures', kind: 'number'},
    error_failures: {label: 'Error failures', kind: 'number'},
    window: {label: 'Window', kind: 'duration'},
    status_codes: {label: 'Status codes', kind: $.fn.zato.micro_forms.chipsKind},
    fault_codes: {label: 'Fault codes', kind: $.fn.zato.micro_forms.chipsKind},
    arrival_overdue: {label: 'Arrival overdue', kind: 'number'},
    test_transfers: {label: 'Test transfers', kind: 'checkbox'},
    overdue_multiplier: {label: 'Overdue multiplier', kind: 'number'},
    start_delay: {label: 'Start delay (ms)', kind: 'number'},
    certificate_warning: {label: 'Certificate warning (days)', kind: 'number'},
    outstanding_backlog: {label: 'Outstanding backlog', kind: 'number'},
    feed_silence: {label: 'Feed silence (s)', kind: 'number'},
    use_llm: {label: 'Use LLM', kind: 'checkbox'},
    slack_webhook: {label: 'Slack webhook', kind: 'text'},
    teams_webhook: {label: 'Teams webhook', kind: 'text'},
    webhook_url: {label: 'Webhook URL', kind: 'text'},
    email_connection: {label: 'Email connection', kind: 'text'},
    default_to: {label: 'Email to', kind: 'text'},
    from: {label: 'Email from', kind: 'text'},
    dashboard_url: {label: 'Dashboard URL', kind: 'text'},
    llm_connection: {label: 'LLM connection', kind: 'text'}
};

// The units a duration is edited and shown in, smallest first - a cell picks the
// largest one dividing its seconds evenly, so 86400 seconds read as 1 day
config.durationUnits = [
    {value: 'minute', singular: 'minute', plural: 'minutes', seconds: 60},
    {value: 'hour', singular: 'hour', plural: 'hours', seconds: 3600},
    {value: 'day', singular: 'day', plural: 'days', seconds: 86400}
];

// The units an amount is edited and shown in, smallest first - a cell picks the
// largest one the amount reaches, so 10000000 tokens read as 10 millions and 1500000 as 1.5 millions
config.amountUnits = [
    {value: 'thousand', singular: 'thousand', plural: 'thousands', size: 1000},
    {value: 'million', singular: 'million', plural: 'millions', size: 1000000},
    {value: 'billion', singular: 'billion', plural: 'billions', size: 1000000000}
];

// The units a size is edited and shown in, smallest first - a cell picks the largest one
// the size reaches, so 100000000 bytes read as 100 megabytes and 1500000000 as 1.5 gigabytes
config.sizeUnits = [
    {value: 'kilobyte', singular: 'kilobyte', plural: 'kilobytes', size: 1000},
    {value: 'megabyte', singular: 'megabyte', plural: 'megabytes', size: 1000000},
    {value: 'gigabyte', singular: 'gigabyte', plural: 'gigabytes', size: 1000000000}
];

// The hidden select a duration's, an amount's or a size's unit is edited through sits next to its number under this suffix
config.unitFieldSuffix = '_unit';

// The step a fractional number - seconds, an amount, a size - goes by, so the browser takes 7.5 and 2.5
config.fractionalStep = 'any';

// What a field means, said once and shown wherever the field is edited
config.fieldHelp = {
    consecutive_failures: 'How many failures in a row raise an alert.',
    error_rate: 'The share of failed calls, in percent, that raises an alert.',
    max_latency: 'Calls slower than this many milliseconds count as slow.',
    max_query_time: 'Queries slower than this many milliseconds count as slow.',
    warning_latency: 'Completions slower than this many seconds raise a warning - a fraction such as 7.5 is fine.',
    error_latency: 'Completions slower than this many seconds are errors - a fraction such as 12.5 is fine.',
    truncations: 'How many completions cut short by the token limit in the window raise an alert - the provider stopped generating because max tokens was reached, so the reply arrived with a 200 but is incomplete.',
    refusals: 'How many refused completions in the window raise an alert - the provider declined to answer or a content filter blocked the prompt or the reply, most of them arriving with a 200.',
    token_budget: 'How many tokens, input and output added up across every call, raise an alert - a count in thousands, millions or billions, a fraction such as 2.5 is fine.',
    invalid_calls: 'How many invalid tool calls in the window raise an alert - the agent named a tool the gateway does not expose or passed arguments its schema refused.',
    rejections: 'How many rejected responses in the window raise an alert - a safeguard in reject mode or the size cap in block mode refused what a tool returned.',
    throttled_calls: 'How many throttled calls in the window raise an alert - requests a security definition\'s rate limit answered with a 429.',
    repeat_calls: 'How many times one session may call one tool in the window before an alert - an agent stuck in a loop.',
    volume_budget: 'How many bytes of tool responses added up across every call raise an alert - a size in kilobytes, megabytes or gigabytes, a fraction such as 1.5 is fine.',
    max_tools: 'How many tools a gateway may expose before an alert - the most capable models degrade past 20 to 25.',
    health_alerts: 'Whether the Microsoft service health feed raises alerts of its own.',
    max_call_time: 'Calls slower than this many milliseconds count as slow.',
    auth_failures: 'How many authentication failures in a row raise an alert.',
    warning_failures: 'How many failures in the window raise a warning.',
    error_failures: 'How many failures in the window count as errors.',
    window: 'How long the window is, in minutes, hours or days.',
    status_codes: 'The status codes an outgoing connection alerts on - three-digit codes such as 401 or 403 and whole classes such as 4xx or 5xx, each one a chip, typed and added with Enter, removed with its cross.',
    fault_codes: 'The SOAP fault codes an outgoing SOAP connection alerts on - Receiver and Server are the endpoint\'s own faults, Sender and Client the caller\'s, and a code of the endpoint\'s own keeps its prefix, e.g. x:Timeout - each one a chip, typed and added with Enter, removed with its cross.',
    arrival_overdue: 'How many arrival windows may pass without a file before an alert.',
    test_transfers: 'Whether periodic test transfers run against each connection.',
    overdue_multiplier: 'How many intervals late a job may run before an alert.',
    start_delay: 'How many milliseconds late a job may start before an alert.',
    certificate_warning: 'How many days before expiry a certificate raises an alert.',
    outstanding_backlog: 'How many outstanding messages raise an alert.',
    feed_silence: 'How many seconds of silence from a feed raise an alert.',
    use_llm: 'Whether the LLM explains every alert raised for this type.',
    slack_webhook: 'The Slack webhook alerts are posted to when a rule names none of its own.',
    teams_webhook: 'The Microsoft Teams webhook alerts are posted to when a rule names none of its own.',
    webhook_url: 'The webhook alerts are posted to as JSON - Jira and other workflow backends read it.',
    email_connection: 'The name of the email connection alert emails go out through.',
    default_to: 'The addresses alert emails go to, separated by commas.',
    from: 'The address alert emails come from.',
    dashboard_url: 'The Dashboard address the links in alerts point to.',
    llm_connection: 'The name of the LLM connection that explains alerts when an object names none of its own.'
};

// One row per rule type, in the order they are rendered, each naming
// the fields its popover edits
config.types = {
    rest: {title: 'REST outgoing', fields: ['consecutive_failures', 'error_rate', 'window', 'status_codes', 'max_latency', 'use_llm']},
    soap: {title: 'SOAP outgoing', fields: ['consecutive_failures', 'error_rate', 'window', 'status_codes', 'fault_codes', 'max_latency', 'use_llm']},
    sql: {title: 'SQL', fields: ['consecutive_failures', 'error_rate', 'window', 'max_query_time', 'use_llm']},
    llm: {title: 'LLM', fields: ['consecutive_failures', 'error_rate', 'window', 'status_codes', 'truncations', 'refusals', 'token_budget', 'warning_latency', 'error_latency', 'use_llm']},
    mcp: {title: 'MCP', fields: ['consecutive_failures', 'error_rate', 'window', 'invalid_calls', 'rejections', 'auth_failures', 'throttled_calls', 'repeat_calls', 'warning_latency', 'error_latency', 'truncations', 'volume_budget', 'max_tools', 'use_llm']},
    microsoft: {title: 'Microsoft cloud', fields: ['consecutive_failures', 'error_rate', 'window', 'health_alerts', 'max_call_time', 'use_llm']},
    email: {title: 'Email', fields: ['consecutive_failures', 'error_rate', 'window', 'auth_failures', 'use_llm']},
    odoo: {title: 'Odoo', fields: ['consecutive_failures', 'error_rate', 'window', 'auth_failures', 'max_call_time', 'use_llm']},
    file_transfer: {title: 'File transfer', fields: ['consecutive_failures', 'warning_failures', 'error_failures', 'window', 'test_transfers', 'use_llm', 'arrival_overdue']},
    scheduler: {title: 'Scheduler', fields: ['error_rate', 'window', 'overdue_multiplier', 'start_delay', 'use_llm']},
    channels: {title: 'Channels', fields: ['error_rate', 'window']},
    common: {title: 'Common', fields: ['certificate_warning', 'outstanding_backlog', 'feed_silence']}
};

// The notifications row's own fields - where alerts go when a rule
// does not name a target of its own
config.notificationFields = [
    'slack_webhook', 'teams_webhook', 'webhook_url', 'email_connection', 'default_to', 'from', 'dashboard_url',
    'llm_connection'
];

// What each type's rules watch, shown at the type's own row header
config.typeHelp = {
    rest: 'Alert rules for REST outgoing connections - failures in a row, error rates, status codes and slow calls.',
    soap: 'Alert rules for SOAP outgoing connections - failures in a row, error rates, status codes, SOAP faults and slow calls.',
    sql: 'Alert rules for SQL connection pools - failures in a row, error rates and slow queries.',
    llm: 'Alert rules for LLM connections - failures in a row, error rates, status codes, truncated completions, refusals, the token budget and slow completions.',
    mcp: 'Alert rules for MCP gateways - failures in a row, error rates, invalid tool calls, rejected responses, rejected and throttled callers, repeated calls, slow tool calls, truncated responses, the response volume and the tool count.',
    microsoft: 'Alert rules for Microsoft cloud connections - failures in a row, error rates, service health and slow calls.',
    email: 'Alert rules for SMTP and IMAP connections - failures in a row, error rates and authentication failures.',
    odoo: 'Alert rules for Odoo connections - failures in a row, error rates, authentication failures and slow calls.',
    file_transfer: 'Alert rules for SMB and SFTP connections - failures in a row, failures over time and periodic test transfers.',
    scheduler: 'Alert rules for scheduler jobs - error rates over time, overdue runs and late starts.',
    channels: 'Alert rules for channels of every kind - the share of failed requests over time.',
    common: 'Alert rules that watch the environment as a whole - expiring certificates, backlogs and silent feeds.',
    notifications: 'Where alerts go by default - the webhooks, the email connection and its addressing, and the Dashboard address the links point to. A rule naming its own target overrides these.'
};

// ////////////////////////////////////////////////////////////////////////

// The hidden checkbox holding whether a type is active
screen.field = function(setName) {
    var out = $('#' + config.fieldIdPrefix + setName);
    return out;
};

// The row of a type
screen.card = function(setName) {
    var out = document.getElementById(config.cardIdPrefix + setName);
    return out;
};

// The type a row stands for, read off its id
screen.setNameOf = function(cardElem) {
    var out = cardElem.id.replace(config.cardIdPrefix, '');
    return out;
};

// ////////////////////////////////////////////////////////////////////////

// One micro-form descriptor per type, built from the same field list its row shows,
// and the notifications row's own - the same popover, all text fields
screen.descriptors = function() {

    var out = {};

    $.each(config.types, function(typeName, typeConfig) {

        var entries = [];
        var popupWidth = config.popupWidth;

        $.each(typeConfig.fields, function(_ignored, fieldName) {
            var fieldConfig = config.fields[fieldName];

            // A duration is edited as a count with the unit select right after it, an amount and a size the same way
            // only their counts take a fraction, and seconds are a fractional number alone
            if(fieldConfig.kind === 'duration') {
                entries.push({field: fieldName, label: fieldConfig.label, kind: 'number', unitField: screen.unitFieldName(fieldName)});
            }
            else if(fieldConfig.kind === 'amount' || fieldConfig.kind === 'size') {
                entries.push({field: fieldName, label: fieldConfig.label, kind: 'number', unitField: screen.unitFieldName(fieldName),
                    fractional: true, step: config.fractionalStep});
            }
            else if(fieldConfig.kind === 'seconds') {
                entries.push({field: fieldName, label: fieldConfig.label, kind: 'number', fractional: true, step: config.fractionalStep});
            }
            else {
                entries.push({field: fieldName, label: fieldConfig.label, kind: fieldConfig.kind});
            }

            // A popover with chips is the wider one
            if(fieldConfig.kind === $.fn.zato.micro_forms.chipsKind) {
                popupWidth = config.chipsPopupWidth;
            }
        });

        out[typeName] = {title: typeConfig.title, width: popupWidth, pages: [entries]};
    });

    var notificationEntries = [];

    $.each(config.notificationFields, function(_ignored, fieldName) {
        var fieldConfig = config.fields[fieldName];
        notificationEntries.push({field: fieldName, label: fieldConfig.label, kind: fieldConfig.kind});
    });

    out[config.notificationsName] = {title: 'Notifications', width: config.popupWidth, pages: [notificationEntries]};

    return out;
};

// ////////////////////////////////////////////////////////////////////////

})(jQuery);
